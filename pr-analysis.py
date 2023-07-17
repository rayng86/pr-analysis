import os
import requests
import pandas as pd
import datetime
from dotenv import load_dotenv
load_dotenv()

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')

query = f'''
query {{
  repository(owner: \"{repo_owner}\", name: \"{repo_name}\") {{
    pullRequests(states: MERGED, first: 50, orderBy: {{ field: UPDATED_AT, direction: DESC }}) {{
      nodes {{
        number
        title
        author {{
          login
        }}
        createdAt
        closedAt
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
      'author.login': 'Author',
      'createdAt': 'Created At',
      'closedAt': 'Closed At',
      'reviews.edges': 'Code Reviewers',
      'mergedBy.login': 'Merged By'
    })

    # The following formats the "Created At" and "Closed At" columns to be human friendly
    formatted_date_string = '%Y-%m-%d %H:%M:%S'
    df['Created At'] = pd.to_datetime(df['Created At']).dt.strftime(formatted_date_string)
    df['Closed At'] = pd.to_datetime(df['Closed At']).dt.strftime(formatted_date_string)

    columns = df.columns.tolist()
    # This will get list of unique code reviewers who participated in the pull request
    code_reviewers = [', '.join(list(set([edge['node']['author']['login'] for edge in pr['reviews']['edges']]))) if pr['reviews']['edges'] else '' for pr in data]
    df['Code Reviewers'] = code_reviewers

    table_results = df[columns].to_markdown(index=False)

    report_date_str = datetime.datetime.now().strftime(formatted_date_string)
    report_page = f"Report generated on {report_date_str}\n\n{table_results}"

    with open('pr-analysis-generated-report-{report_date_str}.md', 'w') as f:
        f.write(report_page)
except KeyError:
    print('Error: Something went terribly wrong!')
