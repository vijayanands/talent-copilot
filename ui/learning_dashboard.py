import streamlit as st
from typing import List
from functions.learning_resource_finder import find_learning_resources
from models.models import get_user_skills


def reset_learning_dashboard():
    if 'learning_state' in st.session_state:
        st.session_state.learning_state = {
            "selected_skills": [],
            "additional_keywords": [],
            "show_recommendations": False,
            "recommendations": ""
        }


def learning_dashboard():
    if 'learning_state' not in st.session_state:
        st.session_state.learning_state = {
            "selected_skills": [],
            "additional_keywords": [],
            "show_recommendations": False,
            "recommendations": ""
        }

    st.subheader("Learning Opportunities Dashboard")

    if not st.session_state.learning_state["show_recommendations"]:
        # Get user skills
        user_skills = get_user_skills(st.session_state.user.id)

        # Select skills
        st.session_state.learning_state["selected_skills"] = st.multiselect(
            "Select skills",
            options=user_skills,
            default=st.session_state.learning_state["selected_skills"]
        )

        # Additional keywords
        st.subheader("Additional Keywords")

        # New keyword input
        new_keyword = st.text_input("", placeholder="Enter a new keyword")

        # Add Keyword button
        if st.button("Add Keyword"):
            if new_keyword and new_keyword not in st.session_state.learning_state["additional_keywords"]:
                st.session_state.learning_state["additional_keywords"].append(new_keyword)
                st.rerun()

        # Display current combined list
        st.subheader("Current Selection")
        combined_list = (
                st.session_state.learning_state["selected_skills"] +
                st.session_state.learning_state["additional_keywords"]
        )
        if combined_list:
            st.write("Skills and keywords for recommendation:")
            for item in combined_list:
                st.write(f"- {item}")
        else:
            st.write("No skills or keywords selected yet.")

        # Generate recommendations button
        if st.button("Generate Recommendations"):
            generate_recommendations()
    else:
        show_recommendation_view()


def generate_recommendations():
    combined_list: List[str] = (
            st.session_state.learning_state["selected_skills"] +
            st.session_state.learning_state["additional_keywords"]
    )

    if not combined_list:
        st.warning(
            "Please select at least one skill or keyword before generating recommendations."
        )
        return

    with st.spinner("Generating recommendations..."):
        st.session_state.learning_state["recommendations"] = find_learning_resources(combined_list)

    st.session_state.learning_state["show_recommendations"] = True
    st.rerun()


def show_recommendation_view():
    st.subheader("Learning Recommendations")
    st.markdown(st.session_state.learning_state["recommendations"])

    if st.button("Back to Selection"):
        reset_learning_dashboard()
        st.rerun()