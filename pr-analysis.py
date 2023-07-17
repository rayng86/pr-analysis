import os
import requests
import pandas as pd
import datetime
from dotenv import load_dotenv
load_dotenv()

from constants import ExportTypeOptions, PullRequestState

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')

pr_state = PullRequestState.MERGED

export_as_file_type = ExportTypeOptions.CSV.value

pr_labels = []

if pr_labels:
    labels_filter_query = 'labels: ['
    for i, label in enumerate(pr_labels):
        if i > 0:
            labels_filter_query += ', '
        labels_filter_query += f'"{label}"'
    labels_filter_query += '],'
else:
    labels_filter_query = ''

query = f'''
query {{
  repository(owner: \"{repo_owner}\", name: \"{repo_name}\") {{
    pullRequests(states: {pr_state.value}, first: 50, {labels_filter_query} orderBy: {{ field: UPDATED_AT, direction: DESC }}) {{
      nodes {{
        number
        title
        author {{
          login
        }}
        createdAt
        closedAt
        changedFiles,
        timelineItems(itemTypes: [REVIEW_REQUESTED_EVENT], first: 100) {{
          totalCount
        }}
        reviews(first: 100) {{
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
    df = pd.json_normalize(data)

    df = df.rename(columns={
      'number': 'PR #',
      'title': 'Title',
      'author.login': 'Code Author',
      'createdAt': 'Created At',
      'closedAt': 'Closed At',
      'reviews.edges': 'Code Reviewers',
      'mergedBy.login': 'Merged By',
      'changedFiles': 'File Changes',
      'timelineItems.totalCount': '# Of Review Requests'
    })

    # The following formats the "Created At" and "Closed At" columns to be human friendly
    formatted_date_string = '%Y-%m-%d %H:%M:%S'
    df['Created At'] = pd.to_datetime(df['Created At']).dt.strftime(formatted_date_string)
    df['Closed At'] = pd.to_datetime(df['Closed At']).dt.strftime(formatted_date_string)

    columns = df.columns.tolist()
    # This will get list of unique code reviewers who participated in the pull request
    code_reviewers = [', '.join(list(set([edge['node']['author']['login'] for edge in pr['reviews']['edges']]))) if pr['reviews']['edges'] else '' for pr in data]
    df['Code Reviewers'] = code_reviewers

    merge_times = []
    for pr in data:
        created_at = pd.to_datetime(pr['createdAt'])
        closed_at = pd.to_datetime(pr['closedAt'])
        merge_time = closed_at - created_at
        merge_time_days = merge_time.days
        if merge_time_days == 0:
            merge_times.append('same day')
        else:
            merge_time_str = f"{merge_time_days} day"
            if merge_time_days > 1:
                merge_time_str += "s"
            merge_times.append(merge_time_str)
    df['Merge Time (Days)'] = merge_times

    columns.append('Merge Time (Days)')


    if export_as_file_type == ExportTypeOptions.MARKDOWN.value:
      table_results = df[columns].to_markdown(index=False)
    elif export_as_file_type == ExportTypeOptions.CSV.value:
      table_results = df[columns].to_csv(index=False)
    elif export_as_file_type == ExportTypeOptions.HTML.value:
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
    file_name = f'pr-analysis-generated-report-{report_filename_date_str}.{export_as_file_type}'
    output_file_path = os.path.join(generated_reports_dir, file_name)

    with open(output_file_path, 'w') as f:
        f.write(report_page)
except KeyError:
    print('Error: Something went terribly wrong!')
