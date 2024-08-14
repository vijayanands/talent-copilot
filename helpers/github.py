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


def get_pull_requests_by_author(owner: str, repo: str, author: str) -> Any:
    client = GitHubAPIClient()
    prs: Any = client.fetch_PR_data(owner, repo)

    prs_by_author = [pr for pr in prs if pr["user"]["login"].lower() == author.lower()]

    print(f"Found {len(prs_by_author)} pull requests by {author}")
    return prs_by_author


def get_pull_request_comments_by_author(owner: str, repo: str, author: str):
    client = GitHubAPIClient()
    pr_comments = client.fetch_PR_comments(owner, repo)
    # todo: filter comments by author and return them as a list of dictionaries with 'author', 'comment_'
    return pr_comments
