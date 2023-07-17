import os
from dotenv import load_dotenv
load_dotenv()

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
query = '''
query {
  repository(owner: \"rayng86\", name: \"ray_test_repo\") {
    pullRequests(states: MERGED, first: 50, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        author {
          login
        }
      }
    }
  }
}
'''

headers = {
  'Authorization': f'Bearer {access_token}',
  'Content-Type': 'application/json'
}

