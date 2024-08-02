import sqlite3
from typing import Dict, Any
from jira import count_resolved_issues_by_assignee
from github import get_commits_per_user_in_repo
from confluence import get_confluence_contributions


def get_mapped_user_info(external_username: str) -> Dict[str, Any]:
    conn = sqlite3.connect("user_mapping.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT u.email, u.firstname, u.lastname, u.address, u.phone_number
        FROM user_mapping m
        JOIN unique_users u ON m.unique_user_email = u.email
        WHERE m.external_username = ?
    """,
        (external_username,),
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "email": result[0],
            "firstname": result[1],
            "lastname": result[2],
            "address": result[3],
            "phone_number": result[4],
        }
    else:
        return None


def map_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    mapped_data = {}
    for username, value in data.items():
        mapped_user = get_mapped_user_info(username)
        if mapped_user:
            mapped_username = f"{mapped_user['firstname']} {mapped_user['lastname']}"
            mapped_data[mapped_username] = value
        else:
            mapped_data[username] = value
    return mapped_data


def get_combined_mapped_data(
    base_url: str,
    username: str,
    api_token: str,
    projects: list,
    owner: str,
    repo: str,
    space_key: str,
) -> Dict[str, Any]:
    # Get Jira data
    jira_data = count_resolved_issues_by_assignee(
        base_url, username, api_token, projects
    )
    mapped_jira_data = map_user_data(jira_data)

    # Get GitHub data
    github_data = get_commits_per_user_in_repo(owner, repo)
    mapped_github_data = map_user_data(github_data)

    # Get Confluence data
    confluence_data = {}
    for user in set(list(jira_data.keys()) + list(github_data.keys())):
        content = get_confluence_contributions(
            base_url, username, api_token, space_key, user
        )
        if content:
            confluence_data[user] = len(
                content.split()
            )  # Simple word count as a metric
    mapped_confluence_data = map_user_data(confluence_data)

    return {
        "jira": mapped_jira_data,
        "github": mapped_github_data,
        "confluence": mapped_confluence_data,
    }


# Example usage
if __name__ == "__main__":
    base_url = "https://your-jira-instance.atlassian.net"
    username = "your-username"
    api_token = "your-api-token"
    projects = ["PROJECT1", "PROJECT2"]
    owner = "github-owner"
    repo = "github-repo"
    space_key = "confluence-space-key"

    combined_data = get_combined_mapped_data(
        base_url, username, api_token, projects, owner, repo, space_key
    )
    print(combined_data)
