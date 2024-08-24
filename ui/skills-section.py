import streamlit as st
from models.models import get_user_skills

def skills_section():
    st.subheader("My Skills")

    # Initialize session state variables
    if "skills_edit_mode" not in st.session_state:
        st.session_state.skills_edit_mode = False
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = get_user_skills(st.session_state.user.id)
    if "show_add_skill_form" not in st.session_state:
        st.session_state.show_add_skill_form = False

    proficiency_scale = {
        1: "Novice",
        2: "Beginner",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert",
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
                    horizontal=True,
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
                    label_visibility="collapsed",
                )
            with col3:
                st.button(
                    "Delete",
                    key=f"delete_{skill}",
                    on_click=delete_skill,
                    args=(skill,),
                )

        # Save button
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            st.button("Save", on_click=save_skills)
