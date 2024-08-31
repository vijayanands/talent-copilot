import streamlit as st

from helpers.ingestion import answer_question, ingest_data
from ui.ic_functions.individual_contributor import \
    individual_contributor_dashboard_conversational


def dashboard():
    is_manager = st.session_state.get("is_manager", False)

    st.title(
        f"Good morning, {st.session_state.user.first_name or st.session_state.user.email.split('@')[0]}"
    )

    st.text_input("Ask a custom question:", key="custom_question_input")
    if st.button("Ask", key="custom_question_button", on_click=process_custom_question):
        pass

    st.markdown("### OR")

    individual_contributor_dashboard_conversational(is_manager)

    # Display spinner and answer at the bottom of the page
    st.markdown("---")
    if (
        "processing_question" in st.session_state
        and st.session_state.processing_question
    ):
        with st.spinner("Processing your question..."):
            question = st.session_state.custom_question_input
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


def process_custom_question():
    st.session_state.processing_question = True
