import json
import os
from collections import defaultdict
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from tools.headers import get_headers
from user_mapping import get_mapped_user

load_dotenv()

atlassian_base_url = "https://vijayanands.atlassian.net"
atlassian_username = "vijayanands@gmail.com"
atlassian_api_token = os.getenv("ATLASSIAN_API_TOKEN")
confluence_space_key = "SD"


def fetch_jira_projects(
    base_url: str, username: str, api_token: str
) -> List[Dict[str, Any]]:
    """
    Fetch a list of projects from Jira using basic authentication.
    :return: A list of dictionaries containing project information
    """
    api_endpoint = f"{base_url}/rest/api/3/project"

    headers = get_headers(username, api_token)
    response = requests.get(
        api_endpoint,
        headers=headers,
    )

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def fetch_jira_issues(
    base_url: str, username: str, project_key: str
) -> List[Dict[str, Any]]:
    url = f"{base_url}/rest/api/3/search"

    project_str = f"project = {project_key}"
    query = {
        "jql": project_str,
        "maxResults": 100,
    }

    # url = "https://vijayanands.atlassian.net/rest/api/3/search?query={'jql': 'project = SSP', 'maxResults': 100}"
    response = requests.request(
        "GET",
        url,
        headers=get_headers(username, api_token),
        params=query,  # query parameters
    )

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def count_resolved_issues(base_url, username, api_token, author):
    projects = fetch_jira_projects(base_url, username, api_token)
    print(json.dumps(projects, indent=2))
    projects = [project["key"] for project in projects]

    # Initialize the count
    total_resolved = 0

    # Construct the JQL query
    jql_query = f'project in ({",".join(projects)}) AND resolution = Done AND assignee = "{author}"'

    # Set up the API endpoint
    api_endpoint = f"{base_url}/rest/api/3/search"

    # Set up the parameters for the request
    params = {
        "jql": jql_query,
        # "maxResults": 0,  # We only need the total, not the actual issues
    }

    try:
        # Make the API request
        response = requests.get(
            api_endpoint, headers=get_headers(username, api_token), params=params
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the JSON response
        data = response.json()

        jira_list = []
        for issue in data["issues"]:
            jira_data = defaultdict()
            jira_data["link"] = issue["self"]
            jira_data["description"] = issue["fields"]["issuetype"]["description"]
            jira_data["timespent"] = issue["fields"]["timespent"]
            jira_data["resolutiondate"] = issue["fields"]["resolutiondate"]
            jira_data["priority"] = issue["fields"]["priority"]["name"]
            print (json.dumps(jira_data, indent=5))
            jira_list.append(jira_data)

        # Get the total number of issues
        jira_response = defaultdict()
        jira_response["total_resolved"] = len(jira_list)
        jira_response["jiras_resolved"] = jira_list
        return jira_response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def count_resolved_issues_by_assignee(base_url, username, api_token):
    projects = fetch_jira_projects(base_url, username, api_token)
    print(json.dumps(projects, indent=2))
    projects = [project["key"] for project in projects]

    # Initialize the count dictionary
    resolved_counts = defaultdict(int)

    # Construct the JQL query
    jql_query = f'project in ({",".join(projects)}) AND resolution = Done'

    # Set up the API endpoint
    api_endpoint = f"{base_url}/rest/api/3/search"

    # Set up the parameters for the request
    params = {
        "jql": jql_query,
        "maxResults": 100,  # Adjust this value based on your needs
        "fields": "assignee",
    }

    try:
        while True:
            # Make the API request
            response = requests.get(
                api_endpoint, headers=get_headers(username, api_token), params=params
            )
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON response
            data = response.json()

            # Process each issue
            for issue in data["issues"]:
                assignee = issue["fields"]["assignee"]
                if assignee:
                    resolved_counts[assignee["displayName"]] += 1
                else:
                    resolved_counts["Unassigned"] += 1

            # Check if there are more issues to fetch
            if data["startAt"] + len(data["issues"]) >= data["total"]:
                break

            # Update startAt for the next page
            params["startAt"] = data["startAt"] + len(data["issues"])

        return resolved_counts

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def map_jira_users(jira_data: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    mapped_jira_activities = {}

    for username, count in jira_data.items():
        mapped_user = get_mapped_user(username)
        if mapped_user:
            mapped_jira_activities[mapped_user["email"]] = {
                "jira_resolved_issues": count,
                "user_info": mapped_user,
            }

    return mapped_jira_activities


def get_jira_contributions_by_author(author: str):
    response = count_resolved_issues(
        atlassian_base_url, atlassian_username, atlassian_api_token, author
    )
    jira_data = response.get("jiras_resolved", [])
    jira_url_list = [jira["link"] for jira in jira_data]
    if response is not None:
        return {
            "author": author,
            "total_resolved_issues": response.get("total_resolved_issues"),
            "jiras_data": jira_data,
            "jira_list": jira_url_list,
        }
    else:
        return None


# Usage example
if __name__ == "__main__":
    base_url = "https://vijayanands.atlassian.net"
    username = "vijayanands@gmail.com"
    api_token = os.getenv("ATLASSIAN_API_TOKEN")

    try:
        issues = fetch_jira_issues(base_url, username, "SSP")
        print(json.dumps(issues, indent=2))
        author = "vijayanands@gmail.com"
        resolved_count = count_resolved_issues(base_url, username, api_token, author)

        if resolved_count is not None:
            print(f"Number of resolved issues by {author}: {resolved_count}")

        resolved_counts = count_resolved_issues_by_assignee(
            base_url, username, api_token
        )

        if resolved_counts is not None:
            print("Number of resolved issues by assignee:")
            for assignee, count in sorted(
                resolved_counts.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"{assignee}: {count}")
            print(f"Total resolved issues: {sum(resolved_counts.values())}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
