import streamlit as st
from supabase import Client

def save_favorite(supabase: Client, user_id, email, content, topic):
    try:
        normalized_topic = topic.lower().strip()
        normalized_content = content.lower().strip()
        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("topic", topic).execute()
        for item in existing.data:
            if item["content"].lower().strip() == normalized_content:
                st.warning("This content is already in your favorites!")
                return False
        data = {"user_id": user_id, "email": email, "topic": topic, "content": content}
        response = supabase.table("favorites").insert(data).execute()
        return bool(response.data)
    except Exception:
        st.error("Failed to save favorite.")
        return False

def get_favorites(supabase: Client, user_id):
    try:
        response = supabase.table("favorites").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception:
        st.error("Error retrieving favorites.")
        return []

def delete_favorite(supabase: Client, user_id, favorite_id):
    try:
        response = supabase.table("favorites").delete().eq("id", favorite_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception:
        st.error("Error deleting favorite.")
        return False

def render_favorites(supabase, user):
    st.title("⭐ Your Favorites")
    if not user:
        st.error("Please log in again.")
    else:
        favorites = get_favorites(supabase, user.id)
        if not favorites:
            st.info("No favorites yet. Start creating!")
        for idx, item in enumerate(favorites):
            with st.container():
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.markdown(
                        f"""
                        <div class='favorite-card' style="padding: 1em; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">
                            <h4 style="margin-bottom: 0.5em;">🌟 {item['topic'].title()}</h4>
                            <div>{item['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col2:
                    if st.button("Delete 🗑️", key=f"del_{idx}", help="Remove this favorite", type='primary'):
                        if delete_favorite(supabase, user.id, item['id']):
                            st.rerun()