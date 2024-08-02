import requests
import os
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
from tools.headers import get_headers
from dotenv import load_dotenv
from helpers.confluence import get_page_content_v2

load_dotenv()


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


# Usage example
base_url = "https://vijayanands.atlassian.net/wiki"
username = "vijayanands@gmail.com"
api_token = os.getenv("ATLASSIAN_API_TOKEN")
space_key = "SD"
target_username = "email2vijay@gmail.com"

contents = get_confluence_contributions(
    base_url, username, api_token, space_key, username
)
