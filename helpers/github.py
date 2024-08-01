import os
import time
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

import requests

headers = {
    "Authorization": f"token {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_PR_data(owner: str, repo: str) -> Any:
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
    prs:Any = fetch_PR_data(owner, repo)

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
