import json
import os
import streamlit as st
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.legacy.vector_stores import PineconeVectorStore

from helpers.confluence import get_confluence_contributions_per_user
from helpers.github import get_github_contributions_by_repo
from helpers.jira import get_jira_contributions_per_user
from constants import unique_user_emails
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

atlassian_base_url = "https://vijayanands.atlassian.net"
atlassian_username = "vijayanands@gmail.com"

# Initialize Pinecone
index_name = "pathforge-data"
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

pinecone_index = pc.Index(index_name)



@st.cache_resource
def ingest_data():
    directory_path = "pathforge-data"
    jira_documents = get_jira_contributions_per_user()
    github_documents = get_github_contributions_by_repo("octocat", "Hello-World")
    confluence_documents = get_confluence_contributions_per_user()

    all_documents_per_user = {}
    for user in unique_user_emails:
        all_documents_per_user[user] = {}
        all_documents_per_user[user]["jira"] = jira_documents[user]
        all_documents_per_user[user]["github"] = github_documents[user]
        all_documents_per_user[user]["confluence"] = confluence_documents[user]

    print(json.dumps(all_documents_per_user, indent=2))

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

    index = VectorStoreIndex.from_documents(
        all_documents_per_user, vector_store=vector_store, embed_model=embed_model
    )
    return index
