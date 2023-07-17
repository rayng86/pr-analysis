import os
import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
query = '''
query {
  repository(owner: \"rayng86\", name: \"ray_test_repo\") {
    pullRequests(states: MERGED, first: 50, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        author {
          login
        }
        createdAt
        closedAt
      }
    }
  }
}
'''

headers = {
  'Authorization': f'Bearer {access_token}',
  'Content-Type': 'application/json'
}

response = requests.post(github_graphql_api_url, headers=headers, json={'query': query})

# print(response.json())
try:
    data = response.json()['data']['repository']['pullRequests']['nodes']
    df = pd.json_normalize(data)

    print(df)
except KeyError:
    print('Error: Something went terribly wrong!')
