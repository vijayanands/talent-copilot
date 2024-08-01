import os

from dotenv import load_dotenv

from helpers.github import (
    fetch_issues_data,
    fetch_PR_data,
    get_pull_requests_by_author,
    list_repo_activity,
    list_repo_contributors,
)
from helpers.github_commits import get_commits_per_user_in_repo

load_dotenv()

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
 # Example Repos and Owners:
 #    username = 'octocat'
 #    repo_name = "Hello-World"
 #    repo_owner = "octocat"
 #    username = "michael-s-molina"
 #
 #    repo_owner = "apache"
 #    repo_name = "superset"
 #    username = "betodealmeida"

    owner = input("Enter the repository owner: ")
    repo = input("Enter the repository name: ")
    # fetch_PR_data(repo_owner, repo_name)
    # fetch_issues_data(repo_owner, repo_name)
    # list_repo_activity(repo_owner, repo_name)
    # list_repo_contributors(repo_owner, repo_name)
    # get_pull_request_info(username, repo_owner, repo_name)
    # get_pull_requests_by_author(repo_owner, repo_name)
    username = input("Enter the user in the repository: ")
    # get_pull_request_by_author(username, repo_owner, repo_name)
    get_commits_per_user_in_repo(owner, repo)
