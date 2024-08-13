import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage.storage_context import StorageContext
from llama_index.legacy.vector_stores import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
import chromadb

from self_appraisal_generator import generate_self_appraisal

# Initialize Chroma client
chroma_client = chromadb.Client()
chroma_collection = chroma_client.create_collection("my_collection")

# Load documents
documents = SimpleDirectoryReader('data').load_data()

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

def get_llm(llm_choice):
    if llm_choice == "OpenAI":
        return OpenAI(model="gpt-3.5-turbo", temperature=0)
    else:
        return Anthropic(model="claude-2", temperature=0)

st.title("Q&A Chatbot and Self-Appraisal Generator")

# LLM choice
llm_choice = st.sidebar.selectbox("Choose LLM", ["OpenAI", "Anthropic"])

# Q&A interface
st.header("Q&A Chatbot")
query = st.text_input("Enter your question:")
if st.button("Ask"):
    llm = get_llm(llm_choice)
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    st.write(response)

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
    appraisal = generate_self_appraisal(email, llm)
    st.write(appraisal)