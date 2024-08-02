from typing import List, Dict, Any

import requests
import os
from tools.headers import get_headers
from dotenv import load_dotenv

load_dotenv()


def get_page_id(base_url, space_key, page_title, username, api_token):
    url = f"{base_url}/rest/api/content"
    params = {"type": "page", "spaceKey": space_key, "title": page_title}
    response = requests.get(
        url, headers=get_headers(username, api_token), params=params
    )
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["id"]
    return None


def get_spaces(base_url, username, api_token) -> List[Dict[str, Any]]:
    url = f"{base_url}/api/v2/spaces"
    response = requests.get(url, headers=get_headers(username, api_token))
    if response.status_code == 200:
        data = response.json()
        return data["results"]
    return None


# url = "https://cwiki.apache.org/confluence/display/KAFKA/Clients"
def get_page_content(
    base_url: str, page_id: str, username: str, api_token: str
) -> str or None:
    # API endpoint to get the page content
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"

    # Make the API request
    headers = get_headers(username, api_token)
    response = requests.request(
        "GET",
        url,
        headers=headers,
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        page_content = data["body"]["storage"]["value"]

        # Print auththe page content
        print(page_content)
        return page_content
    else:
        print(f"Failed to retrieve page content. Status code: {response.status_code}")
    return None


def get_page_content_v2(base_url, page_id, username, api_token) -> str or None:
    headers = get_headers(username, api_token)
    # Use the expand parameter to include body content
    url = f"{base_url}/api/v2/pages/{page_id}?body-format=storage"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        page_data = response.json()
        page_title = page_data.get("title", "")
        page_body = page_data.get("body", {}).get("storage", {}).get("value", "")

        print(f"Page Title: {page_title}")
        print("Page Content:")
        print(page_body)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    base_url = "https://vijayanands.atlassian.net/wiki"
    username = "vijayanands@gmail.com"
    api_token = os.getenv("ATLASSIAN_API_TOKEN")
    space_key = "SD"
    page_title = "Conversational AI For Customer Service"
    spaces = get_spaces(base_url, username, api_token)
    page_id = get_page_id(base_url, space_key, page_title, username, api_token)
    # page_id = "2686977"
    # get_page_content(base_url, page_id, username, api_token)
    get_page_content_v2(base_url, page_id, username, api_token)
