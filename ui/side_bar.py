import base64
import os

import streamlit as st


def setup_sidebar():
    with st.sidebar:
        # Create a container for the profile image
        welcome_container = st.container()
        with welcome_container:
            if st.session_state.user.profile_image:
                img_base64 = get_base64_of_bytes(st.session_state.user.profile_image)
                st.markdown(
                    f'<img src="data:image/png;base64,{img_base64}" width="50" height="50" style="border-radius: 50%;">',
                    unsafe_allow_html=True,
                )
            else:
                default_img = get_base64_of_bin_file("images/default_profile.png")
                st.markdown(
                    f'<img src="data:image/png;base64,{default_img}" width="50" height="50" style="border-radius: 50%;">',
                    unsafe_allow_html=True,
                )

        # st.markdown("---")

        # Initialize the page in session state if it doesn't exist
        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"

        # Dropdown menu using st.selectbox
        selected_page = st.selectbox(
            "",  # Empty label to hide "Menu"
            options=["Dashboard", "Account"],
            index=0 if st.session_state.page == "Dashboard" else 1,
        )

        # Update the page if a different option is selected
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()

        st.markdown("---")

        # Set values from environment variables with defaults
        if st.button("Logout", key="logout_button"):
            del st.session_state.user
            st.rerun()

    return st.session_state.page


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def get_base64_of_bytes(bytes_data):
    return base64.b64encode(bytes_data).decode()
