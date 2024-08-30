import base64
import os

import streamlit as st
from dotenv import load_dotenv

from models.models import create_tables_if_not_exist, engine
from style import set_page_container_style, set_page_style
from ui.account_page import account_page
from ui.enterprise_admin_dashboard import enterprise_admin_dashboard
from ui.individual_contributor_dashboard import \
    individual_contributor_dashboard
from ui.individual_contributor_dashboard_conversationsal import individual_contributor_dashboard_conversational
from ui.login_signup import login_page, signup_page
from ui.manager_dashboard import manager_dashboard

load_dotenv()

# Check if table exists, create only if it doesn't

create_tables_if_not_exist(engine)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def get_base64_of_bytes(bytes_data):
    return base64.b64encode(bytes_data).decode()


def set_title_bar():
    logo_path = "images/pathforge-logo-final.png"
    logo_base64 = get_base64_of_bin_file(logo_path)

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');

            .title-bar {{
                display: flex;
                align-items: center;
                background: linear-gradient(135deg, #2c3e50, #4ca1af);
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .title-bar img {{
                height: 50px;
                margin-right: 20px;
                filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));
            }}
            .title-bar h1 {{
                font-size: 24px;
                color: #ffffff;
                margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}
            .empower-text {{
                font-family: 'Poppins', sans-serif;
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                letter-spacing: 2px;
                margin-right: 20px;
            }}
            .highlight-blue {{
                color: #66ccff;
                font-weight: bold;
            }}
            .highlight-pink {{
                color: #ff99cc;
                font-weight: bold;
            }}
        </style>
        <div class="title-bar">
            <img src="data:image/png;base64,{logo_base64}" alt="PathForge Logo">
            <div class="empower-text">EMPOWER</div>
            <h1>
                Empowering Employee 
                <span class="highlight-pink">Productivity</span>, 
                <span class="highlight-blue">Performance</span>, 
                <span class="highlight-pink">Career</span>, 
                <span class="highlight-blue">Skills</span> and 
                <span class="highlight-pink">Learning</span>
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

def ic_dashboard():
    use_conversational_ai = os.getenv("USE_CONVERSATIONAL_AI", False)
    if use_conversational_ai.lower() == "false":
        individual_contributor_dashboard()
    else:
        individual_contributor_dashboard_conversational()

def main_app():
    is_manager = st.session_state.user.is_manager
    is_enterprise_admin = st.session_state.user.is_enterprise_admin

    if is_enterprise_admin:
        enterprise_admin_dashboard()
    elif is_manager:
        tab1, tab2 = st.tabs(["Manager Dashboard", "My Assistant"])

        with tab1:
            manager_dashboard()

        with tab2:
            ic_dashboard()
    else:
        ic_dashboard()


def show_initial_dashboard():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_page()
    with tab2:
        signup_page()


def setup_sidebar():
    with st.sidebar:
        # Create a container for the profile image
        welcome_container = st.container()
        with welcome_container:
            if st.session_state.user.profile_image:
                img_base64 = get_base64_of_bytes(st.session_state.user.profile_image)
                st.markdown(
                    f'<img src="data:image/png;base64,{img_base64}" width="50" height="50" style="border-radius: 50%;">',
                    unsafe_allow_html=True,
                )
            else:
                default_img = get_base64_of_bin_file("images/default_profile.png")
                st.markdown(
                    f'<img src="data:image/png;base64,{default_img}" width="50" height="50" style="border-radius: 50%;">',
                    unsafe_allow_html=True,
                )

        # st.markdown("---")

        # Initialize the page in session state if it doesn't exist
        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"

        # Dropdown menu using st.selectbox
        selected_page = st.selectbox(
            "",  # Empty label to hide "Menu"
            options=["Dashboard", "Account"],
            index=0 if st.session_state.page == "Dashboard" else 1,
        )

        # Update the page if a different option is selected
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()

        st.markdown("---")

        # Set values from environment variables with defaults
        st.session_state.llm_choice = os.getenv("LLM_CHOICE", "OpenAI")
        if st.button("Logout", key="logout_button"):
            del st.session_state.user
            st.rerun()

    return st.session_state.page


def setup_streamlit_ui():
    st.set_page_config(
        page_title="PathForge",
        layout="wide",
        menu_items=None,  # This removes the hamburger menu
    )

    # Hide the "Made with Streamlit" footer and other potential UI elements
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        header {visibility: hidden;}
        #stDecoration {display:none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    set_page_style()
    set_page_container_style()
    set_title_bar()

    if (
        "logout_after_password_change" in st.session_state
        and st.session_state.logout_after_password_change
    ):
        del st.session_state.user
        del st.session_state.logout_after_password_change
        st.info(
            "You have been logged out due to a password change. Please log in with your new password."
        )
        show_initial_dashboard()
    elif "user" in st.session_state:
        page = setup_sidebar()

        if page == "Dashboard":
            main_app()
        elif page == "Account":
            account_page()
    else:
        show_initial_dashboard()


# Add this at the end of your script
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
