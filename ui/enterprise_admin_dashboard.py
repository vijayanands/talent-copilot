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

    ladders = get_all_ladders()
    selected_ladder = st.selectbox(
        "Select Ladder",
        options=[ladder.name for ladder in ladders],
        key="level_elig_ladder",
    )

    selected_ladder_obj = next(
        (ladder for ladder in ladders if ladder.name == selected_ladder), None
    )

    if selected_ladder_obj:
        positions = get_positions_for_ladder(selected_ladder_obj.id)
        selected_position = st.selectbox(
            "Select Position",
            options=[
                f"{selected_ladder_obj.prefix}{position['level']}: {position['name']}"
                for position in positions
            ],
            key="level_elig_position",
        )

        selected_position_obj = next(
            (
                position
                for position in positions
                if f"{selected_ladder_obj.prefix}{position['level']}: {position['name']}"
                == selected_position
            ),
            None,
        )

        if selected_position_obj:
            # Use level as a unique identifier instead of id
            current_criteria = (
                get_eligibility_criteria(selected_position_obj["level"]) or {}
            )

            st.write("Edit eligibility criteria:")
            new_criteria = {}

            new_criteria["years_of_experience"] = st.number_input(
                "Minimum years of experience",
                value=current_criteria.get("years_of_experience", 0),
                key="years_of_experience",
            )
            new_criteria["projects_completed"] = st.number_input(
                "Minimum projects completed",
                value=current_criteria.get("projects_completed", 0),
                key="projects_completed",
            )
            new_criteria["leadership_experience"] = st.checkbox(
                "Leadership experience required",
                value=current_criteria.get("leadership_experience", False),
                key="leadership_experience",
            )

            if st.button("Update Eligibility Criteria", key="update_eligibility"):
                # Use level as a unique identifier instead of id
                if update_eligibility_criteria(
                    selected_position_obj["level"], new_criteria
                ):
                    st.success("Eligibility criteria updated successfully!")
                else:
                    st.error("Failed to update eligibility criteria.")


if __name__ == "__main__":
    enterprise_admin_dashboard()
