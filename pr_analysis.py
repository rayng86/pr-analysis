import os
import traceback
import requests
import pandas as pd
import datetime
from alive_progress import alive_bar
from dotenv import load_dotenv
load_dotenv()

from constants import EXPORT_FILE_TYPE, MAX_PAGE_COUNT_LIMIT, MERGE_TIME_FORMAT, PULL_REQUEST_STATE, ExportTypeOptions, MergeTimeFormat, PullRequestState

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')

pr_labels = []

def create_labels_filter_query(pr_labels):
    if pr_labels:
        labels_filter_query = 'labels: ['
        for i, label in enumerate(pr_labels):
            if i > 0:
                labels_filter_query += ', '
            labels_filter_query += f'"{label}"'
        labels_filter_query += '],'
    else:
        labels_filter_query = ''
    return labels_filter_query

if PULL_REQUEST_STATE is not None:
  pr_state_query = f'states: {PULL_REQUEST_STATE}, '
else:
  pr_state_query = ''


all_pr_data = []
end_cursor = None
page_count = 0

with alive_bar(None, title='Processing pages...') as bar:
  while True:
    after_query = f', after: "{end_cursor}"' if end_cursor else ""
    query = f'''
    query {{
      repository(owner: \"{repo_owner}\", name: \"{repo_name}\") {{
        pullRequests({pr_state_query}first: 100{after_query}, {create_labels_filter_query(pr_labels)} orderBy: {{ field: CREATED_AT, direction: DESC }}) {{
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

def get_unique_sorted_users(data: any, key: str) -> list:
  '''
  Returns a list of unique sorted github users from the given pull request data
  '''
  return [', '.join(sorted(list(set([edge['node']['author']['login'] for edge in pr[key]['edges']])))) if pr[key]['edges'] else '' for pr in data]

code_reviewers = get_unique_sorted_users(all_pr_data, 'allReviews')
df['Code Reviewers'] = code_reviewers

approved_by_reviewers = get_unique_sorted_users(all_pr_data, 'approvedReviews')
df['Approved By'] = approved_by_reviewers

def format_merge_time(merge_time):
    merge_time_str = ""
    if MERGE_TIME_FORMAT == MergeTimeFormat.DAYS:
        merge_time_days = merge_time.days
        if merge_time_days == 0:
            merge_time_str = 'same day'
        else:
            merge_time_str = f"{merge_time_days} day"
            if merge_time_days > 1:
                merge_time_str += "s"
    elif MERGE_TIME_FORMAT == MergeTimeFormat.HOURS:
        total_seconds = merge_time.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            merge_time_str += f"{int(days)}d "
        if hours > 0:
            merge_time_str += f"{int(hours)}h "
        if minutes > 0:
            merge_time_str += f"{int(minutes)}m "
        if total_seconds < 60:
            merge_time_str += f"{int(total_seconds)}s "
    return merge_time_str.strip()

def calculate_merge_times(data: any) -> list:
    merge_times = []
    for pr in data:
        if pr['state'] == PullRequestState.MERGED.value:
            created_at = pd.to_datetime(pr['createdAt'])
            closed_at = pd.to_datetime(pr['closedAt'])
            if pd.notnull(closed_at):
                merge_time = closed_at - created_at
                merge_times.append(format_merge_time(merge_time))
            else:
                merge_times.append('')
        else:
            merge_times.append('')
    return merge_times

df['Merge Time (Days)'] = calculate_merge_times(all_pr_data)
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
  file_name += f'-{PULL_REQUEST_STATE}'
file_name += f'.{EXPORT_FILE_TYPE}'
output_file_path = os.path.join(generated_reports_dir, file_name)

with open(output_file_path, 'w') as f:
    f.write(report_page)
