import streamlit as st
import database

def render_feedback_ui(interaction_id):
    """Renders helpful/not helpful buttons for a given interaction."""
    st.write("---")
    st.write("Was this response helpful?")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("👍 Helpful", key=f"help_{interaction_id}"):
            database.update_feedback(interaction_id, True)
            st.success("Thank you for your feedback!")
            
    with col2:
        if st.button("👎 Not Helpful", key=f"not_help_{interaction_id}"):
            database.update_feedback(interaction_id, False)
            st.error("Thank you for your feedback, we will improve.")
