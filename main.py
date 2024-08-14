import streamlit as st
import os
from llama_index.core import VectorStoreIndex, download_loader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.legacy.vector_stores import PineconeVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core.schema import Document
from pinecone import Pinecone, ServerlessSpec

from constants import unique_user_emails
from self_appraisal import create_self_appraisal
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Initialize Pinecone
index_name = "pathforge-data"
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

pinecone_index = pc.Index(index_name)

def get_llm(llm_choice):
    if llm_choice == "OpenAI":
        return OpenAI(model="gpt-3.5-turbo", temperature=0)
    else:
        return Anthropic(model="claude-2", temperature=0)

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
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
    return documents

@st.cache_resource
def ingest_data():
    directory_path = "pathforge-data"
    all_documents = load_json_files_from_directory(directory_path)
    
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    
    index = VectorStoreIndex.from_documents(
        all_documents,
        vector_store=vector_store,
        embed_model=embed_model
    )
    return index

def ask(llm, query, index):
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    return response

def setup_streamlit_ui():
    st.set_page_config(page_title="Employee Copilot", layout="wide")
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .content-container {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    .stSelectbox>div>div>div {
        border: 1px solid #ccc;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Employee Copilot")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        llm_choice = st.selectbox("Choose LLM", ["OpenAI", "Anthropic"])

    # Tabs using Streamlit's native tab component
    tab1, tab2 = st.tabs(["Q&A Chatbot", "Self-Appraisal Generator"])

    with tab1:
        st.header("Q&A Chatbot")
        query = st.text_input("Enter your question:")
        if st.button("Ask", key="ask_button"):
            # Initialize data
            index = ingest_data()
            llm = get_llm(llm_choice)
            with st.spinner("Generating response..."):
                response = ask(llm, query, index)
            st.write(response)

    with tab2:
        st.header("Self-Appraisal Generator")
        email = st.selectbox("Select author email:", unique_user_emails)
        if st.button("Generate Self-Appraisal", key="generate_button"):
            llm = get_llm(llm_choice)
            with st.spinner("Generating self-appraisal..."):
                # appraisal = generate_self_appraisal(email, llm, pinecone_index)
                appraisal = create_self_appraisal(llm_choice, email)
            st.write(appraisal)

if __name__ == "__main__":
    setup_streamlit_ui()
