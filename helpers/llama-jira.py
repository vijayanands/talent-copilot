from llama_index.readers.jira.base import JiraReader

reader = JiraReader(
    email="email", api_token="api_token", server_url="your-jira-server.com"
)
documents = reader.load_data(query="project = <your-project>")
