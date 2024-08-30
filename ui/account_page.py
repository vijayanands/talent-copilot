import streamlit as st

from models.models import (
    change_user_password,
    check_password_match,
    is_password_valid,
    verify_current_password,
)
from ui.personal_profile import personal_profile_section
from ui.work_profile import work_profile_section


def account_page():
    st.header("Account")

    user = st.session_state.user

    # Create tabs for Personal Profile, Work Profile, and Change Password
    tabs = ["Personal Profile", "Work Profile", "Change Password"]
    # Initialize the active tab in session state if it doesn't exist
    if "active_tab" not in st.session_state or st.session_state.active_tab not in tabs:
        st.session_state.active_tab = "Personal Profile"
    active_tab = st.radio(
        "Select a section:",
        tabs,
        key="tab_selector",
        index=tabs.index(st.session_state.active_tab),
    )

    # Update the active tab in session state
    st.session_state.active_tab = active_tab

    if active_tab == "Personal Profile":
        personal_profile_section()
    elif active_tab == "Work Profile":
        work_profile_section()
    elif active_tab == "Change Password":
        change_password_section()


def change_password_section():
    st.subheader("Change Password")

    user = st.session_state.user

    # Initialize session state variables if not exists
    if "change_password_match_error" not in st.session_state:
        st.session_state.change_password_match_error = ""
    if "current_password_error" not in st.session_state:
        st.session_state.current_password_error = ""
    if "new_password_error" not in st.session_state:
        st.session_state.new_password_error = ""

    current_password = st.text_input(
        "Current Password", type="password", key="current_password"
    )
    new_password = st.text_input(
        "New Password",
        type="password",
        key="new_password",
        on_change=check_password_match,
        args=(
            "new_password",
            "confirm_new_password",
            "change_password_match_error",
        ),
    )
    confirm_new_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="confirm_new_password",
        on_change=check_password_match,
        args=(
            "new_password",
            "confirm_new_password",
            "change_password_match_error",
        ),
    )

    # Display password match error if it exists
    if st.session_state.change_password_match_error:
        st.error(st.session_state.change_password_match_error)

    # Display current password error if it exists
    if st.session_state.current_password_error:
        st.error(st.session_state.current_password_error)

    # Display new password error if it exists
    if st.session_state.new_password_error:
        st.error(st.session_state.new_password_error)

    if st.button("Change Password"):
        if not current_password or not new_password or not confirm_new_password:
            st.error("Please fill in all password fields.")
        elif new_password != confirm_new_password:
            st.error("New passwords do not match.")
        elif not is_password_valid(new_password):
            st.error(
                "New password does not meet the requirements. Please ensure it's at least 8 characters long, contains at least one number and one symbol."
            )
        else:
            # Verify current password
            if not verify_current_password(user.id, current_password):
                st.session_state.current_password_error = (
                    "Current password is incorrect."
                )
                st.error("Current password is incorrect.")
            elif current_password == new_password:
                st.session_state.new_password_error = (
                    "New password must be different from the current password."
                )
                st.error("New password must be different from the current password.")
            else:
                if change_user_password(user.id, new_password):
                    st.success(
                        "Password changed successfully! You will now be logged out."
                    )
                    st.session_state.logout_after_password_change = True
                    st.rerun()
                else:
                    st.error("Failed to change password. Please try again.")
