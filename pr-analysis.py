import os
import traceback
import requests
import pandas as pd
import datetime
from alive_progress import alive_bar
from dotenv import load_dotenv
load_dotenv()

from constants import EXPORT_FILE_TYPE, MAX_PAGE_COUNT_LIMIT, PULL_REQUEST_STATE, ExportTypeOptions

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')

pr_labels = []

if PULL_REQUEST_STATE is not None:
  pr_state_query = f'states: {PULL_REQUEST_STATE.value}, '
else:
  pr_state_query = ''

if pr_labels:
    labels_filter_query = 'labels: ['
    for i, label in enumerate(pr_labels):
        if i > 0:
            labels_filter_query += ', '
        labels_filter_query += f'"{label}"'
    labels_filter_query += '],'
else:
    labels_filter_query = ''

all_pr_data = []
end_cursor = None
page_count = 0

with alive_bar(None, title='Processing pages...') as bar:
  while True:
    after_query = f', after: "{end_cursor}"' if end_cursor else ""
    query = f'''
    query {{
      repository(owner: \"{repo_owner}\", name: \"{repo_name}\") {{
        pullRequests({pr_state_query}first: 100{after_query}, {labels_filter_query} orderBy: {{ field: CREATED_AT, direction: DESC }}) {{
          pageInfo {{
            endCursor
            hasNextPage
          }}
          nodes {{
            number
            title
            state
            author {{
              login
            }}
            createdAt
            closedAt
            changedFiles
            timelineItems(itemTypes: [REVIEW_REQUESTED_EVENT], first: 100) {{
              totalCount
            }}
            approvedReviews: reviews(first: 100, states: APPROVED) {{
              edges {{
                node {{
                  author {{
                    login
                  }}
                }}
              }}
            }}
            allReviews: reviews(first: 100) {{
              edges {{
                node {{
                  author {{
                    login
                  }}
                }}
              }}
            }}
            mergedBy {{
              login
            }}
          }}
        }}
      }}
    }}
    '''

    headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json'
    }

    response = requests.post(github_graphql_api_url, headers=headers, json={'query': query})

    try:
        data = response.json()['data']['repository']['pullRequests']['nodes']
        all_pr_data.extend(data)

    except KeyError as e:
        print(f'Error: Something went terribly wrong! Reason: {e}')
        traceback.print_exc()

    page_count += 1
    if page_count >= MAX_PAGE_COUNT_LIMIT:
        break

    if response.json()['data']['repository']['pullRequests']['pageInfo']['hasNextPage']:
        end_cursor = response.json()['data']['repository']['pullRequests']['pageInfo']['endCursor']
    else:
        break
    bar()

if response.json()['data']['repository']['pullRequests']['pageInfo']['hasNextPage']:
    end_cursor = response.json()['data']['repository']['pullRequests']['pageInfo']['endCursor']

df = pd.json_normalize(all_pr_data)

df = df.rename(columns={
  'number': 'PR #',
  'title': 'Title',
  'state': 'State',
  'author.login': 'Code Author',
  'createdAt': 'Created At',
  'closedAt': 'Closed At',
  'allReviews.edges': 'Code Reviewers',
  'approvedReviews.edges': 'Approved By',
  'changedFiles': 'File Changes',
  'timelineItems.totalCount': '# Of Review Requests'
})

df = df.rename(columns={'mergedBy.login': 'Merged By'}).drop(columns=['mergedBy'])

# The following formats the "Created At" and "Closed At" columns to be human friendly
formatted_date_string = '%Y-%m-%d %H:%M:%S'
df['Created At'] = pd.to_datetime(df['Created At']).dt.strftime(formatted_date_string)
df['Closed At'] = pd.to_datetime(df['Closed At']).dt.strftime(formatted_date_string)

columns = df.columns.tolist()
# This will get list of unique code reviewers who participated in the pull request
code_reviewers = [', '.join(list(set([edge['node']['author']['login'] for edge in pr['allReviews']['edges']]))) if pr['allReviews']['edges'] else '' for pr in all_pr_data]
df['Code Reviewers'] = code_reviewers

approved_by_reviewers = [', '.join(list(set([edge['node']['author']['login'] for edge in pr['approvedReviews']['edges']]))) if pr['approvedReviews']['edges'] else '' for pr in all_pr_data]
df['Approved By'] = approved_by_reviewers

merge_times = []
for pr in all_pr_data:
    created_at = pd.to_datetime(pr['createdAt'])
    closed_at = pd.to_datetime(pr['closedAt'])
    if closed_at is not None:
      merge_time = closed_at - created_at
      merge_time_days = merge_time.days
      if merge_time_days == 0:
          merge_times.append('same day')
      else:
          merge_time_str = f"{merge_time_days} day"
          if merge_time_days > 1:
              merge_time_str += "s"
          merge_times.append(merge_time_str)
    else:
      merge_times.append('')
df['Merge Time (Days)'] = merge_times

columns.append('Merge Time (Days)')

if EXPORT_FILE_TYPE == ExportTypeOptions.MARKDOWN.value:
  table_results = df[columns].to_markdown(index=False)
elif EXPORT_FILE_TYPE == ExportTypeOptions.CSV.value:
  table_results = df[columns].to_csv(index=False)
elif EXPORT_FILE_TYPE == ExportTypeOptions.HTML.value:
  table_results = df[columns].to_html(index=False).replace('class="dataframe"', 'class="dataframe" style="font-family: sans-serif;"')
else:
  pass

report_page_date_str = datetime.datetime.now().strftime(formatted_date_string)
report_page = f"Report generated on {report_page_date_str}\n\n{table_results}"

# Create the generated-reports directory if it doesn't exist already
current_dir = os.getcwd()
generated_reports_dir = os.path.join(current_dir, 'generated-reports')
if not os.path.exists(generated_reports_dir):
    os.makedirs(generated_reports_dir)

report_filename_date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f'pr-analysis-generated-report-{repo_owner}-{repo_name}-{report_filename_date_str}'
if PULL_REQUEST_STATE is not None:
  file_name += f'-{PULL_REQUEST_STATE.value}'
file_name += f'.{EXPORT_FILE_TYPE}'
output_file_path = os.path.join(generated_reports_dir, file_name)

with open(output_file_path, 'w') as f:
    f.write(report_page)
