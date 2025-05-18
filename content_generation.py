import streamlit as st
import datetime
import requests
from agent import generate_copy
from unsplash import get_unsplash_images
from database import save_usage, check_usage_limit
from utils import text_to_speech, copy_to_clipboard, social_share_buttons

def render_content_generation(supabase, user):
    st.title("✍️ Generate Your Copy")
    can_generate, daily_usage, total_available, remaining = check_usage_limit(supabase, user.id)
    plan = supabase.table("users").select("plan").eq("id", user.id).execute().data[0]["plan"]
    
    st.markdown(
        f'<div class="usage-info">📊 Usage: {daily_usage}/{total_available} generations today ({remaining} remaining)</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        content_type = st.selectbox("Content Type", [
            "blog post", "social media post", "ad copy", "email", "press release", "YouTube script", "newsletter", 
            "LinkedIn post", "product description", "landing page copy"
        ])
        topic = st.text_input("Topic")
    with col2:
        tone = st.selectbox("Tone", [
            "friendly", "professional", "funny", "urgent", "inspirational", "casual", "sarcastic", "formal", 
            "empathetic", "authoritative"
        ])
        length = st.selectbox("Length", ["short", "medium", "long"])

    if "generated_output" not in st.session_state:
        st.session_state.generated_output = None
    if "selected_image" not in st.session_state:
        st.session_state.selected_image = None
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []

    if st.button("🚀 Generate"):
        if not topic.strip():
            st.error("Enter a topic to generate content.")
        elif not can_generate:
            st.error("You've reached your daily limit for content generation.")
            if plan == "free":
                st.markdown(
                    '<a href="?menu=✍️%20Generate%20Content"><button class="upgrade-btn">Upgrade to Pro for More 🚀</button></a>',
                    unsafe_allow_html=True
                )
        else:
            with st.spinner("Crafting your masterpiece..."):
                st.session_state.generated_output = generate_copy(content_type, topic, tone, length)
                if "----" in st.session_state.generated_output or not st.session_state.generated_output.strip():
                    st.session_state.generated_output = generate_copy(content_type, topic, tone, length)
                if st.session_state.generated_output and "<p>Error generating content" not in st.session_state.generated_output:
                    save_usage(supabase, user.id, user.email, content_type)
                st.session_state.generated_images = get_unsplash_images(topic)
                st.session_state.selected_image = st.session_state.generated_images[0] if st.session_state.generated_images else None

    if st.session_state.generated_output:
        st.success("Content ready!")
        st.markdown(st.session_state.generated_output, unsafe_allow_html=True)
        st.markdown("---")

        audio_b64 = text_to_speech(st.session_state.generated_output)
        if audio_b64:
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
        else:
            st.warning("Unable to generate audio for this content.")
        
        col1, col2 = st.columns(2)
        with col1:
            copy_to_clipboard(st.session_state.generated_output)
        with col2:
            social_share_buttons(st.session_state.generated_output, topic)

        if st.session_state.generated_images:
            st.subheader("Pick an Image")
            image_labels = [f"Image {i+1}" for i in range(len(st.session_state.generated_images))]
            image_choice = st.radio("Images", image_labels)
            st.session_state.selected_image = st.session_state.generated_images[image_labels.index(image_choice)]
            st.markdown(
                f'<img src="{st.session_state.selected_image}" class="responsive-image">',
                unsafe_allow_html=True
            )
            image_response = requests.get(st.session_state.selected_image)
            if image_response.status_code == 200:
                st.download_button("📥 Download Image", image_response.content, f"{content_type.replace(' ', '_')}_{topic.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.jpg", "image/jpeg")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        content_with_metadata = f"<!-- Generated on {timestamp} -->\n{st.session_state.generated_output}"
        st.download_button("📄 Download TXT", content_with_metadata.encode('utf-8'), f"{content_type.replace(' ', '_')}_{topic.replace(' ', '_')}_{timestamp}.txt")
        st.download_button("🛠️ Download HTML", content_with_metadata.encode('utf-8'), f"{content_type.replace(' ', '_')}_{topic.replace(' ', '_')}_{timestamp}.html")
        
        if st.button("⭐ Save to Favorites"):
            from favorites import save_favorite
            if user and save_favorite(supabase, user.id, user.email, st.session_state.generated_output, topic):
                st.success("Saved to favorites!")