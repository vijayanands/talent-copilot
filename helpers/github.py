import requests


def get_pull_request_by_author(username: str, repo_owner: str, repo_name: str) -> None:
    # URL for searching pull requests
    url = f"https://api.github.com/search/issues"

    # Query to filter pull requests by user and repository
    query = f"repo:{repo_owner}/{repo_name} type:pr author:{username}"

    # Parameters for the search query
    params = {
        "q": query,
        "per_page": 100,  # Number of results per page
    }

    all_pull_requests = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.json()}")

        pull_requests = response.json().get("items", [])
        if not pull_requests:
            break

        all_pull_requests.extend(pull_requests)
        page += 1

    print(f"Total Pull Requests by {username}: {len(all_pull_requests)}")
    for pr in all_pull_requests:
        print(f"Title: {pr['title']}, URL: {pr['html_url']}")


def get_pull_request_info(username: str, repo_owner: str, repo_name: str) -> None:
    # URL for listing pull requests
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"

    # Parameters to filter pull requests by author
    params = {
        "state": "open",  # Can be 'open', 'closed', or 'all'
        "author": username,
        "per_page": 100,  # Number of results per page
    }

    all_pull_requests = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.json()}")

        pull_requests = response.json()
        if not pull_requests:
            break

        print(f"Pull requests: {len(pull_requests)}")

        # Filter pull requests by the specified username
        user_pull_requests = [
            pr for pr in pull_requests if pr["user"]["login"] == username
        ]
        all_pull_requests.extend(user_pull_requests)
        page += 1

    print(f"Total Pull Requests by {username}: {len(all_pull_requests)}")
    for pr in all_pull_requests:
        print(f"Title: {pr['title']}, URL: {pr['html_url']}")
