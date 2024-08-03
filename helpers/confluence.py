import os
import re
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup, Comment
from dotenv import load_dotenv

from helpers.user_mapping import get_mapped_user
from tmp_inputs import (atlassian_api_token, atlassian_base_url,
                        atlassian_username, confluence_space_key)
from tools.headers import get_headers

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
        return page_body
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_confluence_contributions(
    base_url, username, api_token, space_key, target_username
):
    # Function to make API requests
    def make_request(url, params=None):
        response = requests.get(
            url, headers=get_headers(username, api_token), params=params
        )
        response.raise_for_status()
        return response.json()

    # Get user information
    # user_url = f"{base_url}/api/v2/users"
    # user_params = {"accountId": target_username}
    # user_info = make_request(user_url, user_params)
    #
    # if not user_info.get("results"):
    #     print(f"User {target_username} not found.")
    #     return
    #
    # user_id = user_info["results"][0]["accountId"]

    # Get pages created by the user in the specified space
    pages_url = f"{base_url}/api/v2/pages"
    pages_params = {
        "spaceId": space_key,
        "creator": target_username,
        "limit": 100,  # Adjust as needed
    }
    pages = make_request(pages_url, pages_params)

    print(f"Pages created by {target_username} in space {space_key}:")
    for page in pages.get("results", []):
        print(f"Title: {page['title']}")
        print(f"ID: {page['id']}")
        print(f"Created: {page['createdAt']}")

        # Get page content
        content = get_page_content_v2(base_url, page["id"], username, api_token)

    # Get comments by the user in the specified space
    # comments_url = f"{base_url}/api/v2/pages/comments"
    # comments_params = {
    #     "spaceId": space_key,
    #     "creator": target_username,
    #     "limit": 100,  # Adjust as needed
    # }
    # comments = make_request(comments_url, comments_params)
    #
    # print(f"\nComments by {target_username} in space {space_key}:")
    # for comment in comments.get("results", []):
    #     print(f"Page ID: {comment['pageId']}")
    #     print(f"Created: {comment['createdAt']}")
    #     print(f"Content: {comment['body']['storage']['value']}")
    #     print("---")
    return content


def clean_confluence_content(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda string: isinstance(string, Comment)):
        comment.extract()

    # Extract text from remaining tags
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # Drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def map_confluence_users(confluence_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    mapped_confluence_activities = {}

    for username, content in confluence_data.items():
        mapped_user = get_mapped_user(username)
        if mapped_user:
            mapped_confluence_activities[mapped_user["email"]] = {
                "confluence_contributions": content,
                "user_info": mapped_user,
            }

    return mapped_confluence_activities


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


def get_confluence_contributions_by_author(author: str):
    confluence_data = get_confluence_contributions(
        atlassian_base_url,
        atlassian_username,
        atlassian_api_token,
        confluence_space_key,
        author,
    )
    if not confluence_data:
        return None
    clean_confluence_data = clean_confluence_content(confluence_data)
    mapped_confluence_data = map_confluence_users(clean_confluence_data)
    return mapped_confluence_data
