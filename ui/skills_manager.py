import streamlit as st
from models.models import get_user_skills, update_user_skills

def initialize_skills():
    if 'user_skills' not in st.session_state:
        st.session_state.user_skills = get_user_skills(st.session_state.user.id)

def get_skills():
    initialize_skills()
    return st.session_state.user_skills

def update_skills(skills):
    st.session_state.user_skills = skills
    update_user_skills(st.session_state.user.id, skills)