import base64
import json
import os
from typing import List

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import download_loader
from llama_index.core.schema import Document
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI

from functions.self_appraisal import create_self_appraisal
from helpers.ingestion import ingest_data
from manager_dashboard import manager_dashboard
from models.models import verify_current_password, register_user, verify_login, check_password_match, \
    update_user_profile, change_user_password, is_password_valid, get_user_skills, engine, create_tables_if_not_exist, \
    update_user_profile, update_user_skills

load_dotenv()

# Check if table exists, create only if it doesn't

create_tables_if_not_exist(engine)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

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

    # Initialize session state variables
    if "signup_password_match_error" not in st.session_state:
        st.session_state.signup_password_match_error = ""

    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name*", key="signup_first_name")
        email = st.text_input("Email*", key="signup_email")
        password = st.text_input(
            "Password*",
            type="password",
            key="signup_password",
            on_change=check_password_match,
            args=(
                "signup_password",
                "signup_confirm_password",
                "signup_password_match_error",
            ),
        )
        confirm_password = st.text_input(
            "Confirm Password*",
            type="password",
            key="signup_confirm_password",
            on_change=check_password_match,
            args=(
                "signup_password",
                "signup_confirm_password",
                "signup_password_match_error",
            ),
        )
        st.caption(
            "Password must be at least 8 characters long, contain at least one number and one symbol."
        )

        # Display password match error if it exists
        if st.session_state.signup_password_match_error:
            st.error(st.session_state.signup_password_match_error)

        is_manager = st.checkbox("I am a people manager", key="signup_is_manager")

    with col2:
        last_name = st.text_input("Last Name*", key="signup_last_name")
        address = st.text_input("Address (optional)", key="signup_address")
        phone = st.text_input("Phone (optional)", key="signup_phone")
        linkedin_profile = st.text_input(
            "LinkedIn Profile (optional)", key="signup_linkedin"
        )

    if st.button("Sign Up", key="signup_button"):
        if not first_name or not last_name:
            st.error("First name and last name are required.")
        elif not is_password_valid(st.session_state.signup_password):
            st.error(
                "Password does not meet the requirements. Please ensure it's at least 8 characters long, contains at least one number and one symbol."
            )
        elif (
            st.session_state.signup_password != st.session_state.signup_confirm_password
        ):
            st.error("Passwords do not match. Please try again.")
        else:
            try:
                register_user(
                    email,
                    st.session_state.signup_password,
                    is_manager,
                    linkedin_profile,
                    first_name,
                    last_name,
                    address,
                    phone,
                )
                st.success("Account created successfully! Please log in.")
                # Clear the form after successful signup
                for key in st.session_state.keys():
                    if key.startswith("signup_"):
                        del st.session_state[key]
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")


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
        unsafe_allow_html=True,
    )


def account_page():
    st.header("Account")

    user = st.session_state.user

    # Create tabs for Profile Information and Change Password
    profile_tab, password_tab = st.tabs(["Profile Information", "Change Password"])

    with profile_tab:
        st.subheader("Profile Information")

        # Initialize session state for edit mode if not exists
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        # Edit button with pencil icon
        edit_button = st.button("✏️ Edit")

        if edit_button:
            st.session_state.edit_mode = not st.session_state.edit_mode

        if st.session_state.edit_mode:
            # Edit mode: show editable fields
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=user.first_name)
                last_name = st.text_input("Last Name", value=user.last_name)
                address = st.text_input("Address", value=user.address)
            with col2:
                phone = st.text_input("Phone Number", value=user.phone)
                linkedin_profile = st.text_input(
                    "LinkedIn Profile URL", value=user.linkedin_profile
                )

            if st.button("Update Profile"):
                # Prepare a dictionary of changed fields
                updates = {}
                if first_name != user.first_name:
                    updates["first_name"] = first_name
                if last_name != user.last_name:
                    updates["last_name"] = last_name
                if address != user.address:
                    updates["address"] = address
                if phone != user.phone:
                    updates["phone"] = phone
                if linkedin_profile != user.linkedin_profile:
                    updates["linkedin_profile"] = linkedin_profile

                if updates:
                    updated_user = update_user_profile(user.id, **updates)
                    if updated_user:
                        st.success("Profile updated successfully!")
                        st.session_state.user = updated_user  # Update the session state with the new user data
                        st.session_state.edit_mode = False  # Exit edit mode
                        st.rerun()  # Rerun to show updated profile
                    else:
                        st.error("Failed to update profile. Please try again.")
                else:
                    st.info("No changes detected in the profile.")
        else:
            # Display mode: show non-editable fields
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**First Name:** {user.first_name}")
                st.write(f"**Last Name:** {user.last_name}")
                st.write(f"**Address:** {user.address or 'Not provided'}")
            with col2:
                st.write(f"**Phone Number:** {user.phone or 'Not provided'}")
                st.write(
                    f"**LinkedIn Profile URL:** {user.linkedin_profile or 'Not provided'}"
                )

    with password_tab:
        st.subheader("Change Password")

        # Initialize session state variables if not exists
        if "change_password_match_error" not in st.session_state:
            st.session_state.change_password_match_error = ""
        if "current_password_error" not in st.session_state:
            st.session_state.current_password_error = ""
        if "new_password_error" not in st.session_state:
            st.session_state.new_password_error = ""

        current_password = st.text_input(
            "Current Password", type="password", key="current_password"
        )
        new_password = st.text_input(
            "New Password",
            type="password",
            key="new_password",
            on_change=check_password_match,
            args=(
                "new_password",
                "confirm_new_password",
                "change_password_match_error",
            ),
        )
        confirm_new_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="confirm_new_password",
            on_change=check_password_match,
            args=(
                "new_password",
                "confirm_new_password",
                "change_password_match_error",
            ),
        )

        # Display password match error if it exists
        if st.session_state.change_password_match_error:
            st.error(st.session_state.change_password_match_error)

        # Display current password error if it exists
        if st.session_state.current_password_error:
            st.error(st.session_state.current_password_error)

        # Display new password error if it exists
        if st.session_state.new_password_error:
            st.error(st.session_state.new_password_error)

        if st.button("Change Password"):
            if not current_password or not new_password or not confirm_new_password:
                st.error("Please fill in all password fields.")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match.")
            elif not is_password_valid(new_password):
                st.error(
                    "New password does not meet the requirements. Please ensure it's at least 8 characters long, contains at least one number and one symbol."
                )
            else:
                # Verify current password
                if not verify_current_password(user.id, current_password):
                    st.session_state.current_password_error = (
                        "Current password is incorrect."
                    )
                    st.error("Current password is incorrect.")
                elif current_password == new_password:
                    st.session_state.new_password_error = (
                        "New password must be different from the current password."
                    )
                    st.error(
                        "New password must be different from the current password."
                    )
                else:
                    if change_user_password(user.id, new_password):
                        st.success(
                            "Password changed successfully! You will now be logged out."
                        )
                        st.session_state.logout_after_password_change = True
                        st.rerun()
                    else:
                        st.error("Failed to change password. Please try again.")


def skills_section():
    st.subheader("My Skills")

    # Initialize session state variables
    if 'skills_edit_mode' not in st.session_state:
        st.session_state.skills_edit_mode = False
    if 'user_skills' not in st.session_state:
        st.session_state.user_skills = get_user_skills(st.session_state.user.id)
    if 'show_add_skill_form' not in st.session_state:
        st.session_state.show_add_skill_form = False

    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }

    def toggle_edit_mode():
        st.session_state.skills_edit_mode = not st.session_state.skills_edit_mode
        st.session_state.show_add_skill_form = False

    def delete_skill(skill):
        del st.session_state.user_skills[skill]

    def save_skills():
        # Implement the logic to save skills to the database
        # For now, we'll just print the skills and exit edit mode
        print("Saving skills:", st.session_state.user_skills)
        st.session_state.skills_edit_mode = False
        st.session_state.show_add_skill_form = False

    def show_add_skill_form():
        st.session_state.show_add_skill_form = True

    def add_new_skill(name, proficiency):
        if name and name not in st.session_state.user_skills:
            st.session_state.user_skills[name] = proficiency
            st.session_state.show_add_skill_form = False
        else:
            st.error("Please enter a unique skill name.")

    # Edit button above the skills view
    if not st.session_state.skills_edit_mode:
        st.button("Edit", on_click=toggle_edit_mode)

    if not st.session_state.skills_edit_mode:
        # View mode
        if st.session_state.user_skills:
            for skill, proficiency in st.session_state.user_skills.items():
                st.write(f"**{skill}:** {proficiency_scale[int(proficiency)]}")
        else:
            st.info("No skills found. Click 'Edit' to add your skills.")
    else:
        # Edit mode
        st.write("Edit your skills:")

        # Add new skill button
        col1, col2 = st.columns([3, 1])
        with col2:
            st.button("Add Skill", on_click=show_add_skill_form)

        # New skill form
        if st.session_state.show_add_skill_form:
            with st.form("new_skill_form"):
                new_skill_name = st.text_input("Skill Name")
                new_skill_proficiency = st.radio(
                    "Proficiency",
                    options=list(range(1, 6)),
                    format_func=lambda x: proficiency_scale[x],
                    horizontal=True
                )
                submit_button = st.form_submit_button("Add")
                if submit_button:
                    add_new_skill(new_skill_name, new_skill_proficiency)

        # Existing skills
        for skill, proficiency in st.session_state.user_skills.items():
            col1, col2, col3 = st.columns([3, 6, 1])
            with col1:
                st.write(skill)
            with col2:
                st.session_state.user_skills[skill] = st.radio(
                    f"Proficiency: {skill}",
                    options=list(range(1, 6)),
                    format_func=lambda x: proficiency_scale[x],
                    index=proficiency - 1,
                    key=f"proficiency_{skill}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
            with col3:
                st.button("Delete", key=f"delete_{skill}", on_click=delete_skill, args=(skill,))

        # Save button
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            st.button("Save", on_click=save_skills)
            
def my_assistant_dashboard():
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Performance Management",
        "Learning & Development",
        "Skills",
        "Jobs/Career",
        "Q&A Chatbot",
    ])

    with tab1:
        st.header("Performance Management")
        performance_subtab1, performance_subtab2 = st.tabs(
            ["Self-Appraisal", "Other Performance Tools"]
        )

        with performance_subtab1:
            st.subheader("Self-Appraisal Generator")
            if st.button("Generate Self-Appraisal", key="generate_button"):
                user_email = st.session_state.user.email
                with st.spinner(f"Generating self-appraisal for {user_email} ..."):
                    appraisal = create_self_appraisal(
                        st.session_state.llm_choice, user_email
                    )
                pretty_print_appraisal(appraisal)

        with performance_subtab2:
            st.write(
                "This section is under development. Here you will find additional performance management tools."
            )
            st.info(
                "Coming soon: Goal setting, performance reviews, and feedback mechanisms."
            )

    with tab2:
        st.header("Learning & Development")
        st.write(
            "This section is under development. Here you will be able to track your learning progress and find development opportunities."
        )
        st.info(
            "Coming soon: Course recommendations, learning paths, and skill gap analysis."
        )

    with tab3:
        st.header("Skills")
        skills_subtab1, skills_subtab2 = st.tabs(["My Skills", "Endorsements"])
        with skills_subtab1:
            skills_section()
        with skills_subtab2:
            st.subheader("Endorsements")
            st.info("This feature is coming soon. Here you'll be able to view and manage skill endorsements.")

    with tab4:
        st.header("Jobs/Career")
        st.write(
            "This section is under development. Here you will be able to explore career opportunities and plan your career path."
        )
        st.info(
            "Coming soon: Job recommendations, career path visualization, and mentorship opportunities."
        )

    with tab5:
        st.header("Q&A Chatbot")
        query = st.text_input("Enter your question:")

        show_full_response = st.checkbox("Show full response (debug)", value=False)

        if st.button("Ask", key="ask_button"):
            if not query.strip():
                st.error("Please enter a question before clicking 'Ask'.")
            else:
                index = ingest_data(st.session_state.recreate_index)
                if index is None:
                    st.error(
                        "Failed to initialize the index. Please check the logs and try again."
                    )
                    return

                llm = get_llm(st.session_state.llm_choice)
                with st.spinner("Generating response..."):
                    full_response, response_text = ask(llm, query, index)

                st.write("Response:")
                st.write(response_text)

                if show_full_response:
                    st.write("Full Response (Debug):")
                    st.write(full_response)


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

def show_initial_dashboard():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_page()
    with tab2:
        signup_page()


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

    if "logout_after_password_change" in st.session_state and st.session_state.logout_after_password_change:
        del st.session_state.user
        del st.session_state.logout_after_password_change
        st.info("You have been logged out due to a password change. Please log in with your new password.")
        show_initial_dashboard()
    elif "user" in st.session_state:
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

