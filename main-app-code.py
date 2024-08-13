import json
import streamlit as st
import os
import pinecone
import os
from llama_index.core import download_loader, Document
from typing import List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.legacy.vector_stores import PineconeVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import TextNode
from pinecone import Pinecone, ServerlessSpec

from self_appraisal_generator import generate_self_appraisal
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
index_name = "pathforge-data"
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Update this to match your embedding dimension
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Connect to the index
pinecone_index = pc.Index(index_name)

def get_llm(llm_choice):
    if llm_choice == "OpenAI":
        return OpenAI(model="gpt-3.5-turbo", temperature=0)
    else:
        return Anthropic(model="claude-2", temperature=0)

def ingest_data(llm_choice):

    def load_json_files_from_directory(directory_path: str) -> List[Document]:
        JSONReader = download_loader("JSONReader")
        loader = JSONReader()

        documents = []

        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                file_path = os.path.join(directory_path, filename)
                try:
                    file_documents = loader.load_data(file_path)
                    documents.extend(file_documents)
                    print(f"Loaded {len(file_documents)} documents from {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")

        return documents

    # Usage
    directory_path = "pathforge-data"
    all_documents = load_json_files_from_directory(directory_path)
    print(f"Total documents loaded: {len(all_documents)}")

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    # storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # llm = get_llm(llm_choice)
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    # service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model, node_parser=node_parser)

    # Create and populate the index
    embed_model = OpenAIEmbedding()
    index = VectorStoreIndex.from_documents(
        all_documents,
        vector_store=vector_store,
        embed_model=embed_model
    )
    # index = VectorStoreIndex.from_documents(all_documents, storage_context=storage_context, service_context=service_context, show_progress=True)
    print("finished ingesting data")
    return index

def ask(llm, query):
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    print(response)

st.title("Q&A Chatbot and Self-Appraisal Generator")

# LLM choice
llm_choice = st.sidebar.selectbox("Choose LLM", ["OpenAI", "Anthropic"])
index = ingest_data(llm_choice)

# Q&A interface
st.header("Q&A Chatbot")
query = st.text_input("Enter your question:")
if st.button("Ask"):
    llm = get_llm(llm_choice)
    ask(llm, query)

# Self-appraisal interface
st.header("Self-Appraisal Generator")
email = st.selectbox("Select author email:", [
    "vijayanands@gmail.com", 
    "email2vijay@gmail.com", 
    "vijayanands@yahoo.com", 
    "vjy1970@gmail.com"
])
if st.button("Generate Self-Appraisal"):
    llm = get_llm(llm_choice)
    appraisal = generate_self_appraisal(email, llm, pinecone_index)
    st.write(appraisal)
