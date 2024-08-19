import base64

import streamlit as st
from dotenv import load_dotenv

from web.login_signup import login_page, signup_page
from web.manager_dashboard import manager_dashboard
from models.models import engine, create_tables_if_not_exist
from web.individual_contributor_dashboard import individual_contributor_dashboard
from web.account_page import account_page

load_dotenv()

# Check if table exists, create only if it doesn't

create_tables_if_not_exist(engine)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_page_style():
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

def set_page_container_style(
        max_width: int = 1100,
        max_width_100_percent: bool = False,
        padding_top: int = 1,
        padding_right: int = 10,
        padding_left: int = 10,
        padding_bottom: int = 10,
        color: str = "black",
        background_color: str = "#f0f2f6",
):
    if max_width_100_percent:
        max_width_str = f"max-width: 100%;"
    else:
        max_width_str = f"max-width: {max_width}px;"
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
    logo_path = "data/pathforge-logo-final.png"
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
        unsafe_allow_html=True,
    )

def my_assistant_dashboard():
    individual_contributor_dashboard()

def main_app():
    st.title("PathForge Dashboard")

    is_manager = st.session_state.user.is_manager

    if is_manager:
        tab1, tab2 = st.tabs(["Manager Dashboard", "My Assistant"])

        with tab1:
            manager_dashboard()

        with tab2:
            my_assistant_dashboard()
    else:
        my_assistant_dashboard()

def setup_sidebar():
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.user.email}")
        st.markdown("---")

        page = st.radio("Navigation", ["Dashboard", "Account"])

        st.markdown("---")

        st.header("Settings")
        llm_choice = st.selectbox("Choose LLM", ["OpenAI", "Anthropic"])
        st.session_state.llm_choice = llm_choice

        recreate_index = st.checkbox(
            "Recreate Index",
            value=False,
            help="If checked, the index will be recreated on the next query. This may take some time.",
        )
        st.session_state.recreate_index = recreate_index

        st.markdown("---")

        if st.button("Logout", key="logout_button"):
            del st.session_state.user
            st.rerun()

    return page

def show_initial_dashboard():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_page()
    with tab2:
        signup_page()

def setup_streamlit_ui():
    st.set_page_config(page_title="PathForge", layout="wide")

    set_page_style()
    set_page_container_style()
    set_title_bar()

    if "logout_after_password_change" in st.session_state and st.session_state.logout_after_password_change:
        del st.session_state.user
        del st.session_state.logout_after_password_change
        st.info("You have been logged out due to a password change. Please log in with your new password.")
        show_initial_dashboard()
    elif "user" in st.session_state:
        page = setup_sidebar()

        if page == "Dashboard":
            main_app()
        elif page == "Account":
            account_page()
    else:
        show_initial_dashboard()

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

