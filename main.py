import streamlit as st
from dotenv import load_dotenv

from models.models import create_tables_if_not_exist, engine
from style import set_page_container_style, set_page_style
from ui.account.account import account_page
from ui.dashboard import dashboard
from ui.enterprise_admin import enterprise_admin_dashboard
from ui.login_signup import login_page, logout, signup_page
from ui.side_bar import setup_sidebar
from ui.title_bar import set_title_bar

load_dotenv()

create_tables_if_not_exist(engine)


def main_app():
    is_manager = st.session_state.user.is_manager
    is_enterprise_admin = st.session_state.user.is_enterprise_admin

    if is_enterprise_admin:
        enterprise_admin_dashboard()
    else:
        dashboard()


def show_initial_dashboard():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_page()
    with tab2:
        signup_page()


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
        logout()
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
