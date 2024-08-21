import json
import streamlit as st
from functions.self_appraisal import create_self_appraisal
from helpers.get_llm import get_llm
from helpers.ingestion import ingest_data
from models.models import get_user_skills


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


def individual_contributor_dashboard():
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Performance Management",
        "Learning & Development",
        "Skills",
        "Career",
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
        learning_dashboard()

    with tab3:
        st.header("Skills")
        skills_subtab1, skills_subtab2 = st.tabs(["My Skills", "Endorsements"])
        with skills_subtab1:
            skills_section()
        with skills_subtab2:
            st.subheader("Endorsements")
            st.info("This feature is coming soon. Here you'll be able to view and manage skill endorsements.")

    with tab4:
        st.header("Career")
        st.write(
            "This section is under development. Here you will be able to explore career opportunities and plan your career path."
        )
        st.info(
            "Coming soon: Career path visualization, and mentorship opportunities."
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
