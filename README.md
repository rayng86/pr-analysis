## PR Analysis

### Prerequisites
Make sure you have python 3.9.0+ installed on your machine.
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### How to run
1. Clone the repository.
2. Go into `pr-analysis` directory.
3. Rename `.env.sample` file to `.env`.
4. Go to github or your github enterprise hosted website and head to settings page. Generate a personal access token. For more information, see https://docs.github.com/en/graphql/guides/using-the-explorer.
5. Paste the personal access token into the `.env` file under `ACCESS_TOKEN`. Save file.
6. Be sure to update the graphql github api base url if necessary.
7. Update the `REPO_OWNER` and `REPO_NAME` in the .env file and make sure that it is correct.
8. To execute, run `python pr-analysis.py`
