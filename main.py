import os
import sys
import argparse

from dotenv import load_dotenv

from functions.llamaindex.appraisal import (
    generate_self_appraisal,
    save_appraisal_to_json
)
from functions.llamaindex.generate_appraisal_docs import generate_appraisal_docs
from helpers.github import (
    list_repo_contributors,
)
from user_mapping import (
    map_user,
    create_or_get_unique_users,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def get_unique_user_emails():
    return create_or_get_unique_users()

def prompt_for_author(unique_user_emails):
    choices = ", ".join(unique_user_emails)
    while True:
        author = input(f"Enter the unique user email for generating appraisals ({choices}): ")
        if author in unique_user_emails:
            return author
        print("Invalid email. Please try again.")

def prompt_for_vendor():
    while True:
        vendor = input("Choose the AI model vendor to use (openai, anthropic): ").lower()
        if vendor in ["openai", "anthropic"]:
            return vendor
        print("Invalid vendor. Please choose either 'openai' or 'anthropic'.")


def main():
    unique_user_emails = get_unique_user_emails()

    parser = argparse.ArgumentParser(description="Generate self-appraisals using AI models.")
    parser.add_argument(
        "author",
        type=str,
        nargs='?',
        help="The unique user email for generating appraisals. Choose from: " + ", ".join(unique_user_emails)
    )
    parser.add_argument(
        "vendor",
        type=str,
        nargs='?',
        choices=["openai", "anthropic"],
        help="The AI model vendor to use (openai or anthropic)"
    )

    args = parser.parse_args()

    if args.author is None:
        args.author = prompt_for_author(unique_user_emails)
    elif args.author not in unique_user_emails:
        parser.error(f"Invalid author email. Please choose from: {', '.join(unique_user_emails)}")

    if args.vendor is None:
        args.vendor = prompt_for_vendor()

    contributors = list_repo_contributors(owner="octocat", repo="Hello-World")
    print(contributors)

    external_usernames = {contributor["login"] for contributor in contributors}
    for username in external_usernames:
        map_user(username, unique_user_emails)

    # Generate appraisal based on the chosen vendor
    if args.vendor == 'openai':
        appraisal = generate_self_appraisal(
            args.author, "openai", model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")
        )
    else:  # anthropic
        appraisal = generate_self_appraisal(
            args.author, "anthropic", model="claude-2.1", api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    # Save appraisal to JSON
    print(appraisal)
    json_file_name = f"/tmp/self_appraisal_{args.author}_{args.vendor}.json"
    save_appraisal_to_json(appraisal, json_file_name)
    print(f"Appraisal saved as JSON: {json_file_name}")

    # Generate HTML and PDF documents
    generate_appraisal_docs(json_file_name)

if __name__ == "__main__":
    main()
