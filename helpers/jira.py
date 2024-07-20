import json

import requests
from requests.auth import HTTPBasicAuth

from auth.credentials import get_password


def get_projects(base_url, username) -> None:
    password = get_password("jira", username)
    auth = HTTPBasicAuth(username=username, password=password)

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, auth=auth)

    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )


def get_issues(base_url, username) -> None:
    password = get_password("jira", username)
    auth = HTTPBasicAuth(username=username, password=password)

    headers = {"Accept": "application/json"}

    query = {"jql": "project = SSP"}

    response = requests.request("GET", url, headers=headers, params=query, auth=auth)

    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )


if __name__ == "__main__":
    url = "https://vijayanands.atlassian.net/rest/api/3/project"
    get_projects(url, "email2vijay@gmail.com")
    url = "https://vijayanands.atlassian.net/rest/api/3/search"
    get_issues(url, "email2vijay@gmail.com")
