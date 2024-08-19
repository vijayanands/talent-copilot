import streamlit as st
from models.models import update_user_profile, verify_current_password, change_user_password, is_password_valid, \
    check_password_match


def account_page():
    st.header("Account")

    user = st.session_state.user

    # Create tabs for Profile Information and Change Password
    profile_tab, password_tab = st.tabs(["Profile Information", "Change Password"])

    with profile_tab:
        st.subheader("Profile Information")

        # Initialize session state for edit mode if not exists
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        # Edit button with pencil icon
        edit_button = st.button("✏️ Edit")

        if edit_button:
            st.session_state.edit_mode = not st.session_state.edit_mode

        if st.session_state.edit_mode:
            # Edit mode: show editable fields
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=user.first_name)
                last_name = st.text_input("Last Name", value=user.last_name)
                address = st.text_input("Address", value=user.address)
            with col2:
                phone = st.text_input("Phone Number", value=user.phone)
                linkedin_profile = st.text_input(
                    "LinkedIn Profile URL", value=user.linkedin_profile
                )

            if st.button("Update Profile"):
                # Prepare a dictionary of changed fields
                updates = {}
                if first_name != user.first_name:
                    updates["first_name"] = first_name
                if last_name != user.last_name:
                    updates["last_name"] = last_name
                if address != user.address:
                    updates["address"] = address
                if phone != user.phone:
                    updates["phone"] = phone
                if linkedin_profile != user.linkedin_profile:
                    updates["linkedin_profile"] = linkedin_profile

                if updates:
                    updated_user = update_user_profile(user.id, **updates)
                    if updated_user:
                        st.success("Profile updated successfully!")
                        st.session_state.user = updated_user  # Update the session state with the new user data
                        st.session_state.edit_mode = False  # Exit edit mode
                        st.rerun()  # Rerun to show updated profile
                    else:
                        st.error("Failed to update profile. Please try again.")
                else:
                    st.info("No changes detected in the profile.")
        else:
            # Display mode: show non-editable fields
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**First Name:** {user.first_name}")
                st.write(f"**Last Name:** {user.last_name}")
                st.write(f"**Address:** {user.address or 'Not provided'}")
            with col2:
                st.write(f"**Phone Number:** {user.phone or 'Not provided'}")
                st.write(
                    f"**LinkedIn Profile URL:** {user.linkedin_profile or 'Not provided'}"
                )

    with password_tab:
        st.subheader("Change Password")

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
                    st.error(
                        "New password must be different from the current password."
                    )
                else:
                    if change_user_password(user.id, new_password):
                        st.success(
                            "Password changed successfully! You will now be logged out."
                        )
                        st.session_state.logout_after_password_change = True
                        st.rerun()
                    else:
                        st.error("Failed to change password. Please try again.")
