import requests
import os
from tools.headers import get_headers
from dotenv import load_dotenv

load_dotenv()


def get_page_id(base_url, space_key, page_title):
    url = f"{base_url}/rest/api/content"
    params = {"type": "page", "spaceKey": space_key, "title": page_title}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["id"]
    return None

# url = "https://cwiki.apache.org/confluence/display/KAFKA/Clients"
def get_page_content(base_url: str, page_id: str, username: str, api_token: str):

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
    else:
        print(f"Failed to retrieve page content. Status code: {response.status_code}")


if __name__ == "__main__":
    base_url = "https://vijayanands.atlassian.net/wiki"
    page_id = "2686977"
    username = "vijayanands@gmail.com"
    api_token = os.getenv("ATLASSIAN_API_KEY")
    get_page_content(base_url, page_id, username, api_token)
