import json
import logging
from collections import defaultdict
from typing import Any
from constants import user_to_external_users
from helpers.github_client import GitHubAPIClient

github_repo = "Hello-World"
github_owner = "octocat"

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def _analyze_commits_per_user(client, owner, repo):
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


def _get_commits_per_user_in_repo(owner, repo):
    logging.info(f"Analyzing repository: {owner}/{repo}")
    client = GitHubAPIClient()

    try:
        commits_per_user = _analyze_commits_per_user(client, owner, repo)

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
    github_data = _get_commits_per_user_in_repo(github_owner, github_repo)

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

def extract_comment_info(pr_comments):
    comments = []
    for comment in pr_comments:
        comments.append({
            "author": comment["user"]["login"],
            "comment_id": comment["id"],
            "comment_url": comment["html_url"],
            "comment_body": comment["body"],
            "created_at": comment["created_at"],
            "updated_at": comment["updated_at"],
        })
    return comments

def extract_pr_info(pr, owner: str, repo: str) -> dict:
    # comments = _get_pull_request_comments_by_author(owner, repo, pr["number"])
    client = GitHubAPIClient()
    pr_comments = client.fetch_PR_comments(owner, repo, pr["number"])

    return {
        "number": pr["number"],
        "pr_title": pr["title"],
        "pr_url": pr["html_url"],
        "author": pr["user"]["login"],
        "assignee": pr["assignee"],
        "assignees": pr["assignees"],
        "body": pr["body"],
        "created_at": pr["created_at"],
        "closed_at": pr["closed_at"],
        "merged_at": pr["merged_at"],
        "labels": pr["labels"],
        "milestone": pr["milestone"],
        "comments": extract_comment_info(pr_comments) if pr_comments else [],
    }

def get_all_pull_requests_data(owner: str, repo: str) -> Any:
    client = GitHubAPIClient()
    raw_prs: Any = client.fetch_PR_data(owner, repo)
    prs = [extract_pr_info(pr, owner, repo) for pr in raw_prs]

    print(f"Found {len(prs)} pull requests in {owner}/{repo}")
    return prs

def get_pull_requests_by_author(owner: str, repo: str, author: str) -> Any:
    client = GitHubAPIClient()
    raw_prs: Any = client.fetch_PR_data(owner, repo)

    raw_prs_by_author = [pr for pr in raw_prs if pr["user"]["login"].lower() == author.lower()]
    prs_by_author = [extract_pr_info(pr, owner, repo) for pr in raw_prs_by_author]
    print(f"Found {len(prs_by_author)} pull requests by {author}")
    return prs_by_author


if __name__ == "__main__":
    prs = get_all_pull_requests_data(github_owner, github_repo)
    print(f"\nAll pull requests in {github_owner}/{github_repo}:")
    print(json.dumps(prs, indent=2))

    author = "vijayanands@gmail.com"
    prs_by_author = get_pull_requests_by_author(github_owner, github_repo, author)
    print(f"\nPull requests by {author}:")
    print(json.dumps(prs_by_author, indent=2))

    contributions_by_author = get_github_contributions_by_author(author)
    print(f"\nGitHub contributions by {author}:")
    print(json.dumps(contributions_by_author, indent=2))
