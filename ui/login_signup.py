import streamlit as st

from models.models import (
    check_password_match,
    is_password_valid,
    register_user,
    verify_login,
)


def login_page():
    st.header("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        user = verify_login(email, password)
        if user:
            st.session_state.user = user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid email or password")


def signup_page():
    st.header("Sign Up")

    if "signup_password_match_error" not in st.session_state:
        st.session_state.signup_password_match_error = ""

    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name*", key="signup_first_name")
        email = st.text_input("Email*", key="signup_email")
        password = st.text_input(
            "Password*",
            type="password",
            key="signup_password",
            on_change=check_password_match,
            args=(
                "signup_password",
                "signup_confirm_password",
                "signup_password_match_error",
            ),
        )
        confirm_password = st.text_input(
            "Confirm Password*",
            type="password",
            key="signup_confirm_password",
            on_change=check_password_match,
            args=(
                "signup_password",
                "signup_confirm_password",
                "signup_password_match_error",
            ),
        )
        st.caption(
            "Password must be at least 8 characters long, contain at least one number and one symbol."
        )

        if st.session_state.signup_password_match_error:
            st.error(st.session_state.signup_password_match_error)

        role = st.radio(
            "Select Role", ["Individual Contributor", "People Manager", "Enterprise Administrator"]
        )
        is_manager = role == "People Manager"
        is_enterprise_admin = role == "Enterprise Admin"

    with col2:
        last_name = st.text_input("Last Name*", key="signup_last_name")
        address = st.text_input("Address (optional)", key="signup_address")
        phone = st.text_input("Phone (optional)", key="signup_phone")
        linkedin_profile = st.text_input(
            "LinkedIn Profile (optional)", key="signup_linkedin"
        )
        profile_image = st.file_uploader(
            "Profile Image (optional)", type=["jpg", "jpeg", "png"]
        )

    if st.button("Sign Up", key="signup_button"):
        if not first_name or not last_name:
            st.error("First name and last name are required.")
        elif not is_password_valid(st.session_state.signup_password):
            st.error(
                "Password does not meet the requirements. Please ensure it's at least 8 characters long, contains at least one number and one symbol."
            )
        elif (
            st.session_state.signup_password != st.session_state.signup_confirm_password
        ):
            st.error("Passwords do not match. Please try again.")
        else:
            try:
                register_user(
                    email,
                    st.session_state.signup_password,
                    is_manager,
                    is_enterprise_admin,
                    linkedin_profile,
                    first_name,
                    last_name,
                    address,
                    phone,
                    profile_image,
                )
                st.success("Account created successfully! Please log in.")
                for key in st.session_state.keys():
                    if key.startswith("signup_"):
                        del st.session_state[key]
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")
