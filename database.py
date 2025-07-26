import streamlit as st
import time as time_module  # Renamed to avoid conflict
from datetime import date, datetime, time
from supabase import Client
from auth import generate_referral_code, check_referral_code_unique

def save_user(supabase: Client, user_id, email, username, full_name, referral_code=None):
    try:
        referral_code = referral_code if referral_code else generate_referral_code()
        while not check_referral_code_unique(supabase, referral_code):
            referral_code = generate_referral_code()
        data = {
            "id": user_id,
            "email": email,
            "username": username.lower(),
            "full_name": full_name,
            "plan": "free",
            "referral_code": referral_code,
            "extra_generations": 0
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = supabase.table("users").insert(data).execute()
                if response.data:
                    return True
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error(f"Failed to save user data after {max_retries} attempts: {str(e)}")
                    return False
                time_module.sleep(1)
        return False
    except Exception as e:
        st.error(f"Failed to save user data: {str(e)}")
        return False

def get_user_plan(supabase: Client, user_id):
    try:
        response = supabase.table("users").select("plan").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["plan"]
        return "free"
    except Exception as e:
        st.error(f"Error retrieving user plan: {str(e)}")
        return "free"

def get_extra_generations(supabase: Client, user_id):
    try:
        response = supabase.table("users").select("extra_generations").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["extra_generations"]
        return 0
    except Exception as e:
        st.error(f"Error retrieving extra generations: {str(e)}")
        return 0

def save_usage(supabase: Client, user_id, email, content_type):
    try:
        data = {
            "user_id": user_id,
            "email": email,
            "content_type": content_type
        }
        response = supabase.table("usage").insert(data).execute()
        return bool(response.data)
    except Exception as e:
        st.error(f"Failed to save usage: {str(e)}")
        return False

def get_daily_usage(supabase: Client, user_id):
    try:
        today = date.today()
        start_of_day = datetime.combine(today, time.min).isoformat() + "Z"
        end_of_day = datetime.combine(today, time.max).isoformat() + "Z"
        response = supabase.table("usage").select("id").eq("user_id", user_id).gte("created_at", start_of_day).lte("created_at", end_of_day).execute()
        return len(response.data)
    except Exception as e:
        st.error(f"Error retrieving daily usage: {str(e)}")
        return 0

def check_usage_limit(supabase: Client, user_id):
    plan = get_user_plan(supabase, user_id)
    daily_usage = get_daily_usage(supabase, user_id)
    extra_generations = get_extra_generations(supabase, user_id)
    if plan == "pro":
        limit = 30
    else:
        limit = 3
    total_available = limit + extra_generations
    can_generate = daily_usage < total_available
    remaining = max(0, total_available - daily_usage)
    return can_generate, daily_usage, total_available, remaining