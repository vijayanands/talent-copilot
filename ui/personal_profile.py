import streamlit as st

from models.models import update_user_profile


def personal_profile_section():
    st.subheader("Personal Profile")

    user = st.session_state.user

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if not st.session_state.edit_mode:
        edit_button = st.button("✏️ Edit Personal Profile")
        if edit_button:
            st.session_state.edit_mode = True
            st.rerun()

    if st.session_state.edit_mode:
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
            profile_image = st.file_uploader(
                "Profile Image", type=["jpg", "jpeg", "png"]
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Personal Profile"):
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
                if profile_image:
                    updates["profile_image"] = profile_image

                if updates:
                    updated_user = update_user_profile(user.id, **updates)
                    if updated_user:
                        st.success("Profile updated successfully!")
                        st.session_state.user = updated_user
                        st.session_state.edit_mode = False
                        st.rerun()
                    else:
                        st.error("Failed to update profile. Please try again.")
                else:
                    st.info("No changes detected in the profile.")
        with col2:
            if st.button("Cancel"):
                st.session_state.edit_mode = False
                st.rerun()
    else:
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

        if user.profile_image:
            profile_image = user.get_profile_image()
            st.image(profile_image, caption="Profile Image", width=150)
        else:
            st.write("No profile image uploaded")
