import json
import streamlit as st
import os
from llama_index.core import download_loader
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core.schema import Document

from constants import unique_user_emails
from functions.self_appraisal import create_self_appraisal
from dotenv import load_dotenv
from typing import List

from helpers.ingestion import ingest_data

load_dotenv()

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
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                file_documents = loader.load_data(file_path)
                documents.extend(file_documents)
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
    return documents


def pretty_print_appraisal(appraisal_data):
    # Convert string to dictionary if needed
    if isinstance(appraisal_data, str):
        try:
            appraisal_data = json.loads(appraisal_data)
        except json.JSONDecodeError:
            st.error("Invalid JSON string provided. Please check the input.")
            return

    if not isinstance(appraisal_data, dict):
        st.error("Input must be a dictionary or a valid JSON string.")
        return

    st.header("Self-Appraisal")

    # Summary
    if "Summary" in appraisal_data:
        st.subheader("Summary")
        st.write(appraisal_data["Summary"])

    # Key Achievements
    if "Key Achievements" in appraisal_data:
        st.subheader("Key Achievements")
        for achievement in appraisal_data["Key Achievements"]:
            st.markdown(f"• {achievement}")

    # Contributions
    if "Contributions" in appraisal_data:
        st.subheader("Contributions")
        for platform, contribution in appraisal_data["Contributions"].items():
            st.markdown(f"**{platform}**")
            st.write(contribution)
            st.markdown("---")

    # Learning Opportunities
    if "Learning Opportunities" in appraisal_data:
        st.subheader("Learning Opportunities")
        for opportunity in appraisal_data["Learning Opportunities"]:
            st.markdown(f"• {opportunity}")

def ask(llm, query, index):
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    return response, response.response  # Return both full response and text


def setup_streamlit_ui():
    st.set_page_config(page_title="Employee Copilot", layout="wide")

    # Custom CSS for styling
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

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

        # Debug checkbox moved outside of the button click condition
        show_full_response = st.checkbox("Show full response (debug)", value=False)

        if st.button("Ask", key="ask_button"):
            # Initialize data
            index = ingest_data()
            llm = get_llm(llm_choice)
            with st.spinner("Generating response..."):
                full_response, response_text = ask(llm, query, index)

            # Display the response text
            st.write("Response:")
            st.write(response_text)

            # Optionally show full response based on checkbox
            if show_full_response:
                st.write("Full Response (Debug):")
                st.write(full_response)

    with tab2:
        st.header("Self-Appraisal Generator")
        email = st.selectbox("Select author email:", unique_user_emails)
        if st.button("Generate Self-Appraisal", key="generate_button"):
            llm = get_llm(llm_choice)
            with st.spinner("Generating self-appraisal..."):
                appraisal = create_self_appraisal(llm_choice, email)
            pretty_print_appraisal(appraisal)

if __name__ == "__main__":
    setup_streamlit_ui()


# Example usage
# questions = [
#     "What are the Jira issues for vijayanands@gmail.com?",
#     "How many pull requests are there for vijayanands@yahoo.com?",
#     "What is the content of the 'Getting started in Confluence' page for vjy1970@gmail.com?",
#     "Which users have GitHub data?",
#     "List all email addresses that have Confluence data.",
# ]
