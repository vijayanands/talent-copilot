import base64
import os
import streamlit as st
import bcrypt
import re as regex
from sqlalchemy import create_engine, Column, Integer, String, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
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

# Database setup
engine = create_engine('sqlite:///users.db', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_manager = Column(Boolean, default=False)
    linkedin_profile = Column(String)

# Check if table exists, create only if it doesn't
def create_table_if_not_exists(engine, table):
    if not inspect(engine).has_table(table.__tablename__):
        table.__table__.create(engine)

create_table_if_not_exists(engine, User)

Session = sessionmaker(bind=engine)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def register_user(email, password, is_manager, linkedin_profile):
    session = Session()
    hashed_password = hash_password(password)
    new_user = User(email=email, password=hashed_password, is_manager=is_manager, linkedin_profile=linkedin_profile)
    session.add(new_user)
    session.commit()
    session.close()

def verify_login(email, password):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    if user and verify_password(user.password, password):
        return user
    return None

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

def is_password_valid(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    # Check if password contains at least one number
    if not regex.search(r"\d", password):
        return False
    # Check if password contains at least one symbol
    if not regex.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def login_page():
    st.header("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        user = verify_login(email, password)
        if user:
            st.session_state.user = user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid email or password")


def signup_page():
    st.header("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    st.caption("Password must be at least 8 characters long, contain at least one number and one symbol.")
    is_manager = st.checkbox("I am a people manager", key="signup_is_manager")
    linkedin_profile = st.text_input("LinkedIn Profile (optional)", key="signup_linkedin")
    if st.button("Sign Up", key="signup_button"):
        if not is_password_valid(password):
            st.error("Password does not meet the requirements. Please ensure it's at least 8 characters long, contains at least one number and one symbol.")
        else:
            try:
                register_user(email, password, is_manager, linkedin_profile)
                st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

def register_user(email, password, is_manager, linkedin_profile):
    session = Session()
    if not is_password_valid(password):
        raise ValueError("Password does not meet the requirements.")
    hashed_password = hash_password(password)
    new_user = User(email=email, password=hashed_password, is_manager=is_manager, linkedin_profile=linkedin_profile)
    session.add(new_user)
    session.commit()
    session.close()


def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_page_container_style(
        max_width: int = 1100, max_width_100_percent: bool = False,
        padding_top: int = 1, padding_right: int = 10, padding_left: int = 10, padding_bottom: int = 10,
        color: str = 'black', background_color: str = '#f0f2f6',
):
    if max_width_100_percent:
        max_width_str = f'max-width: 100%;'
    else:
        max_width_str = f'max-width: {max_width}px;'
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{
                {max_width_str}
                padding-top: {padding_top}rem;
                padding-right: {padding_right}rem;
                padding-left: {padding_left}rem;
                padding-bottom: {padding_bottom}rem;
            }}
            .reportview-container .main {{
                color: {color};
                background-color: {background_color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_title_bar():
    logo_path = "data/pathforge-logo-final.png"  # Replace with the actual path to your logo file
    logo_base64 = get_base64_of_bin_file(logo_path)

    st.markdown(
        f"""
        <style>
            .title-bar {{
                display: flex;
                align-items: center;
                background-color: #e0e0e0;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .title-bar img {{
                height: 40px;
                margin-right: 15px;
            }}
            .title-bar h1 {{
                font-size: 22px;
                color: #333333;
                margin: 0;
            }}
        </style>
        <div class="title-bar">
            <img src="data:image/png;base64,{logo_base64}" alt="PathForge Logo">
            <h1>PathForge - Empowering Employee Performance, Career, Skills and Learning through AI</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

def main_app():
    st.title("PathForge Dashboard")

    tab1, tab2 = st.tabs(["Q&A Chatbot", "Self-Appraisal Generator"])

    with tab1:
        st.header("Q&A Chatbot")
        query = st.text_input("Enter your question:")

        show_full_response = st.checkbox("Show full response (debug)", value=False)

        if st.button("Ask", key="ask_button"):
            if not query.strip():  # Check if query is empty or just whitespace
                st.error("Please enter a question before clicking 'Ask'.")
            else:
                # Initialize data
                index = ingest_data(st.session_state.recreate_index)
                if index is None:
                    st.error("Failed to initialize the index. Please check the logs and try again.")
                    return

                llm = get_llm(st.session_state.llm_choice)
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
            with st.spinner("Generating self-appraisal..."):
                appraisal = create_self_appraisal(st.session_state.llm_choice, email)
            pretty_print_appraisal(appraisal)

def setup_streamlit_ui():
    st.set_page_config(page_title="PathForge", layout="wide")

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

    set_page_container_style()
    set_title_bar()

    if 'user' in st.session_state:
        # Sidebar (only shown when user is logged in)
        with st.sidebar:
            st.write(f"Welcome, {st.session_state.user.email}")
            st.markdown("---")  # Add a horizontal line for visual separation

            st.header("Settings")
            llm_choice = st.selectbox("Choose LLM", ["OpenAI", "Anthropic"])
            st.session_state.llm_choice = llm_choice

            # Add RECREATE_INDEX setting
            recreate_index = st.checkbox("Recreate Index", value=False, help="If checked, the index will be recreated on the next query. This may take some time.")
            st.session_state.recreate_index = recreate_index

            st.markdown("---")  # Add another horizontal line for visual separation

            if st.button("Logout", key="logout_button"):
                del st.session_state.user
                st.rerun()

        # Main content for logged-in users
        main_app()
    else:
        # Login/Signup pages (no sidebar)
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login_page()
        with tab2:
            signup_page()

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
