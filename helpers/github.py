import json
import logging
import os
import sys
import time
from collections import defaultdict
from typing import Any, Dict

from dotenv import load_dotenv
from user_mapping import get_mapped_user

from tmp_inputs import github_owner, github_repo

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


import requests

headers = {
    "Authorization": f"token {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json",
}


class GitHubAPIClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = headers

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
        return response.json()["default_branch"]

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
        author = commit["commit"]["author"]["name"]
        commits_per_user[author] += 1

    return dict(commits_per_user)


def get_commits_per_user_in_repo(owner, repo):
    logging.info(f"Analyzing repository: {owner}/{repo}")
    client = GitHubAPIClient()

    try:
        commits_per_user = analyze_commits_per_user(client, owner, repo)

        output_file = "commits_per_user.json"
        logging.info(f"Saving analysis results to {output_file}")
        with open(output_file, "w") as f:
            json.dump(commits_per_user, f, indent=2)

        print(f"Analysis complete. Results saved to '{output_file}'.")

        # Print the results to the console as well
        print("\nCommits per user:")
        for user, count in sorted(
            commits_per_user.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"{user}: {count}")

    except Exception as e:
        logging.exception("An error occurred during analysis")
        print(f"An error occurred during analysis: {str(e)}")
        print("Please check your token, owner, and repo name, and try again.")


def fetch_PR_data(owner: str, repo: str) -> Any:
    logging.info(f"Fetching pull requests for {owner}/{repo}")

    state = "all"
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params: Dict[str, Any] = {"state": state, "per_page": 100}
    all_prs = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch PRs: {response.status_code}, {response.text}"
            )

        prs = response.json()
        all_prs.extend(prs)

        # Check for pagination
        url = response.links.get("next", {}).get("url")

        # Respect rate limits
        time.sleep(1)

    print(f"Fetched {len(all_prs)} pull requests")
    return all_prs


def fetch_PR_comments(owner: str, repo: str) -> Any:
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    url = f"{base_url}/pulls/comments"
    params: Dict[str, Any] = {"per_page": 100}
    all_comments = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch Comments: {response.status_code}, {response.text}"
            )

        comments = response.json()
        all_comments.extend(comments)

        # Check for pagination
        url = response.links.get("next", {}).get("url")

        # Respect rate limits
        time.sleep(1)

    print(f"Fetched {len(all_comments)} comments")
    return all_comments


def get_pull_requests_by_author(owner: str, repo: str, author: str) -> Any:
    prs: Any = fetch_PR_data(owner, repo)

    prs_by_author = [pr for pr in prs if pr["user"]["login"].lower() == author.lower()]

    print(f"Found {len(prs_by_author)} pull requests by {author}")
    return prs_by_author


def list_repo_activity(owner: str, repo: str) -> Any:
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    url = f"{base_url}/activity"
    params: Dict[str, Any] = {"per_page": 100}
    all_activity = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch Activities: {response.status_code}, {response.text}"
            )

        activities = response.json()
        all_activity.extend(activities)

        # Check for pagination
        url = response.links.get("next", {}).get("url")

        # Respect rate limits
        time.sleep(1)

    print(f"Fetched {len(all_activity)} repository activities")
    return all_activity


def list_repo_contributors(owner: str, repo: str) -> Any:
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    url = f"{base_url}/contributors"
    params: Dict[str, Any] = {"per_page": 100}
    all_contributors = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch Contributors: {response.status_code}, {response.text}"
            )

        contributors = response.json()
        all_contributors.extend(contributors)

        # Check for pagination
        url = response.links.get("next", {}).get("url")

        # Respect rate limits
        time.sleep(1)

    print(f"Fetched {len(all_contributors)} contributors")
    return all_contributors


def fetch_issues_data(owner: str, repo: str) -> Any:
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    url = f"{base_url}/issues"
    params: Dict[str, Any] = {"state": "all", "per_page": 100}
    all_issues = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch PRs: {response.status_code}, {response.text}"
            )

        issues = response.json()
        all_issues.extend(issues)

        # Check for pagination
        url = response.links.get("next", {}).get("url")

        # Respect rate limits
        time.sleep(1)

    print(f"Fetched {len(all_issues)} issues")
    return all_issues


def map_github_users(github_data: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    mapped_github_activities = {}

    for username, count in github_data.items():
        mapped_user = get_mapped_user(username)
        if mapped_user:
            mapped_github_activities[mapped_user["email"]] = {
                "github_commits": count,
                "user_info": mapped_user,
            }

    return mapped_github_activities


def get_github_contributions_by_author(author):
    github_data = get_commits_per_user_in_repo(github_owner, github_repo)
    mapped_github_data = map_github_users(github_data)
    return mapped_github_data
