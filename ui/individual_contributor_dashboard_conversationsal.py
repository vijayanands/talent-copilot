import json
import os

import streamlit as st
from dotenv import load_dotenv

from functions.learning_resource_finder import find_learning_resources
from functions.self_appraisal import create_self_appraisal
from helpers.get_llm import get_llm
from helpers.ingestion import ingest_data, answer_question
from models.models import LinkedInProfileInfo, get_user_skills
from ui.career import career_section
from ui.learning_dashboard import learning_dashboard, reset_learning_dashboard
from ui.productivity import productivity_tab
from ui.skills_section import skills_section

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
    endorsements = LinkedInProfileInfo.display_endorsements(user_id)
    if endorsements:
        st.subheader("LinkedIn Endorsements")
        for endorsement in endorsements:
            with st.expander(f"Endorsement from {endorsement['endorser']}"):
                st.write(endorsement["text"])
    else:
        st.info(
            "No endorsements found in your LinkedIn profile. Make sure your LinkedIn profile is up to date and linked to your account."
        )


def update_performance_page():
    st.session_state.performance_page = st.session_state.performance_selector


def performance_management_tab():
    # Initialize the performance management page in session state if it doesn't exist
    if "performance_page" not in st.session_state:
        st.session_state.performance_page = "Self-Appraisal"

    st.selectbox(
        "",  # Empty label to hide the heading
        options=["Self-Appraisal", "Endorsements", "Career"],
        index=["Self-Appraisal", "Endorsements", "Career"].index(
            st.session_state.performance_page
        ),
        key="performance_selector",
        on_change=update_performance_page,
    )

    if st.session_state.performance_page == "Self-Appraisal":
        perform_self_appraisal()
    elif st.session_state.performance_page == "Endorsements":
        display_endorsements(st.session_state.user.id)
    elif st.session_state.performance_page == "Career":
        career_section()  # Call the career section


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
        return create_self_appraisal(st.session_state.llm_choice, user_email)
    elif prompt == "endorsements":
        return LinkedInProfileInfo.display_endorsements(st.session_state.user.id)
    elif prompt == "career":
        return career_section()
    elif prompt == "skills":
        return "Switching to Skills Management"
    elif prompt == "learning":
        return "Switching to Learning Opportunities Dashboard"
    elif prompt == "productivity":
        return productivity_tab()
    elif prompt.startswith("improve_skill:"):
        skill = prompt.split(":")[1]
        resources = find_learning_resources([skill])
        return resources
    else:
        # Handle custom questions using the Q&A bot
        if "qa_index" not in st.session_state:
            st.session_state.qa_index = ingest_data()

        if st.session_state.qa_index is None:
            return "Failed to initialize the index. Please check the logs and try again."

        llm = get_llm(st.session_state.llm_choice)
        try:
            response = answer_question(st.session_state.qa_index, user_email, prompt)
            return response
        except Exception as e:
            return f"An error occurred while processing your question: {str(e)}"


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
                    index=proficiency - 1
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
        format_func=lambda x: ["Novice", "Beginner", "Intermediate", "Advanced", "Expert"][x - 1]
    )
    if st.button("Add Skill"):
        if new_skill and new_skill not in st.session_state.user_skills:
            st.session_state.user_skills[new_skill] = proficiency
            st.success(f"Skill '{new_skill}' added successfully!")
            st.session_state.current_view = "skills"
            st.rerun()
        else:
            st.error("Please enter a unique skill name.")


def individual_contributor_dashboard_conversational():
    st.title(f"Good morning, {st.session_state.user.first_name or st.session_state.user.email.split('@')[0]}")

    if "current_view" not in st.session_state:
        st.session_state.current_view = "main"

    if st.session_state.current_view == "main":
        prompt_options = [
            "Generate a self appraisal for me",
            "Show me the endorsements I have",
            "Show me my current career trajectory information",
            "I would like to manage my skills",
            "I would like to manage my learning opportunities",
            "I would like to get a picture of my productivity",
            "I just want to ask a custom question",
        ]

        selected_prompt = st.selectbox("What would you like to do?", prompt_options)

        if st.button("Submit"):
            if selected_prompt == "I would like to manage my learning opportunities":
                st.session_state.current_view = "learning_dashboard"
                reset_learning_dashboard()
                st.rerun()
            elif selected_prompt == "Show me my current career trajectory information":
                st.session_state.current_view = "career"
                st.rerun()
            elif selected_prompt == "I would like to manage my skills":
                st.session_state.current_view = "skills"
                st.rerun()
            else:
                prompt_map = {
                    "Generate a self appraisal for me": "self_appraisal",
                    "Show me the endorsements I have": "endorsements",
                    "I would like to get a picture of my productivity": "productivity",
                }
                response = handle_prompt(prompt_map.get(selected_prompt, selected_prompt), st.session_state.user.email)
                st.write("Response:", response)

    elif st.session_state.current_view == "learning_dashboard":
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