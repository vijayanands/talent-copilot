import json
import os
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from functions.learning_resource_finder import find_learning_resources
from functions.self_appraisal import create_self_appraisal
from helpers.get_llm import get_llm
from helpers.ingestion import answer_question, ingest_data
from models.models import LinkedInProfileInfo, get_user_skills
from ui.ic_functions.career import career_section
from ui.ic_functions.learning import (learning_dashboard,
                                      reset_learning_dashboard)
from ui.ic_functions.productivity import productivity_tab
from ui.ic_functions.skills_manager import initialize_skills
from ui.ic_functions.skills_section import skills_section

load_dotenv()


def ask(llm, query, index):
    enhanced_query = f"Based on the jira, github and the confluence data in the embedded json data, please answer my {query}"
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(enhanced_query)
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
            "Reset",
            on_click=reset_performance_management,
            key="reset_performance_header",
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


def perform_self_appraisal():
    if "reset_appraisal" in st.session_state and st.session_state.reset_appraisal:
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
            key="reset_performance_bottom",
        )


def display_endorsements(user_id):
    st.subheader("LinkedIn Endorsements")
    endorsements = LinkedInProfileInfo.display_endorsements(user_id)
    if endorsements:
        for endorsement in endorsements:
            with st.expander(f"Endorsement from {endorsement['endorser']}"):
                st.write(endorsement["text"])
    else:
        st.info(
            "No endorsements found in your LinkedIn profile. Make sure your LinkedIn profile is up to date and linked to your account."
        )


def update_skills_learning_dev_page():
    st.session_state.skills_learning_dev_page = (
        st.session_state.skills_learning_dev_selector
    )


def skills_learning_development_tab():
    # Initialize the skills_learning_dev page in session state if it doesn't exist
    if "skills_learning_dev_page" not in st.session_state:
        st.session_state.skills_learning_dev_page = "My Skills"

    # Selectbox for choosing the sub-page
    st.selectbox(
        "",  # Empty label to hide the heading
        options=["My Skills", "Learning Recommendations"],
        index=["My Skills", "Learning Recommendations"].index(
            st.session_state.skills_learning_dev_page
        ),
        key="skills_learning_dev_selector",
        on_change=update_skills_learning_dev_page,
    )

    if st.session_state.skills_learning_dev_page == "My Skills":
        skills_section()
    else:  # Learning Recommendations
        learning_dashboard()


def load_qa_data():
    with st.spinner("Ingesting data... This may take a moment."):
        index = ingest_data()
        if index is None:
            st.error(
                "Failed to initialize the index. Please check the logs and try again."
            )
            return None
        return index


def q_and_a_tab():
    if "qa_index" not in st.session_state:
        st.session_state.qa_index = load_qa_data()

    if st.session_state.qa_index is None:
        return

    # Initialize session state for storing the last question and answer
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = ""

    # Get the logged-in user's email
    user_email = st.session_state.user.email

    query = st.text_input("Enter your question:", key="query_input")
    show_full_response = os.getenv("SHOW_CHATBOT_DEBUG_LOG", "false").lower() == "true"

    if st.button("Ask", key="ask_button"):
        if not query.strip():
            st.error("Please enter a question before clicking 'Ask'.")
        else:
            llm = get_llm(st.session_state.llm_choice)
            with st.spinner("Generating Answer..."):
                try:
                    response = answer_question(
                        st.session_state.qa_index, user_email, query
                    )

                    # Store the question and answer in session state
                    st.session_state.last_question = query
                    st.session_state.last_answer = response

                except Exception as e:
                    st.error(
                        f"An error occurred while processing your question: {str(e)}"
                    )

    # Display the last question and answer if they exist
    if st.session_state.last_question:
        st.subheader("Question:")
        st.write(st.session_state.last_question)
        st.subheader("Answer:")
        st.write(st.session_state.last_answer)

        if show_full_response:
            st.write("Full Response (Debug):")
            st.write(response)  # This will show the full response object if available

    # Add a note about the context of the answers
    st.info(f"Answers are based on the data available for {user_email}.")


def conversational_ai_dashboard():
    st.markdown(
        """
        <script>
            const { createRoot } = ReactDOM;
            const rootElement = document.getElementById('conversational-ai-dashboard');
            const root = createRoot(rootElement);
            root.render(
                React.createElement(ConversationalAIDashboard, {
                    user: {user},
                    llm_choice: '{llm_choice}'
                })
            );
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.components.v1.html(
        """
        <div id="conversational-ai-dashboard"></div>
        """
    )


def handle_prompt(prompt, user_email):
    if prompt == "self_appraisal":
        return "self_appraisal"  # Return the view name instead of a message
    elif prompt == "endorsements":
        return "endorsements"
    elif prompt == "career":
        return career_section()
    elif prompt == "skills":
        return "skills"
    elif prompt == "learning":
        return "learning"
    elif prompt == "productivity":
        return productivity_tab()
    elif prompt == "employee_productivity":
        return "employee_productivity"
    elif prompt.startswith("improve_skill:"):
        skill = prompt.split(":")[1]
        resources = find_learning_resources([skill])
        return resources
    else:
        return f"Error: Unknown prompt '{prompt}'."


def display_skills():
    st.subheader("My Skills")
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = get_user_skills(st.session_state.user.id)
    if "skills_edit_mode" not in st.session_state:
        st.session_state.skills_edit_mode = False

    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert",
    }

    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.skills_edit_mode:
            if st.button("Edit Skills"):
                st.session_state.skills_edit_mode = True
                st.rerun()
        else:
            if st.button("Exit Edit Mode"):
                st.session_state.skills_edit_mode = False
                st.rerun()
    with col2:
        if st.button("Add New Skill"):
            st.session_state.current_view = "add_skill"
            st.rerun()

    if st.session_state.skills_edit_mode:
        for skill, proficiency in st.session_state.user_skills.items():
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(skill)
            with col2:
                new_proficiency = st.selectbox(
                    f"Proficiency for {skill}",
                    options=list(range(1, 6)),
                    format_func=lambda x: proficiency_scale[x],
                    key=f"proficiency_{skill}",
                    index=proficiency - 1,
                )
                st.session_state.user_skills[skill] = new_proficiency
            with col3:
                if st.button("Delete", key=f"delete_{skill}"):
                    del st.session_state.user_skills[skill]
                    st.rerun()

        if st.button("Save Changes"):
            # Here you would typically save the changes to your database
            st.success("Skills updated successfully!")
            st.session_state.skills_edit_mode = False
            st.rerun()
    else:
        if st.session_state.user_skills:
            for skill, proficiency in st.session_state.user_skills.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{skill}:** {proficiency_scale[int(proficiency)]}")
                with col2:
                    if st.button("Improve", key=f"improve_{skill}"):
                        st.session_state.current_view = "improve_skill"
                        st.session_state.skill_to_improve = skill
                        st.rerun()
        else:
            st.info("No skills found. Click 'Add New Skill' to add your skills.")


def add_skill():
    st.subheader("Add New Skill")
    new_skill = st.text_input("Skill Name")
    proficiency = st.select_slider(
        "Proficiency",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: [
            "Novice",
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert",
        ][x - 1],
    )
    if st.button("Add Skill"):
        if new_skill and new_skill not in st.session_state.user_skills:
            st.session_state.user_skills[new_skill] = proficiency
            st.success(f"Skill '{new_skill}' added successfully!")
            st.session_state.current_view = "skills"
            st.rerun()
        else:
            st.error("Please enter a unique skill name.")


# New functions for manager dashboard functionality
def get_dummy_employees():
    return [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com"},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com"},
        {"id": 4, "name": "Diana Ross", "email": "diana@example.com"},
    ]


def get_employee_jira_data(employee_id):
    date_range = pd.date_range(end=datetime.now(), periods=30)
    data = {
        "date": date_range,
        "issues_created": [random.randint(0, 5) for _ in range(30)],
        "issues_resolved": [random.randint(0, 4) for _ in range(30)],
    }
    return pd.DataFrame(data)


def get_employee_confluence_data(employee_id):
    date_range = pd.date_range(end=datetime.now(), periods=30)
    data = {
        "date": date_range,
        "pages_created": [random.randint(0, 2) for _ in range(30)],
        "pages_edited": [random.randint(0, 3) for _ in range(30)],
    }
    return pd.DataFrame(data)


def get_employee_github_data(employee_id):
    date_range = pd.date_range(end=datetime.now(), periods=30)
    data = {
        "date": date_range,
        "commits": [random.randint(0, 10) for _ in range(30)],
        "pull_requests": [random.randint(0, 2) for _ in range(30)],
    }
    return pd.DataFrame(data)


def predict_productivity(jira_data, confluence_data, github_data):
    total_jira_issues = jira_data["issues_resolved"].sum()
    total_confluence_edits = confluence_data["pages_edited"].sum()
    total_github_commits = github_data["commits"].sum()

    productivity_score = (
        total_jira_issues * 0.4
        + total_confluence_edits * 0.3
        + total_github_commits * 0.3
    )

    return min(productivity_score / 100, 1.0)


def display_employee_stats(employee):
    st.subheader(f"Statistics for {employee['name']}")

    jira_data = get_employee_jira_data(employee["id"])
    confluence_data = get_employee_confluence_data(employee["id"])
    github_data = get_employee_github_data(employee["id"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Jira Issues Resolved", jira_data["issues_resolved"].sum())
    with col2:
        st.metric(
            "Total Confluence Pages Edited", confluence_data["pages_edited"].sum()
        )
    with col3:
        st.metric("Total GitHub Commits", github_data["commits"].sum())

    fig_jira = px.line(
        jira_data,
        x="date",
        y=["issues_created", "issues_resolved"],
        title="Jira Activity",
    )
    st.plotly_chart(fig_jira)

    fig_confluence = px.line(
        confluence_data,
        x="date",
        y=["pages_created", "pages_edited"],
        title="Confluence Activity",
    )
    st.plotly_chart(fig_confluence)

    fig_github = px.line(
        github_data, x="date", y=["commits", "pull_requests"], title="GitHub Activity"
    )
    st.plotly_chart(fig_github)

    productivity = predict_productivity(jira_data, confluence_data, github_data)
    fig_productivity = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=productivity,
            title={"text": "Predicted Productivity"},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 1]},
                "steps": [
                    {"range": [0, 0.3], "color": "lightgray"},
                    {"range": [0.3, 0.7], "color": "gray"},
                    {"range": [0.7, 1], "color": "darkgray"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 0.8,
                },
            },
        )
    )
    st.plotly_chart(fig_productivity)


def individual_contributor_dashboard_conversational(is_manager):
    initialize_skills()

    if "current_view" not in st.session_state:
        st.session_state.current_view = "main"

    if st.session_state.current_view == "main":
        prompt_options = [
            "Select an action",
            "Generate a self appraisal for me",
            "Show me the endorsements I have",
            "Show me my current career trajectory information",
            "I would like to manage my skills",
            "I would like to manage my learning opportunities",
            "I would like to get a picture of my productivity",
        ]

        if is_manager:
            prompt_options.append("Show me productivity stats for my employees")

        selected_prompt = st.selectbox(
            "", prompt_options, index=0, key="action_selector"
        )

        if selected_prompt != "Select an action":
            prompt_map = {
                "Generate a self appraisal for me": "self_appraisal",
                "Show me the endorsements I have": "endorsements",
                "Show me my current career trajectory information": "career",
                "I would like to manage my skills": "skills",
                "I would like to manage my learning opportunities": "learning",
                "I would like to get a picture of my productivity": "productivity",
            }

            if is_manager:
                prompt_map["Show me productivity stats for my employees"] = (
                    "employee_productivity"
                )

            response = handle_prompt(
                prompt_map.get(selected_prompt, selected_prompt),
                st.session_state.user.email,
            )

            if response in [
                "self_appraisal",
                "endorsements",
                "learning",
                "career",
                "skills",
                "employee_productivity",
            ]:
                st.session_state.current_view = response
                st.rerun()
            else:
                st.write("Response:", response)

    elif st.session_state.current_view == "self_appraisal":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            perform_self_appraisal()

    elif st.session_state.current_view == "endorsements":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            display_endorsements(st.session_state.user.id)

    elif st.session_state.current_view == "learning":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            reset_learning_dashboard()
            st.rerun()
        else:
            learning_dashboard()

    elif st.session_state.current_view == "career":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            career_section()

    elif st.session_state.current_view == "skills":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            display_skills()

    elif st.session_state.current_view == "improve_skill":
        if st.button("Back to Skills"):
            st.session_state.current_view = "skills"
            st.rerun()
        else:
            st.subheader(f"Learning Resources for {st.session_state.skill_to_improve}")
            with st.spinner("Finding learning resources..."):
                resources = find_learning_resources([st.session_state.skill_to_improve])
                st.markdown(resources)

    elif st.session_state.current_view == "add_skill":
        if st.button("Back to Skills"):
            st.session_state.current_view = "skills"
            st.rerun()
        else:
            add_skill()

    elif st.session_state.current_view == "employee_productivity":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            if is_manager:
                employees = get_dummy_employees()
                selected_employee = st.selectbox(
                    "Select an employee",
                    options=employees,
                    format_func=lambda x: x["name"],
                )
                if selected_employee:
                    display_employee_stats(selected_employee)
            else:
                st.error("You do not have permission to view this page.")
                if st.button("Return to Dashboard"):
                    st.session_state.current_view = "main"
                    st.rerun()

    elif st.session_state.current_view == "productivity":
        if st.button("Back to Dashboard"):
            st.session_state.current_view = "main"
            st.rerun()
        else:
            productivity_tab()
