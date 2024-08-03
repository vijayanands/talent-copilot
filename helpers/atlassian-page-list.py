import os
import requests
from dotenv import load_dotenv
from base64 import b64encode

# Load environment variables at the start
load_dotenv()

# Set the base URL for all API calls
BASE_URL = "https://vijayanands.atlassian.net"


def get_basic_auth_header():
    username = "vijayanands@gmail.com"
    api_token = os.getenv("ATLASSIAN_API_TOKEN")

    if not api_token:
        raise ValueError("ATLASSIAN_API_TOKEN not found in environment variables")

    auth_string = b64encode(f"{username}:{api_token}".encode()).decode()
    return {"Authorization": f"Basic {auth_string}"}


def get_space_id(space_key):
    api_endpoint = f"{BASE_URL}/wiki/api/v2/spaces"

    headers = get_basic_auth_header()
    headers["Accept"] = "application/json"

    params = {"key": space_key, "status": "current"}

    response = requests.get(api_endpoint, headers=headers, params=params)

    if response.status_code == 200:
        spaces = response.json()["results"]
        if spaces:
            return spaces[0]["id"]
        else:
            print(f"No space found with key '{space_key}'")
            return None
    else:
        print(f"Error fetching space ID: {response.status_code}")
        print(response.text)
        return None


def get_confluence_pages(space_id):
    api_endpoint = f"{BASE_URL}/wiki/api/v2/spaces/{space_id}/pages"

    headers = get_basic_auth_header()
    headers["Accept"] = "application/json"

    params = {"limit": 100, "status": "current"}  # Adjust as needed

    response = requests.get(api_endpoint, headers=headers, params=params)

    if response.status_code == 200:
        pages = response.json()["results"]
        return pages
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def main():
    space_key = "SD"
    space_id = get_space_id(space_key)

    if space_id:
        pages = get_confluence_pages(space_id)
        if pages:
            print(f"Pages in space '{space_key}' (ID: {space_id}):")
            for page in pages:
                print(f"- {page['title']} (ID: {page['id']})")
        else:
            print("Failed to retrieve pages.")
    else:
        print(f"Failed to retrieve space ID for key '{space_key}'.")


if __name__ == "__main__":
    main()
