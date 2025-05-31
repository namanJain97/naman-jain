import streamlit as st
from supabase import Client

def save_feedback(supabase: Client, user_id, email, feedback):
    try:
        data = {"user_id": user_id if user_id else "anonymous", "email": email if email else "anonymous", "feedback": feedback}
        response = supabase.table("feedback").insert(data).execute()
        return bool(response.data)
    except Exception as e:
        st.error("Failed to submit feedback. Please try again.")
        return False

def render_feedback_form(supabase, user):
    st.subheader("We'd Love Your Feedback!")
    with st.form("feedback_form"):
        feedback = st.text_area("Share your thoughts or suggestions:")
        submitted = st.form_submit_button("Submit")
        if submitted and feedback.strip():
            if 'feedback_submitted' not in st.session_state:
                st.session_state.feedback_submitted = False
            if not st.session_state.feedback_submitted:
                user_id = user.id if user else None
                user_email = user.email if user else None
                if save_feedback(supabase, user_id, user_email, feedback):
                    st.success("Thank you for your feedback!")
                    st.session_state.feedback_submitted = True
            else:
                st.warning("Feedback already submitted.")
                