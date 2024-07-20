import requests

from auth.credentials import get_password


# url = "https://cwiki.apache.org/confluence/display/KAFKA/Clients"
def get_page(base_url: str, page_id: str, username: str):

    password = get_password("confluence", username)
    # API endpoint to get the page content
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"

    # Make the API request
    response = requests.get(url, auth=(username, password))

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
    get_page(base_url, page_id, username)
