import os
from dotenv import load_dotenv
load_dotenv()

github_graphql_api_url = os.getenv('GITHUB_GRAPHQL_API_URL')
access_token = os.getenv('ACCESS_TOKEN')
