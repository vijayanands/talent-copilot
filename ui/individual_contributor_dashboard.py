import json
from functions.self_appraisal import create_self_appraisal
from helpers.get_llm import get_llm
from helpers.ingestion import ingest_data
from models.models import LinkedInProfileInfo
from ui.career import career_section
from ui.learning_dashboard import learning_dashboard
import streamlit as st

from ui.productivity import productivity_tab
from ui.skills_section import skills_section


def ask(llm, query, index):
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    return response, response.response  # Return both full response and text


def reset_performance_management():
    if "appraisal" in st.session_state:
        del st.session_state.appraisal
    st.session_state.reset_appraisal = True


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

    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("Self-Appraisal")

    with col2:
        st.button(
            "Reset", on_click=reset_performance_management, key="reset_performance"
        )

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

def update_performance_page():
    st.session_state.performance_page = st.session_state.performance_selector

def perform_self_appraisal():
    if (
            "reset_appraisal" in st.session_state
            and st.session_state.reset_appraisal
    ):
        if "appraisal" in st.session_state:
            del st.session_state.appraisal
        del st.session_state.reset_appraisal

    if st.button("Generate Self-Appraisal", key="generate_button"):
        user_email = st.session_state.user.email
        with st.spinner(f"Generating self-appraisal for {user_email} ..."):
            st.session_state.appraisal = create_self_appraisal(
                st.session_state.llm_choice, user_email
            )

    if "appraisal" in st.session_state:
        pretty_print_appraisal(st.session_state.appraisal)
        st.button(
            "Reset",
            on_click=reset_performance_management,
            key="reset_performance",
        )

def display_endorsements(user_id):
    endorsements = LinkedInProfileInfo.display_endorsements(user_id)
    if endorsements:
        st.subheader("LinkedIn Endorsements")
        for endorsement in endorsements:
            with st.expander(f"Endorsement from {endorsement['endorser']}"):
                st.write(endorsement['text'])
    else:
        st.info("No endorsements found in your LinkedIn profile. Make sure your LinkedIn profile is up to date and linked to your account.")


def performance_management_tab():
    # Initialize the performance management page in session state if it doesn't exist
    if "performance_page" not in st.session_state:
        st.session_state.performance_page = "Self-Appraisal"

    st.selectbox(
        "",  # Empty label to hide the heading
        options=["Self-Appraisal", "Endorsements", "Career", "Other Performance Tools"],
        index=["Self-Appraisal", "Endorsements", "Career", "Other Performance Tools"].index(
            st.session_state.performance_page),
        key="performance_selector",
        on_change=update_performance_page
    )

    if st.session_state.performance_page == "Self-Appraisal":
        perform_self_appraisal()
    elif st.session_state.performance_page == "Endorsements":
        display_endorsements(st.session_state.user.id)
    elif st.session_state.performance_page == "Career":
        career_section()  # Call the new career section
    else:
        st.write("This section is under development. Stay tuned for more performance management tools!")

def update_skills_learning_dev_page():
    st.session_state.skills_learning_dev_page = st.session_state.skills_learning_dev_selector

def skills_learning_development_tab():
    # Initialize the skills_learning_dev page in session state if it doesn't exist
    if "skills_learning_dev_page" not in st.session_state:
        st.session_state.skills_learning_dev_page = "My Skills"

    # Selectbox for choosing the sub-page
    st.selectbox(
        "",  # Empty label to hide the heading
        options=["My Skills", "Learning Recommendations"],
        index=["My Skills", "Learning Recommendations"].index(st.session_state.skills_learning_dev_page),
        key="skills_learning_dev_selector",
        on_change=update_skills_learning_dev_page
    )

    if st.session_state.skills_learning_dev_page == "My Skills":
        skills_section()
    else:  # Learning Recommendations
        learning_dashboard()


def q_and_a_tab():
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

def individual_contributor_dashboard():
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Performance Management",
            "Skills, Learning and Development",
            "Productivity",
            "Q&A Chatbot",
        ]
    )

    with tab1:
        performance_management_tab()

    with tab2:
        skills_learning_development_tab()

    with tab3:
        productivity_tab()  # Use the imported productivity_tab function

    with tab4:
        q_and_a_tab()