import streamlit as st
from models.models import update_user_profile

def personal_profile_section():
    st.subheader("Personal Profile")

    user = st.session_state.user

    # Initialize session state for edit mode if not exists
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # Edit button with pencil icon
    edit_button = st.button("✏️ Edit Personal Profile")

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

        if st.button("Update Personal Profile"):
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
