from helpers.github import (
    fetch_PR_data,
    fetch_issues_data,
    list_repo_activity,
    list_repo_contributors,
    get_pull_requests_by_author,
)
import os
from dotenv import load_dotenv

load_dotenv()

# Press the green button in the gutter to run the script.
if __name__ == "__main__":

    # initialize
    # initialize()

    username = "octocat"
    repo_name = "Hello-World"
    repo_owner = "octocat"
    # username = "michael-s-molina"
    # repo_owner = "apache"
    # repo_name = "superset"
    # fetch_PR_data(repo_owner, repo_name, os.getenv("GITHUB_TOKEN"))
    # fetch_issues_data(repo_owner, repo_name, os.getenv("GITHUB_"))
    # list_repo_activity(repo_owner, repo_name, os.getenv("GITHUB_TOKEN"))
    # list_repo_contributors(repo_owner, repo_name, os.getenv("GITHUB_TOKEN"))
    # get_pull_request_info(username, repo_owner, repo_name)
    get_pull_requests_by_author(
        repo_owner, repo_name, os.getenv("GITHUB_TOKEN"), "octocat"
    )

    # username = "betodealmeida"
    # repo_owner = "apache"
    # repo_name = "superset"
    # get_pull_request_by_author(username, repo_owner, repo_name)
