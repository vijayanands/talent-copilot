import streamlit as st
from models.models import update_work_profile, get_user_by_id, delete_resume
import os
import base64

def work_profile_section():
    st.subheader("Work Profile")

    user = st.session_state.user

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
        ladder = st.selectbox("Career Ladder", 
                              ["Individual Contributor (Software)", "Management", "Product"], 
                              index=["Individual Contributor (Software)", "Management", "Product"].index(user.ladder) if user.ladder else 0)

        position_options = {
            "Individual Contributor (Software)": [
                "Software Engineer", "Sr Software Engineer", "Staff Software Engineer",
                "Sr Staff Software Engineer", "Principal Engineer", "Distinguished Engineer", "Fellow"
            ],
            "Management": [
                "Manager", "Sr Manager", "Director", "Sr Director",
                "Vice President", "Sr Vice President", "Executive Vice President"
            ],
            "Product": [
                "Product Manager", "Sr Product Manager", "Group Product Manager",
                "Vice President", "Sr Vice President"
            ]
        }

        current_position = st.selectbox("Current Position", 
                                        position_options[ladder], 
                                        index=position_options[ladder].index(user.current_position) if user.current_position in position_options[ladder] else 0)
        
        responsibilities = st.text_area("Current Responsibilities", value=user.responsibilities or "")

        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Work Profile"):
                updates = {
                    "ladder": ladder,
                    "current_position": current_position,
                    "responsibilities": responsibilities
                }

                if uploaded_file is not None:
                    # Create a directory to store resumes if it doesn't exist
                    os.makedirs("resumes", exist_ok=True)
                    
                    # Generate a unique filename
                    filename = f"resumes/resume_{user.id}.pdf"
                    
                    # Save the file
                    with open(filename, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    updates["resume_pdf"] = filename

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
        st.write(f"**Career Ladder:** {user.ladder or 'Not specified'}")
        st.write(f"**Current Position:** {user.current_position or 'Not specified'}")
        st.write("**Current Responsibilities:**")
        st.write(user.responsibilities or 'Not specified')
        
        if user.resume_pdf and os.path.exists(user.resume_pdf):
            st.write("**Resume:**")
            
            # Display PDF viewer
            with open(user.resume_pdf, "rb") as pdf_file:
                base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Download button
            with col1:
                with open(user.resume_pdf, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Download Resume",
                    data=pdf_bytes,
                    file_name="resume.pdf",
                    mime="application/pdf"
                )
            
            # Delete button
            with col2:
                if st.button("Delete Resume"):
                    if delete_resume(user.id):
                        os.remove(user.resume_pdf)
                        st.success("Resume deleted successfully!")
                        st.session_state.user = get_user_by_id(user.id)  # Refresh user data
                        st.rerun()
                    else:
                        st.error("Failed to delete resume. Please try again.")
        else:
            st.write("No resume uploaded")

    # Ensure the active tab remains "Work Profile"
    st.session_state.active_tab = "Work Profile"
