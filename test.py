import requests
import os

# Configuration
base_url = "https://cwiki.apache.org/confluence"
space_key = "KAFKA"
page_title = "Introduction"
username = "vijayanands@gmail.com"
api_token = os.getenv("CONFLUENCE_API_KEY")


# Function to find the page ID by title
def get_page_id(base_url, space_key, page_title, auth):
    url = f"{base_url}/rest/api/content"
    params = {
        "type": "page",
        "spaceKey": space_key,
        "title": page_title,
        "expand": "body.storage",
    }
    response = requests.get(url, params=params, auth=auth)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["id"]
    return None


# Function to get the content of a page by ID
def get_page_content(base_url, page_id, auth):
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json()
        return data["body"]["storage"]["value"]
    return None


# Authentication (use an API token for your user)
auth = (username, api_token)

# Get the page ID
page_id = get_page_id(base_url, space_key, page_title, auth)
if page_id:
    # Get the page content
    page_content = get_page_content(base_url, page_id, auth)
    if page_content:
        print(page_content)
    else:
        print("Failed to retrieve page content.")
else:
    print("Failed to find page ID.")
