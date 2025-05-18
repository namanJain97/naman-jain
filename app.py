import streamlit as st
import os
from supabase import create_client, Client
from auth import validate_and_refresh_session, handle_authentication
from content_generation import render_content_generation
from favorites import render_favorites
from feedback import render_feedback_form
from database import get_user_plan

# ----- Streamlit Page Config -----
st.set_page_config(page_title="Writeaidaily.com", layout="wide", page_icon="🧑‍🚀")

# ----- Supabase Configuration -----
SUPABASE_URL = "https://qgdnzyrhaezbanbnakfe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZG56eXJoYWV6YmFuYm5ha2ZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyNjk0NjIsImV4cCI6MjA2MTg0NTQ2Mn0.N3ToBQ4UwuQvKGKPok--_cRhw0tYWoSsmoUOiGWrvwE"

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in environment variables.")
    st.stop()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state
if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 Home"
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = False
if 'supabase_user' not in st.session_state:
    st.session_state.supabase_user = None

# Validate session only if user is supposed to be logged in
if st.session_state.get('authentication_status', False):
    validate_and_refresh_session(supabase)

# ----- Hide Default Streamlit Style -----
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----- Custom CSS for Premium Look -----
premium_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f0f2f6;
        color: #333;
    }
    .main-container {
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 900px;
        margin: 2rem auto;
        animation: fadeIn 0.5s ease-in;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: bold;
        transition: background-color 0.3s, transform 0.1s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .delete-btn {
        background-color: #ff4d4d;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-size: 0.85rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s, transform 0.1s;
    }
    .delete-btn:hover {
        background-color: #d9363e;
        transform: scale(1.05);
    }
    .favorite-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.2s;
        position: relative;
    }
    .favorite-card:hover {
        transform: translateY(-5px);
    }
    .favorite-card h3 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    .favorite-card .delete-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
    .sidebar .stSelectbox {
        margin-top: 1rem;
    }
    .sidebar .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        font-size: 0.9rem;
        color: #333;
        margin-top: 2rem;
    }
    .logout-message {
        text-align: center;
        font-size: 1.2rem;
        padding: 1rem;
    }
    .error-message {
        color: #ff4d4d;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    .strength-weak {
        color: #ff4d4d;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    .strength-medium {
        color: #ffcc00;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    .strength-strong {
        color: #4CAF50;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    .responsive-image {
        width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .usage-info {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #333;
    }
    .upgrade-btn {
        background-color: #FFD700;
        color: #333;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: bold;
        transition: background-color 0.3s, transform 0.1s;
    }
    .upgrade-btn:hover {
        background-color: #FFC107;
        transform: scale(1.05);
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
"""
st.markdown(premium_css, unsafe_allow_html=True)

# Handle authentication
authentication_status = handle_authentication(supabase)
user = st.session_state.get('supabase_user')

# ----- Page Content -----
with st.container():
    if st.session_state.menu == "🏠 Home":
        st.title("🧑‍🚀 Writeaidaily.com")
        st.markdown("### Your AI-powered writing companion 🤖")
        st.markdown("""
        ### 🚀 Unleash Your Creativity with AI
        Create SEO-optimized blogs, social media posts, ads, and emails in seconds.
        - 💬 Simple and intuitive  
        - 🎯 High-quality output  
        - ⚡ Fast and efficient  
        """)
        if authentication_status:
            plan = get_user_plan(supabase, user.id)
            if plan == "free":
                st.markdown("""
                You're on the Free Plan (5 generations/day).  
                Upgrade to Pro for 100 generations/day and unlock your full creative potential!  
                <a href="?menu=✍️%20Generate%20Content"><button class="upgrade-btn">Upgrade to Pro 🚀</button></a>
                """, unsafe_allow_html=True)
            else:
                st.markdown("You're on the Pro Plan! Enjoy 100 generations/day and unleash your creativity! 🎉")
            st.markdown("Ready to create? Explore our tools or revisit your saved favorites!")
        else:
            st.markdown("Join us to unlock the full power of AI-driven copywriting.")

    elif st.session_state.menu == "✍️ Generate Content":
        if not authentication_status:
            st.error("Please log in to access this feature.")
        else:
            render_content_generation(supabase, user)

    elif st.session_state.menu == "⭐ Favorites":
        if not authentication_status:
            st.error("Please log in to access this feature.")
        else:
            render_favorites(supabase, user)

    elif st.session_state.menu == "ℹ️ About":
        st.title("ℹ️ About")
        st.markdown("""
        **Writeaidaily.com** is your go-to tool for effortless, high-quality content creation. Powered by advanced AI, it transforms your ideas into SEO-optimized blogs, catchy social media posts, compelling ads, and professional emails in seconds. Built with cutting-edge technology and a passion for creativity, this tool is designed to make your writing process faster, easier, and more effective.

        **Built with:**  
        - 🤖 LLaMA 3.3 70B Versatile model via Groq API for intelligent content generation  
        - 🎨 Streamlit for a sleek, user-friendly interface  
        - 📸 Unsplash for inspiring, high-quality images  

        **Developed by Naman Jain** 🚀 – Bringing AI to your creative fingertips.
        """)
        st.caption("Version 1.0 | Crafted with ❤️ for creators")

        render_feedback_form(supabase, user)

# Footer
st.markdown("<div class='footer'>© 2025 Writeaidaily.com | Developed by Naman Jain 🚀</div>", unsafe_allow_html=True)
