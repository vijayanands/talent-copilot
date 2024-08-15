import json
import os
import time
import shutil
import random
from typing import Dict, List
from uuid import uuid5, NAMESPACE_DNS

from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.node_parser import SimpleNodeParser

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore

from helpers.confluence import get_confluence_contributions_per_user
from helpers.github import get_github_contributions_by_repo
from helpers.jira import get_jira_contributions_per_user
from constants import unique_user_emails
from pinecone import Pinecone, ServerlessSpec, PineconeException
from dotenv import load_dotenv

load_dotenv()

atlassian_base_url = "https://vijayanands.atlassian.net"
atlassian_username = "vijayanands@gmail.com"

# Initialize Pinecone
index_name = "pathforge-data"
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Function to convert nested dictionary to string
def _dict_to_string(d: Dict, indent: int = 0) -> str:
    result = []
    for key, value in d.items():
        if isinstance(value, dict):
            result.append(f"{'  ' * indent}{key}:")
            result.append(_dict_to_string(value, indent + 1))
        elif isinstance(value, list):
            result.append(f"{'  ' * indent}{key}:")
            for item in value:
                if isinstance(item, dict):
                    result.append(_dict_to_string(item, indent + 2))
                else:
                    result.append(f"{'  ' * (indent + 2)}- {item}")
        else:
            result.append(f"{'  ' * indent}{key}: {value}")
    return "\n".join(result)

# Function to generate a consistent ID for a user
def _generate_key(user: str) -> str:
    return str(uuid5(NAMESPACE_DNS, user))

def _get_documents_to_ingest() -> List[Document]:
    # Fetch data
    jira_documents = get_jira_contributions_per_user()
    github_documents = get_github_contributions_by_repo("octocat", "Hello-World")
    confluence_documents = get_confluence_contributions_per_user()

    all_documents_per_user = {}
    for user in unique_user_emails:
        all_documents_per_user[user] = {
            "jira": jira_documents[user],
            "github": github_documents[user],
            "confluence": confluence_documents[user]
        }

    print(json.dumps(all_documents_per_user, indent=2))

    # Process documents
    documents = []
    for user, user_data in all_documents_per_user.items():
        content = json.dumps(user_data, indent=2)
        metadata = {
            "email": user,
            "has_jira": bool(user_data["jira"]),
            "has_github": bool(user_data["github"]),
            "has_confluence": bool(user_data["confluence"])
        }
        user_id = _generate_key(user)
        doc = Document(text=content, metadata=metadata, id_=user_id)
        documents.append(doc)

    return documents

def create_pinecone_index():
    try:
        print(f"Creating new Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        
        # Wait for the index to be created
        while True:
            try:
                index_description = pc.describe_index(index_name)
                if index_description.status['ready']:
                    print(f"Pinecone index {index_name} is ready.")
                    return True
                else:
                    print("Waiting for Pinecone index to be ready...")
                    time.sleep(10)
            except Exception as e:
                print(f"Error checking index status: {e}")
                time.sleep(10)
    except Exception as e:
        print(f"Failed to create Pinecone index: {e}")
        return False


def verify_index_creation_with_retries(index: VectorStoreIndex, documents: List[Document],
                                       max_retries: int = 5, retry_delay: int = 10,
                                       sample_size: int = 5, similarity_threshold: float = 0.5) -> bool:
    for attempt in range(max_retries):
        print(f"Verification attempt {attempt + 1} of {max_retries}")
        if verify_index_creation(index, documents, sample_size, similarity_threshold):
            print("Index verification successful!")
            return True
        else:
            if attempt < max_retries - 1:  # Don't sleep after the last attempt
                print(f"Verification failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All verification attempts failed.")
    return False


def verify_index_creation(index: VectorStoreIndex, documents: List[Document],
                          sample_size: int = 5, similarity_threshold: float = 0.5) -> bool:
    # Step 1: Verify vector count
    if not verify_vector_count(index):
        return False

    # Step 2: Sample and verify content retrieval
    sampled_docs = random.sample(documents, min(sample_size, len(documents)))
    query_engine = index.as_query_engine()

    for doc in sampled_docs:
        if not verify_document_retrieval(query_engine, doc, similarity_threshold):
            return False

    return True


def verify_vector_count(index: VectorStoreIndex) -> bool:
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    pinecone_index = pc.Index(index_name)

    stats = pinecone_index.describe_index_stats()
    vector_count = stats['total_vector_count']

    print(f"Pinecone index stats - Total vectors: {vector_count}")
    return vector_count > 0


def verify_document_retrieval(query_engine: BaseQueryEngine, document: Document,
                              similarity_threshold: float) -> bool:
    # Extract multiple snippets from the document
    snippets = extract_snippets(document.text, num_snippets=3, snippet_length=100)

    for snippet in snippets:
        # Query the index for this content
        response = query_engine.query(snippet)

        # Check if the response contains part of the original document's content
        similarity = calculate_similarity(response.response, document.text)

        if similarity >= similarity_threshold:
            print(f"Successfully retrieved content for document: {document.id_}")
            return True

    print(f"Failed to retrieve content for document: {document.id_}")
    return False


def extract_snippets(text: str, num_snippets: int = 3, snippet_length: int = 100) -> List[str]:
    if len(text) <= snippet_length:
        return [text]

    snippets = []
    for _ in range(num_snippets):
        start = random.randint(0, max(0, len(text) - snippet_length))
        snippets.append(text[start:start + snippet_length])

    return snippets


def calculate_similarity(text1: str, text2: str) -> float:
    # Implement a similarity measure (e.g., cosine similarity, Jaccard similarity)
    # For simplicity, let's use a basic overlap coefficient
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    overlap = len(words1.intersection(words2))
    return overlap / min(len(words1), len(words2))


def ingest_data():
    recreate_index = os.environ.get("RECREATE_INDEX", "false").lower() == "true"
    local_persist_path = "/home/vijay/workspace/talent-copilot-1/data/pinecone_store"

    # Set up Pinecone vector store
    embed_model = OpenAIEmbedding()
    
    if recreate_index:
        # Delete local store if it exists
        if os.path.exists(local_persist_path):
            print(f"Deleting existing local store at {local_persist_path}")
            shutil.rmtree(local_persist_path)
        
        if index_name in pc.list_indexes().names():
            print(f"Deleting existing Pinecone index: {index_name}")
            pc.delete_index(index_name)
        
        if not create_pinecone_index():
            print("Failed to create Pinecone index. Exiting.")
            return None
    elif index_name not in pc.list_indexes().names():
        print(f"Pinecone index {index_name} does not exist and recreate_index is False.")
        print("Please set RECREATE_INDEX=true to create a new index.")
        return None

    print("Initializing Pinecone vector store...")
    vector_store = PineconeVectorStore(index_name=index_name)
    
    if os.path.exists(local_persist_path) and not recreate_index:
        print("Loading existing Pinecone store from local persistence...")
        storage_context = StorageContext.from_defaults(persist_dir=local_persist_path, vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    else:
        print("Creating new storage context...")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if recreate_index:
            print("Recreating index with new documents...")
            documents = _get_documents_to_ingest()

            # Create a SimpleNodeParser with custom chunk size and overlap
            node_parser = SimpleNodeParser.from_defaults(
                chunk_size=500,
                chunk_overlap=50
            )
    
            # Use the node parser to chunk the documents
            nodes = node_parser.get_nodes_from_documents(documents)

            # Create the index from nodes instead of documents
            index = VectorStoreIndex(
                nodes,
                storage_context=storage_context,
                embed_model=embed_model
            )

            # Comprehensive verification with retries
            if verify_index_creation_with_retries(index, documents):
                print("Index created and verified successfully. Persisting Pinecone store locally...")
                storage_context.persist(persist_dir=local_persist_path)
            else:
                print("Failed to verify index creation after multiple attempts. Please check the logs and try again.")
                return None
        else:
            print("Error: Local store not found and recreate_index is False.")
            print("Please set RECREATE_INDEX=true to create a new index.")
            return None

    return index

# Example usage
if __name__ == "__main__":
    questions = [
        "What are the Jira issues for vijayanands@gmail.com?",
        "How many pull requests are there for vijayanands@yahoo.com?",
        "What is the content of the 'Getting started in Confluence' page for vjy1970@gmail.com?",
        "Which users have GitHub data?",
        "List all email addresses that have Confluence data.",
    ]

    # Set up query engine
    index = ingest_data()
    if index is None:
        exit(1)

    query_engine = index.as_query_engine()
    for question in questions:
        print(f"Question: {question}")
        print(f"Answer: {query_engine.query(question)}")
        print()