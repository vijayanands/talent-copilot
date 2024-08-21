import streamlit as st
from typing import List

from functions.learning_resource_finder import find_learning_resources
from models.models import get_user_skills

def learning_dashboard():
    st.header("Learning & Development")
    
    # Initialize session state variables
    if 'selected_skills' not in st.session_state:
        st.session_state.selected_skills = []
    if 'additional_keywords' not in st.session_state:
        st.session_state.additional_keywords = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Select Skills and Keywords")
        
        # Get user skills
        user_skills = get_user_skills(st.session_state.user.id)
        
        # Create checkboxes for existing skills
        for skill in user_skills:
            if st.checkbox(skill, key=f"skill_{skill}"):
                if skill not in st.session_state.selected_skills:
                    st.session_state.selected_skills.append(skill)
            elif skill in st.session_state.selected_skills:
                st.session_state.selected_skills.remove(skill)
        
        # Add new keyword
        new_keyword = st.text_input("Add a new keyword")
        if st.button("Add Keyword"):
            if new_keyword and new_keyword not in st.session_state.additional_keywords:
                st.session_state.additional_keywords.append(new_keyword)
                st.success(f"Added: {new_keyword}")
            else:
                st.warning("Please enter a unique keyword.")
    
    with col2:
        st.subheader("Selected Skills and Keywords")
        
        # Display selected skills
        if st.session_state.selected_skills:
            st.write("Selected Skills:")
            for skill in st.session_state.selected_skills:
                st.write(f"- {skill}")
        
        # Display additional keywords
        if st.session_state.additional_keywords:
            st.write("Additional Keywords:")
            for keyword in st.session_state.additional_keywords:
                st.write(f"- {keyword}")
    
    # Generate recommendations button
    if st.button("Generate Recommendations"):
        generate_recommendations()

def generate_recommendations():
    combined_list: List[str] = st.session_state.selected_skills + st.session_state.additional_keywords
    
    if not combined_list:
        st.warning("Please select at least one skill or keyword before generating recommendations.")
        return
    
    st.subheader("Learning Resources and Recommendations")
    
    with st.spinner("Generating recommendations..."):
        recommendations = find_learning_resources(combined_list)
    
    st.markdown(recommendations)

