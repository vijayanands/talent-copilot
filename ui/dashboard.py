import streamlit as st
import uuid

from helpers.ingestion import answer_question, ingest_data
from ui.ic_functions.individual_contributor import \
    individual_contributor_dashboard_conversational


def dashboard():
    is_manager = st.session_state.get("is_manager", False)

    st.title(
        f"Good morning, {st.session_state.user.first_name or st.session_state.user.email.split('@')[0]}"
    )

    # Get the current selection
    current_action = individual_contributor_dashboard_conversational(is_manager)

    # Store the previous selection
    if "previous_action" not in st.session_state:
        st.session_state.previous_action = "Select an action"

    # Check if the action has changed and update the input key and value if it has
    if current_action != st.session_state.previous_action and current_action != "Select an action":
        st.session_state.input_key = str(uuid.uuid4())
        st.session_state.input_value = ""
        st.session_state.previous_action = current_action
        st.rerun()  # Force a rerun to update the UI immediately

    # Only show the "OR" and custom question input if no action is selected
    if current_action == "Select an action":
        st.markdown("### OR")

        # Initialize the input_key and input_value in session state if they don't exist
        if "input_key" not in st.session_state:
            st.session_state.input_key = str(uuid.uuid4())
        if "input_value" not in st.session_state:
            st.session_state.input_value = ""

        # Use the dynamic key for the text input and set its value
        custom_question = st.text_input("Ask a custom question:", key=st.session_state.input_key, value=st.session_state.input_value)

        if st.button("Ask", key="custom_question_button"):
            st.session_state.processing_question = True
            st.session_state.custom_question = custom_question

    # Display spinner and answer at the bottom of the page
    st.markdown("---")
    if st.session_state.get("processing_question", False):
        with st.spinner("Processing your question..."):
            question = st.session_state.get("custom_question", "")
            if question:
                index = ingest_data()
                answer = answer_question(index, st.session_state.user.email, question)
                st.session_state.question_answer = answer
            st.session_state.processing_question = False
            st.rerun()

    if "question_answer" in st.session_state and st.session_state.question_answer:
        st.subheader("Answer to your question:")
        st.write(st.session_state.question_answer)
        # Clear the answer after displaying
        st.session_state.question_answer = None