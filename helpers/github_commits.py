import os
import requests
import json
from collections import defaultdict
import sys
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubAPIClient:
    def __init__(self, token):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def api_call(self, url, params=None):
        logging.info(f"Making API call to: {url}")
        response = requests.get(url, headers=self.headers, params=params)
        logging.info(f"Response status code: {response.status_code}")
        # logging.info("Sleeping for 0.5 seconds")
        # time.sleep(0.5)
        return response

    def get_default_branch(self, owner, repo):
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.api_call(url)
        if response.status_code != 200:
            logging.error(f"Error fetching repository info: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            sys.exit(1)
        return response.json()['default_branch']

    def get_commits(self, owner, repo, branch):
        commits = []
        page = 1
        while True:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {"sha": branch, "page": page, "per_page": 100}
            response = self.api_call(url, params)
            if response.status_code != 200:
                logging.error(f"Error fetching commits: {response.status_code}")
                logging.error(f"Response content: {response.text}")
                break
            page_commits = response.json()
            if not page_commits:
                break
            commits.extend(page_commits)
            page += 1
        return commits

def analyze_commits_per_user(client, owner, repo):
    branch = client.get_default_branch(owner, repo)
    logging.info(f"Analyzing commits on the default branch: {branch}")

    commits = client.get_commits(owner, repo, branch)
    logging.info(f"Found {len(commits)} commits on the {branch} branch")

    commits_per_user = defaultdict(int)

    for commit in commits:
        author = commit['commit']['author']['name']
        commits_per_user[author] += 1

    return dict(commits_per_user)

def get_commits_per_user_in_repo(owner, repo):
    token = os.getenv("GITHUB_TOKEN")

    logging.info(f"Analyzing repository: {owner}/{repo}")
    client = GitHubAPIClient(token)

    try:
        commits_per_user = analyze_commits_per_user(client, owner, repo)

        output_file = 'commits_per_user.json'
        logging.info(f"Saving analysis results to {output_file}")
        with open(output_file, 'w') as f:
            json.dump(commits_per_user, f, indent=2)

        print(f"Analysis complete. Results saved to '{output_file}'.")

        # Print the results to the console as well
        print("\nCommits per user:")
        for user, count in sorted(commits_per_user.items(), key=lambda x: x[1], reverse=True):
            print(f"{user}: {count}")

    except Exception as e:
        logging.exception("An error occurred during analysis")
        print(f"An error occurred during analysis: {str(e)}")
        print("Please check your token, owner, and repo name, and try again.")

