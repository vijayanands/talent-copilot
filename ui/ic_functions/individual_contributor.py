import json
import os
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from helpers import import_env

from functions.learning_resource_finder import find_learning_resources
from functions.self_appraisal import create_self_appraisal
from helpers.ingestion import answer_question, ingest_data
from models.models import LinkedInProfileInfo, get_user_skills, update_user_skills
from ui.ic_functions.career import career_section
from ui.ic_functions.learning import (learning_dashboard)
from ui.ic_functions.productivity import productivity_tab
from ui.ic_functions.skills_manager import initialize_skills


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
            st.session_state.appraisal = create_self_appraisal(user_email)

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


def add_skill():
    st.subheader("Add New Skill")
    new_skill = st.text_input("Skill Name")
    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }
    proficiency = st.select_slider(
        "Proficiency",
        options=list(proficiency_scale.keys()),
        format_func=lambda x: proficiency_scale[x]
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Skill"):
            if new_skill and new_skill not in st.session_state.user_skills:
                st.session_state.user_skills[new_skill] = proficiency
                if update_user_skills(st.session_state.user.id, st.session_state.user_skills):
                    st.success(f"Skill '{new_skill}' added successfully!")
                    st.session_state.add_skill_mode = False
                    st.rerun()
                else:
                    st.error("Failed to update skills. Please try again.")
            else:
                st.error("Please enter a unique skill name.")
    with col2:
        if st.button("Cancel"):
            st.session_state.add_skill_mode = False
            st.rerun()


def edit_skills():
    st.subheader("Edit Skills")

    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }

    edited_skills = {}
    for skill, proficiency in st.session_state.user_skills.items():
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{skill}**")
        with col2:
            new_proficiency = st.select_slider(
                f"Proficiency for {skill}",
                options=list(proficiency_scale.keys()),
                value=proficiency,
                key=f"edit_{skill}",
                format_func=lambda x: proficiency_scale[x]
            )
        edited_skills[skill] = new_proficiency

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes"):
            st.session_state.user_skills = edited_skills
            if update_user_skills(st.session_state.user.id, st.session_state.user_skills):
                st.success("Skills updated successfully!")
                st.session_state.skills_edit_mode = False
                st.rerun()
            else:
                st.error("Failed to update skills. Please try again.")
    with col2:
        if st.button("Cancel"):
            st.session_state.skills_edit_mode = False
            st.rerun()


def display_skills():
    st.subheader("My Skills")
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = get_user_skills(st.session_state.user.id)
    if "skills_edit_mode" not in st.session_state:
        st.session_state.skills_edit_mode = False
    if "add_skill_mode" not in st.session_state:
        st.session_state.add_skill_mode = False
    if "selected_skill_for_improvement" not in st.session_state:
        st.session_state.selected_skill_for_improvement = None

    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }

    if not st.session_state.skills_edit_mode and not st.session_state.add_skill_mode:
        # Add Skill and Edit Skills buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Skill"):
                st.session_state.add_skill_mode = True
                st.session_state.skills_edit_mode = False
                st.rerun()
        with col2:
            if st.button("Edit Skills"):
                st.session_state.skills_edit_mode = True
                st.session_state.add_skill_mode = False
                st.rerun()

        st.markdown("---")  # Add a horizontal line for visual separation

    if st.session_state.add_skill_mode:
        add_skill()
    elif st.session_state.skills_edit_mode:
        edit_skills()
    else:
        for skill, proficiency in st.session_state.user_skills.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{skill}:** {proficiency_scale[proficiency]}")
            with col3:
                if st.button("Improve", key=f"improve_{skill}"):
                    st.session_state.selected_skill_for_improvement = skill
                    st.rerun()
            with col4:
                if st.button("Remove", key=f"remove_{skill}"):
                    del st.session_state.user_skills[skill]
                    if update_user_skills(st.session_state.user.id, st.session_state.user_skills):
                        st.success(f"Skill '{skill}' removed successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to remove skill. Please try again.")

    if st.session_state.selected_skill_for_improvement:
        st.subheader(f"Learning Opportunities for {st.session_state.selected_skill_for_improvement}")
        with st.spinner(f"Finding learning resources for {st.session_state.selected_skill_for_improvement}..."):
            learning_resources = find_learning_resources([st.session_state.selected_skill_for_improvement])
        st.markdown(learning_resources)

def individual_contributor_dashboard_conversational(is_manager):
    initialize_skills()

    if "current_view" not in st.session_state:
        st.session_state.current_view = "main"

    if st.session_state.current_view != "main":
        if st.button("Back to Dashboard", key=f"back_{st.session_state.current_view}"):
            st.session_state.current_view = "main"
            st.session_state.selected_skill_for_improvement = None
            st.session_state.add_skill_mode = False
            st.session_state.skills_edit_mode = False
            st.rerun()

    if st.session_state.current_view == "main":
        prompt_options = [
            "Select an action",
            "Generate a self appraisal for me",
            "Show me the endorsements I have",
            "I would like to manage my skills",
            "Show me my current career trajectory information",
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
                "I would like to manage my skills": "skills",
                "Show me my current career trajectory information": "career",
                "I would like to manage my learning opportunities": "learning",
                "I would like to get a picture of my productivity": "productivity",
            }

            if is_manager:
                prompt_map["Show me productivity stats for my employees"] = (
                    "employee_productivity"
                )

            st.session_state.current_view = prompt_map.get(selected_prompt, selected_prompt)
            st.rerun()

        return selected_prompt  # Return the selected action

    elif st.session_state.current_view == "self_appraisal":
        perform_self_appraisal()
    elif st.session_state.current_view == "endorsements":
        display_endorsements(st.session_state.user.id)
    elif st.session_state.current_view == "learning":
        learning_dashboard()
    elif st.session_state.current_view == "career":
        career_section()
    elif st.session_state.current_view == "skills":
        display_skills()
    elif st.session_state.current_view == "productivity":
        productivity_tab()
    elif st.session_state.current_view == "employee_productivity":
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

    return st.session_state.current_view  # Return the current view for all cases