import streamlit as st
from models.models import (
    get_all_ladders, get_positions_for_ladder, update_ladder_positions,
    get_eligibility_criteria, update_eligibility_criteria, Ladder, Position
)

def enterprise_admin_dashboard():
    st.title("Enterprise Admin Dashboard")

    tab1, tab2 = st.tabs(["Level Definitions", "Level Eligibility"])

    with tab1:
        level_definitions()

    with tab2:
        level_eligibility()

def level_definitions():
    st.header("Level Definitions")

    ladders = get_all_ladders()
    selected_ladder = st.selectbox("Select Ladder", options=[ladder.name for ladder in ladders], key="level_def_ladder")
    
    selected_ladder_obj = next((ladder for ladder in ladders if ladder.name == selected_ladder), None)
    
    if selected_ladder_obj:
        positions = get_positions_for_ladder(selected_ladder_obj.id)
        position_names = [position.name for position in positions]
        
        st.write(f"Current positions for {selected_ladder}:")
        for i, name in enumerate(position_names, start=1):
            st.write(f"{selected_ladder_obj.prefix}{i}: {name}")
        
        st.write("Edit positions:")
        new_positions = []
        for i in range(len(position_names) + 1):
            new_position = st.text_input(f"Position {i+1}", value=position_names[i] if i < len(position_names) else "", key=f"position_{i}")
            if new_position:
                new_positions.append(new_position)
        
        if st.button("Update Positions", key="update_positions"):
            if update_ladder_positions(selected_ladder_obj.id, new_positions):
                st.success("Positions updated successfully!")
            else:
                st.error("Failed to update positions.")

def level_eligibility():
    st.header("Level Eligibility")

    ladders = get_all_ladders()
    selected_ladder = st.selectbox("Select Ladder", options=[ladder.name for ladder in ladders], key="level_elig_ladder")
    
    selected_ladder_obj = next((ladder for ladder in ladders if ladder.name == selected_ladder), None)
    
    if selected_ladder_obj:
        positions = get_positions_for_ladder(selected_ladder_obj.id)
        selected_position = st.selectbox("Select Position", options=[f"{selected_ladder_obj.prefix}{position.level}: {position.name}" for position in positions], key="level_elig_position")
        
        selected_position_obj = next((position for position in positions if f"{selected_ladder_obj.prefix}{position.level}: {position.name}" == selected_position), None)
        
        if selected_position_obj:
            current_criteria = get_eligibility_criteria(selected_position_obj.id) or {}
            
            st.write("Edit eligibility criteria:")
            new_criteria = {}
            
            # Example criteria fields (you can customize these based on your needs)
            new_criteria["years_of_experience"] = st.number_input("Minimum years of experience", value=current_criteria.get("years_of_experience", 0), key="years_of_experience")
            new_criteria["projects_completed"] = st.number_input("Minimum projects completed", value=current_criteria.get("projects_completed", 0), key="projects_completed")
            new_criteria["leadership_experience"] = st.checkbox("Leadership experience required", value=current_criteria.get("leadership_experience", False), key="leadership_experience")
            
            if st.button("Update Eligibility Criteria", key="update_eligibility"):
                if update_eligibility_criteria(selected_position_obj.id, new_criteria):
                    st.success("Eligibility criteria updated successfully!")
                else:
                    st.error("Failed to update eligibility criteria.")

if __name__ == "__main__":
    enterprise_admin_dashboard()
