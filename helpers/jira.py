import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from tools.headers import get_headers

load_dotenv()


def fetch_jira_projects(
    base_url: str, username: str, api_token: str
) -> List[Dict[str, Any]]:
    """
    Fetch a list of projects from Jira using basic authentication.
    :return: A list of dictionaries containing project information
    """
    api_endpoint = f"{base_url}/rest/api/3/project"

    response = requests.get(
        api_endpoint,
        headers=get_headers(username, api_token),
    )

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def fetch_jira_issues(base_url: str, username: str, project_key: str) -> List[Dict[str, Any]]:
    url  = f"{base_url}/rest/api/3/search"

    project_str = f"project = {project_key}"
    query = {
        'jql': project_str,
        'maxResults': 100,
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


# Usage example
if __name__ == "__main__":
    base_url = "https://vijayanands.atlassian.net"
    username = "vijayanands@gmail.com"
    api_token = os.getenv("ATLASSIAN_API_TOKEN")

    try:
        projects = fetch_jira_projects(base_url, username, api_token)
        print(json.dumps(projects, indent=2))
        # issues = fetch_jira_issues(base_url, username,"SSP")
        # print(json.dumps(issues, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
