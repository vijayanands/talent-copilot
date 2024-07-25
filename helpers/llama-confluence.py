# Example that reads the pages with the `page_ids`
from llama_index.readers.confluence import ConfluenceReader

token = {"access_token": "<access_token>", "token_type": "<token_type>"}
oauth2_dict = {"client_id": "<client_id>", "token": token}

base_url = "https://yoursite.atlassian.com/wiki"

page_ids = ["<page_id_1>", "<page_id_2>", "<page_id_3"]
space_key = "<space_key>"

reader = ConfluenceReader(base_url=base_url, oauth2=oauth2_dict)
documents = reader.load_data(
    space_key=space_key, include_attachments=True, page_status="current"
)
documents.extend(
    reader.load_data(page_ids=page_ids, include_children=True, include_attachments=True)
)
