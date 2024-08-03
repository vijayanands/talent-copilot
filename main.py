import os
import sys

from dotenv import load_dotenv

from functions.llamaindex.appraisal import create_html_document, generate_self_appraisal
from helpers.confluence import get_confluence_contributions_by_author
from helpers.github import (
    fetch_issues_data,
    fetch_PR_data,
    get_commits_per_user_in_repo,
    get_pull_requests_by_author,
    list_repo_activity,
    list_repo_contributors,
)
from helpers.jira import get_jira_contributions_by_author

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()


def main():
    # Example Repos and Owners:
    #    username = 'octocat'
    #    repo_name = "Hello-World"
    #    repo_owner = "octocat"
    #    username = "michael-s-molina"ATATT3xFfGF02OUGmoPBmRXvFW_J_Pwvv0FRHscctc8Z_EBqE07xxM6FAVYxZ_558ziQt7MxEOpily2mgbAHWa9wc1lN5ZPV2-Pzoa3WCgAVQKG62OHjBjy3iKBQMkju7YzDzgltwiOIY2Ea79bzPC729bso04vhY0WDC_V1rdxpSx4gDJGIo3s=33787158
    #
    #    repo_owner = "apache"
    #    repo_name = "superset"
    #    username = "betodealmeida"

    author = input("Enter the username for which you want to generate appraisals: ")
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
    # get_jira_contributions_by_author('vijayanands@gmail.com')
    get_confluence_contributions_by_author("vijayanands@gmail.com")
    # main()
