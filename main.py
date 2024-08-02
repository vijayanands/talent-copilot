import os

from dotenv import load_dotenv

from helpers.github import (
    fetch_issues_data,
    fetch_PR_data,
    get_pull_requests_by_author,
    list_repo_activity,
    list_repo_contributors,
)
from helpers.github import get_commits_per_user_in_repo
from functions.llamaindex.appraisal import generate_self_appraisal, create_html_document


load_dotenv()


def main():
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
    author = input("Enter the username for which you want to generate apprailsals: ")
    # fetch_PR_data(repo_owner, repo_name)
    # fetch_issues_data(repo_owner, repo_name)
    # list_repo_activity(repo_owner, repo_name)
    # list_repo_contributors(repo_owner, repo_name)
    # get_pull_request_info(username, repo_owner, repo_name)
    # get_pull_requests_by_author(repo_owner, repo_name)
    # get_pull_request_by_author(username, repo_owner, repo_name)
    # get_commits_per_user_in_repo(owner, repo)

    # author = "John Doe"  # Replace with the actual author name

    # Example usage for different LLMs
    # OpenAI
    appraisal_openai = generate_self_appraisal(author, "openai", model="gpt-3.5-turbo")

    # Anthropic
    appraisal_anthropic = generate_self_appraisal(author, "anthropic", model="claude-2")

    # Create and save HTML documents for each appraisal
    for vendor, appraisal in [
        ("openai", appraisal_openai),
        ("anthropic", appraisal_anthropic),
    ]:
        html_document = create_html_document(appraisal)
        with open(f"self_appraisal_{vendor}.html", "w") as f:
            f.write(html_document)
        print(
            f"Self-appraisal generated using {vendor.capitalize()} and saved as 'self_appraisal_{vendor}.html'"
        )


if __name__ == "__main__":
    main()
