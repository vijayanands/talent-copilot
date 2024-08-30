import streamlit as st
from functions.self_appraisal import create_self_appraisal
from helpers.ingestion import ingest_data, answer_question
from models.models import LinkedInProfileInfo
from ui.career import career_section
from ui.learning_dashboard import learning_dashboard
from ui.productivity import productivity_tab
from ui.skills_section import skills_section


def infer_category(query):
    performance_keywords = [
        "appraisal",
        "performance",
        "achievements",
        "contributions",
        "endorsements",
        "career",
    ]
    learning_keywords = ["skills", "learning", "development", "recommendations"]
    productivity_keywords = ["productivity", "tasks", "time management", "efficiency"]

    query_lower = query.lower()

    if any(keyword in query_lower for keyword in performance_keywords):
        return "Performance Management"
    elif any(keyword in query_lower for keyword in learning_keywords):
        return "Skills, Learning and Development"
    elif any(keyword in query_lower for keyword in productivity_keywords):
        return "Productivity"
    else:
        return "General Q&A"


def handle_performance_query(query):
    # Implement logic to handle performance-related queries
    return "Handling performance query: " + query


def handle_learning_query(query):
    # Implement logic to handle learning-related queries
    return "Handling learning and development query: " + query


def handle_productivity_query(query):
    # Implement logic to handle productivity-related queries
    return "Handling productivity query: " + query


def handle_general_query(query):
    if "qa_index" not in st.session_state:
        st.session_state.qa_index = ingest_data()

    if st.session_state.qa_index is None:
        return "Sorry, I couldn't access the necessary data to answer your question."

    if "user" in st.session_state and hasattr(st.session_state.user, "email"):
        user_email = st.session_state.user.email
    else:
        user_email = "anonymous@example.com"  # Fallback email for unauthenticated users

    response = answer_question(st.session_state.qa_index, user_email, query)
    return response


def conversational_ui():
    st.title("Individual Contributor Assistant")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "user" not in st.session_state or not hasattr(st.session_state.user, "email"):
        st.warning("You are not logged in. Some features may be limited.")

    for message in st.session_state.conversation_history:
        st.text(f"User: {message['user']}")
        st.text(f"Assistant: {message['assistant']}")

    user_input = st.text_input(
        "Ask me anything about your performance, learning, productivity, or any other questions:",
        key="user_input",
    )

    if st.button("Send"):
        if user_input:
            category = infer_category(user_input)

            if category == "Performance Management":
                response = handle_performance_query(user_input)
            elif category == "Skills, Learning and Development":
                response = handle_learning_query(user_input)
            elif category == "Productivity":
                response = handle_productivity_query(user_input)
            else:
                response = handle_general_query(user_input)

            st.session_state.conversation_history.append(
                {"user": user_input, "assistant": response}
            )
            st.text(f"User: {user_input}")
            st.text(f"Assistant: {response}")
            st.text(f"(Category: {category})")


if __name__ == "__main__":
    conversational_ui()
