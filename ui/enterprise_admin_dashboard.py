import streamlit as st

from models.models import (Ladder, Position, get_all_ladders,
                           get_eligibility_criteria, get_positions_for_ladder,
                           update_eligibility_criteria,
                           update_ladder_positions)


def enterprise_admin_dashboard():
    st.title("Enterprise Admin Dashboard")

    tab1, tab2 = st.tabs(["Level Definitions", "Level Eligibility"])

    with tab1:
        level_definitions()

    with tab2:
        level_eligibility()


def level_definitions():
    st.header("Level Definitions")

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "positions" not in st.session_state:
        st.session_state.positions = []
    if "new_position" not in st.session_state:
        st.session_state.new_position = {"name": "", "level": 1}

    ladders = get_all_ladders()
    selected_ladder = st.selectbox(
        "Select Ladder",
        options=[ladder.name for ladder in ladders],
        key="level_def_ladder",
    )

    selected_ladder_obj = next(
        (ladder for ladder in ladders if ladder.name == selected_ladder), None
    )

    if selected_ladder_obj:
        if not st.session_state.edit_mode:
            display_current_positions(selected_ladder_obj)
        else:
            edit_positions(selected_ladder_obj)


def display_current_positions(ladder):
    positions = get_positions_for_ladder(ladder.id)
    st.session_state.positions = positions

    st.write(f"Current positions for {ladder.name}:")
    for position in positions:
        st.write(f"{ladder.prefix}{position['level']}: {position['name']}")

    if st.button("Edit Positions", key="edit_positions_button"):
        st.session_state.edit_mode = True
        st.rerun()


def edit_positions(ladder):
    st.write(f"Editing positions for {ladder.name}:")

    if "positions" not in st.session_state:
        st.session_state.positions = get_positions_for_ladder(ladder.id)

    positions = st.session_state.positions

    for i, position in enumerate(positions):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            position["name"] = st.text_input(
                f"Position {position['level']}",
                value=position["name"],
                key=f"position_{i}",
            )
        with col2:
            position["level"] = st.number_input(
                "Level", min_value=1, value=position["level"], key=f"level_{i}"
            )
        with col3:
            if st.button("Delete", key=f"delete_{i}"):
                delete_position(i)
                st.rerun()

    st.write("Add a new position:")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        new_name = st.text_input("New Position Name", key="new_position_name")
    with col2:
        new_level = st.number_input(
            "New Position Level",
            min_value=1,
            max_value=len(positions) + 1,
            key="new_position_level",
        )
    with col3:
        if st.button("Add Position", key="add_position_button"):
            add_new_position(positions, new_name, new_level)
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update Positions", key="update_positions_button"):
            if update_ladder_positions(ladder.id, positions):
                st.success("Positions updated successfully!")
                st.session_state.edit_mode = False
                st.rerun()
            else:
                st.error("Failed to update positions.")
    with col2:
        if st.button("Cancel", key="cancel_edit_button"):
            st.session_state.edit_mode = False
            st.rerun()

    st.session_state.positions = positions

def add_new_position(positions, name, level):
    # Shift existing positions if necessary
    for position in positions:
        if position["level"] >= level:
            position["level"] += 1

    # Add the new position
    positions.append({"name": name, "level": level})

    # Sort positions by level
    positions.sort(key=lambda x: x["level"])


def delete_position(index):
    positions = st.session_state.positions
    deleted_level = positions[index]["level"]

    # Remove the position
    del positions[index]

    # Decrement levels for positions above the deleted one
    for position in positions:
        if position["level"] > deleted_level:
            position["level"] -= 1

    # Sort positions by level
    st.session_state.positions = sorted(positions, key=lambda x: x["level"])

def level_eligibility():
    st.header("Level Eligibility")

    # Custom CSS for bordered text areas
    st.markdown("""
    <style>
    .stTextArea textarea {
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    ladders = get_all_ladders()
    ladder_names = [ladder.name for ladder in ladders]

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "temp_criteria" not in st.session_state:
        st.session_state.temp_criteria = {}
    if "selected_ladder_name" not in st.session_state:
        st.session_state.selected_ladder_name = ladder_names[0] if ladder_names else None

    # Dropdown to select a ladder
    selected_ladder_name = st.selectbox(
        "Select Ladder",
        options=ladder_names,
        key="level_elig_ladder_select",
        index=ladder_names.index(st.session_state.selected_ladder_name) if st.session_state.selected_ladder_name in ladder_names else 0
    )

    st.session_state.selected_ladder_name = selected_ladder_name
    selected_ladder_obj = next((ladder for ladder in ladders if ladder.name == selected_ladder_name), None)

    if selected_ladder_obj:
        positions = get_positions_for_ladder(selected_ladder_obj.id)

        if not st.session_state.edit_mode:
            if st.button(f"Edit {selected_ladder_obj.name} Eligibility", key=f"edit_button_{selected_ladder_obj.name}"):
                st.session_state.edit_mode = True
                st.session_state.temp_criteria = {}
                for position in positions:
                    position_key = f"{selected_ladder_obj.name}_{position['name']}_{position['id']}"
                    criteria = get_eligibility_criteria(position['id'])
                    st.session_state.temp_criteria[position_key] = criteria or ""
                st.rerun()
        else:
            st.write(f"Editing {selected_ladder_obj.name} Ladder Eligibility")

        for index, position in enumerate(positions):
            level = position['level']
            name = position['name']
            position_id = position['id']
            position_key = f"{selected_ladder_obj.name}_{name}_{position_id}"

            if st.session_state.edit_mode:
                st.text_area(
                    f"Level {level} ({name}) Eligibility",
                    value=st.session_state.temp_criteria.get(position_key, ""),
                    key=f"criteria_{position_key}_{index}",
                    on_change=lambda pk=position_key, idx=index: st.session_state.temp_criteria.update({pk: st.session_state[f"criteria_{pk}_{idx}"]})
                )
            else:
                criteria = get_eligibility_criteria(position_id)
                st.write(f"**Level {level} ({name}):**")
                st.write(criteria or "No eligibility criteria set.")

        if st.session_state.edit_mode:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_button_{selected_ladder_obj.name}"):
                    for position_key, criteria in st.session_state.temp_criteria.items():
                        _, _, position_id = position_key.rsplit('_', 2)
                        update_eligibility_criteria(int(position_id), criteria)
                    st.session_state.edit_mode = False
                    st.success("Eligibility criteria updated successfully!")
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_button_{selected_ladder_obj.name}"):
                    st.session_state.edit_mode = False
                    st.session_state.temp_criteria = {}
                    st.rerun()

    # Ensure we stay on the Level Eligibility tab
    st.session_state.active_tab = "Level Eligibility"
    
if __name__ == "__main__":
    enterprise_admin_dashboard()
