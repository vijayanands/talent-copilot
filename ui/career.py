import streamlit as st
import plotly.graph_objects as go
from models.models import get_positions_for_ladder, get_eligibility_criteria, Session, User, Position
from sqlalchemy.orm import joinedload

def career_section():
    st.subheader("Career Progression")

    # Fetch the user data within a session
    with Session() as session:
        user = session.query(User).options(joinedload(User.position).joinedload(Position.ladder)).get(st.session_state.user.id)
        
        if not user or not user.position:
            st.warning("You don't have a current position set. Please update your work profile.")
            return

        ladder = user.position.ladder
        positions = get_positions_for_ladder(ladder.id)

        # Create a visualization of the career ladder
        fig = create_career_ladder_visualization(positions, user.position)
        st.plotly_chart(fig)

        # Show eligibility criteria for next level
        show_next_level_criteria(user.position, positions)

    # Add "What are my gaps?" button
    if st.button("What are my gaps?"):
        st.info("This feature is coming soon!")

def create_career_ladder_visualization(positions, current_position):
    levels = [f"{p['level']}" for p in positions]
    names = [p['name'] for p in positions]
    
    fig = go.Figure(go.Bar(
        x=[1] * len(levels),
        y=levels,
        orientation='h',
        text=names,
        textposition='inside',
        insidetextanchor='middle',
        marker=dict(color=['lightblue' if p['level'] != current_position.level else 'gold' for p in positions])
    ))
    
    fig.update_layout(
        title='Your Career Ladder',
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(title='Level', autorange='reversed'),
        height=400,
        width=600,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def show_next_level_criteria(current_position, all_positions):
    current_level = current_position.level
    next_position = next((p for p in all_positions if p['level'] > current_level), None)

    if next_position:
        st.subheader(f"What's Needed for Promotion to {next_position['name']}")
        criteria = get_eligibility_criteria(next_position['id'])
        if criteria:
            st.write(criteria)
        else:
            st.info("No specific criteria defined for the next level.")
    else:
        st.info("You're at the highest level in your current ladder!")
