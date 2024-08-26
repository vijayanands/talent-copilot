import base64

import streamlit as st

from models.models import (delete_resume, get_all_ladders,
                           get_positions_for_ladder, get_user_by_id,
                           update_work_profile, Session, User, Position)
from sqlalchemy.orm import joinedload

def work_profile_section():
    st.subheader("Work Profile")

    # Fetch the user data within a session
    with Session() as session:
        user = session.query(User).options(
            joinedload(User.position).joinedload(Position.ladder)
        ).get(st.session_state.user.id)

        if user is None:
            st.error("User not found. Please log in again.")
            return

        # Initialize session state for work profile edit mode if not exists
        if "work_edit_mode" not in st.session_state:
            st.session_state.work_edit_mode = False

        # Edit button with pencil icon
        if not st.session_state.work_edit_mode:
            work_edit_button = st.button("✏️ Edit Work Profile")
            if work_edit_button:
                st.session_state.work_edit_mode = True
                st.rerun()

        if st.session_state.work_edit_mode:
            # Edit mode: show editable fields
            ladders = get_all_ladders()
            ladder_names = [ladder.name for ladder in ladders]
            selected_ladder = st.selectbox(
                "Career Ladder",
                options=ladder_names,
                index=ladder_names.index(user.position.ladder.name) if user.position else 0,
            )

            selected_ladder_obj = next(
                (ladder for ladder in ladders if ladder.name == selected_ladder), None
            )

            if selected_ladder_obj:
                positions = get_positions_for_ladder(selected_ladder_obj.id)
                position_options = [
                    f"{selected_ladder_obj.prefix}{position['level']}: {position['name']}"
                    for position in positions
                ]

                current_position = st.selectbox(
                    "Current Position",
                    options=position_options,
                    index=(
                        position_options.index(
                            f"{user.position.ladder.prefix}{user.position.level}: {user.position.name}"
                        )
                        if user.position
                        else 0
                    ),
                )

            responsibilities = st.text_area(
                "Current Responsibilities", value=user.responsibilities or ""
            )

            uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Work Profile"):
                    selected_position_obj = next(
                        (
                            position
                            for position in positions
                            if f"{selected_ladder_obj.prefix}{position['level']}: {position['name']}"
                            == current_position
                        ),
                        None,
                    )

                    updates = {
                        "position_id": (
                            selected_position_obj['id'] if selected_position_obj else None
                        ),
                        "responsibilities": responsibilities,
                    }

                    if uploaded_file is not None:
                        pdf_bytes = uploaded_file.getvalue()
                        updates["resume_pdf"] = pdf_bytes

                    updated_user = update_work_profile(user.id, **updates)
                    if updated_user:
                        st.success("Work profile updated successfully!")
                        st.session_state.user = updated_user
                        st.session_state.work_edit_mode = False
                        st.rerun()
                    else:
                        st.error("Failed to update work profile. Please try again.")
            with col2:
                if st.button("Cancel"):
                    st.session_state.work_edit_mode = False
                    st.rerun()
        else:
            # Display mode: show non-editable fields
            if user.position:
                st.write(f"**Career Ladder:** {user.position.ladder.name}")
                st.write(
                    f"**Current Position:** {user.position.ladder.prefix}{user.position.level}: {user.position.name}"
                )
            else:
                st.write("**Career Ladder:** Not specified")
                st.write("**Current Position:** Not specified")

            st.write("**Current Responsibilities:**")
            st.write(user.responsibilities or "Not specified")

            if user.resume_pdf:
                st.write("**Resume:**")

                # Display PDF viewer
                base64_pdf = base64.b64encode(user.resume_pdf).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                # Download button
                with col1:
                    st.download_button(
                        label="Download Resume",
                        data=user.resume_pdf,
                        file_name="resume.pdf",
                        mime="application/pdf",
                    )

                # Delete button
                with col2:
                    if st.button("Delete Resume"):
                        if delete_resume(user.id):
                            st.success("Resume deleted successfully!")
                            st.session_state.user = get_user_by_id(user.id)  # Refresh user data
                            st.rerun()
                        else:
                            st.error("Failed to delete resume. Please try again.")
            else:
                st.write("No resume uploaded")

    # Ensure the active tab remains "Work Profile"
    st.session_state.active_tab = "Work Profile"
