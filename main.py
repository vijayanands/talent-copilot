import argparse
import json

from dotenv import load_dotenv

from helpers.confluence import get_confluence_contributions_by_author
from helpers.github import get_github_contributions_by_author
from helpers.jira import get_jira_contributions_by_author

debug_jira = False
debug_confluence = False
debug_github = False

from functions.llamaindex_appraisal import self_appraisal_tool
from helpers.github import list_repo_contributors
from user_mapping import create_or_get_unique_users, map_user

load_dotenv()


def get_unique_user_emails():
    return create_or_get_unique_users()


def prompt_for_author(unique_user_emails):
    choices = ", ".join(unique_user_emails)
    while True:
        author = input(
            f"Enter the unique user email for generating appraisals ({choices}): "
        )
        if author in unique_user_emails:
            return author
        print("Invalid email. Please try again.")


def prompt_for_vendor():
    while True:
        vendor = input(
            "Choose the AI model vendor to use (openai, anthropic): "
        ).lower()
        if vendor in ["openai", "anthropic"]:
            return vendor
        print("Invalid vendor. Please choose either 'openai' or 'anthropic'.")


def initialize_jira_hack(unique_user_emails):
    contributors = list_repo_contributors(owner="octocat", repo="Hello-World")
    print(contributors)

    external_usernames = {contributor["login"] for contributor in contributors}
    for username in external_usernames:
        map_user(username, unique_user_emails)


def initialize_hacks_and_get_user_inputs():
    unique_user_emails = get_unique_user_emails()

    parser = argparse.ArgumentParser(
        description="Generate self-appraisals using AI models."
    )
    parser.add_argument(
        "author",
        type=str,
        nargs="?",
        help="The unique user email for generating appraisals. Choose from: "
        + ", ".join(unique_user_emails),
    )
    parser.add_argument(
        "vendor",
        type=str,
        nargs="?",
        help="The AI model vendor to use (openai or anthropic)",
    )

    args = parser.parse_args()

    if args.author is None:
        args.author = prompt_for_author(unique_user_emails)
    elif args.author not in unique_user_emails:
        parser.error(
            f"Invalid author email. Please choose from: {', '.join(unique_user_emails)}"
        )

    if args.vendor is None:
        args.vendor = prompt_for_vendor()

    initialize_jira_hack(unique_user_emails)

    return args.vendor, args.author


def main():
    vendor, author = initialize_hacks_and_get_user_inputs()
    self_appraisal_tool(author, vendor)


if __name__ == "__main__":
    if debug_jira:
        response = get_jira_contributions_by_author("vijayanands@gmail.com")
        print(json.dumps(response, indent=4))
    elif debug_confluence:
        response = get_confluence_contributions_by_author("vijayanands@gmail.com")
        print(json.dumps(response, indent=4))
    elif debug_github:
        response = get_github_contributions_by_author("vijayanands@gmail.com")
        print(json.dumps(response, indent=4))
    else:
        main()
