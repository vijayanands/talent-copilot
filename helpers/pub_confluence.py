import requests
from bs4 import BeautifulSoup
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Configuration
base_url = "https://cwiki.apache.org/confluence"
space_key = "KAFKA"
page_title = "Kafka Replication"
username = "your-email@example.com"
api_token = "your-api-token"


# Function to find the page ID by title
def get_page_id(base_url, space_key, page_title):
    url = f"{base_url}/rest/api/content"
    params = {"type": "page", "spaceKey": space_key, "title": page_title}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["id"]
    return None


# Function to get the content of a page by ID
def get_page_content(base_url, page_id):
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version,history,ancestors,children.comment"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Get the page ID
page_id = get_page_id(base_url, space_key, page_title)
if page_id:
    # Get the page content
    page_data = get_page_content(base_url, page_id)
    if page_data:
        html_content = page_data["body"]["storage"]["value"]
        author = page_data["version"]["by"]["displayName"]
        created_at = page_data["history"]["createdDate"]

        # Print metadata
        print(f"Author: {author}")
        print(f"Created At: {created_at}")

        # Summarize content
        parser = HtmlParser.from_string(html_content, "", Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 5)  # Summarize to 5 sentences

        print("\nSummary:")
        for sentence in summary:
            print(sentence)

        # Extract comments if available
        if "children" in page_data and "comment" in page_data["children"]:
            comments = page_data["children"]["comment"]["results"]
            print("\nComments:")
            for comment in comments:
                commenter = comment["createdBy"]["displayName"]
                comment_text = BeautifulSoup(
                    comment["body"]["storage"]["value"], "html.parser"
                ).get_text()
                print(f"Comment by {commenter}: {comment_text}")
    else:
        print("Failed to retrieve page content.")
else:
    print("Failed to find page ID.")
