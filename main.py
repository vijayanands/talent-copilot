import os

from dotenv import load_dotenv

from functions.llamaindex.appraisal import create_html_document, generate_self_appraisal
from helpers.github import (
    fetch_issues_data,
    fetch_PR_data,
    get_commits_per_user_in_repo,
    get_pull_requests_by_author,
    list_repo_activity,
    list_repo_contributors,
)

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

    author = input("Enter the username for which you want to generate apprailsals: ")
    # OpenAI
    appraisal_openai = generate_self_appraisal(
        author, "openai", model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")
    )

    # Anthropic
    appraisal_anthropic = generate_self_appraisal(
        author, "anthropic", model="claude-2", api_key=os.getenv("ANTHROPIC_API_KEY")
    )

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
