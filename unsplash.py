import requests
import streamlit as st
import os

UNSPLASH_ACCESS_KEY = "W5RZutueFTHjisfmz75pFCD9w6TS2jIWaoIa0wYMsS8"
PLACEHOLDER_IMAGE = "https://via.placeholder.com/800x400.png?text=No+Image+Found"

@st.cache_data(show_spinner=False)
def get_unsplash_images(query, count=3, collections=None):
    try:
        params = {
            "query": query,
            "client_id": UNSPLASH_ACCESS_KEY,
            "orientation": "landscape",
            "count": count
        }
        if collections:
            params["collections"] = collections

        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params=params,
            timeout=10
        )
        
        if response.status_code == 403:
            st.warning("Rate limited by Unsplash API.")
            return [PLACEHOLDER_IMAGE]
        
        response.raise_for_status()
        data = response.json()
        images = [img["urls"]["regular"] for img in data]
        return images if images else [PLACEHOLDER_IMAGE]
    
    except Exception as e:
        st.error(f"Unsplash error: {str(e)}")
        return [PLACEHOLDER_IMAGE]
    