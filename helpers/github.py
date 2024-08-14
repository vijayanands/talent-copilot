import json
import logging
import os
import sys
import time
from collections import defaultdict
from typing import Any, Dict
from dotenv import load_dotenv
from constants import user_to_external_users

load_dotenv()

github_repo = "Hello-World"
github_owner = "octocat"

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


import requests

headers = {
    "Authorization": f"token {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json",
}


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

    commits_per_user = defaultdict(dict)

    for commit in commits:
        author = commit["author"]["login"]
        commits_per_user[author]["login"] = author
        commits_per_user[author].setdefault("commits", []).append(
            f"https://github.com/{author}/{repo}/commits/{commit['sha']}"
        )
        commits_per_user[author]["total_commits"] = (
            commits_per_user[author].setdefault("total_commits", 0) + 1
        )
        commits_per_user[author]["comment_count"] = commit["commit"]["comment_count"]
        commits_per_user[author]["message"] = commit["commit"]["message"]

    return commits_per_user


def get_commits_per_user_in_repo(owner, repo):
    logging.info(f"Analyzing repository: {owner}/{repo}")
    client = GitHubAPIClient()

    try:
        commits_per_user = analyze_commits_per_user(client, owner, repo)

        # Print the results to the console as well
        print("\nCommits per user:")
        for commit_info in commits_per_user.items():
            print(json.dumps(commit_info))

        # Return the commits_per_user dictionary
        return commits_per_user

    except Exception as e:
        logging.exception("An error occurred during analysis")
        print(f"An error occurred during analysis: {str(e)}")
        print("Please check your token, owner, and repo name, and try again.")
        return None  # Return None in case of an error


def get_github_contributions_by_author(author):
    # Get a list of external user ids mapped to the author
    external_usernames = user_to_external_users[author]

    if not external_usernames:
        logging.warning(f"No external usernames found for author: {author}")
        return None

    # Get commits per user in the repository
    github_data = get_commits_per_user_in_repo(github_owner, github_repo)

    if not github_data:
        logging.warning("No GitHub data retrieved")
        return None

    # Sum up the total commits for all external usernames
    commit_info_list = []
    total_commits = 0
    for username in external_usernames:
        commit_info = github_data.get(username)
        if not commit_info:
            logging.warning(f"No commit info found for external username: {username}")
            continue
        total_commits += commit_info.get("total_commits")
        commit_info_list.append(commit_info)

    return {
        "author": author,
        "total_commits": total_commits,
        "commit_info_list": commit_info_list,
    }
