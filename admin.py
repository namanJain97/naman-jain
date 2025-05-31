import streamlit as st
from supabase import Client
import pandas as pd
from datetime import date, datetime, time

def render_admin_dashboard(supabase: Client):
    st.title("Admin Dashboard")
    
    # Total Users
    users = supabase.table("users").select("id").execute()
    total_users = len(users.data)
    st.metric("Total Users", total_users)
    
    # Daily Content Generations
    today = date.today()
    start_of_day = datetime.combine(today, time.min).isoformat() + "Z"
    end_of_day = datetime.combine(today, time.max).isoformat() + "Z"
    usage = supabase.table("usage").select("id").gte("created_at", start_of_day).lte("created_at", end_of_day).execute()
    daily_generations = len(usage.data)
    st.metric("Daily Generations", daily_generations)
    
    # Plan Distribution
    plans = supabase.table("users").select("plan").execute()
    plan_counts = pd.Series([user["plan"] for user in plans.data]).value_counts()
    st.write("Plan Distribution")
    
    # Use st.bar_chart for Plan Distribution
    plan_df = pd.DataFrame({
        "Plan Type": plan_counts.index,
        "Number of Users": plan_counts.values
    }).set_index("Plan Type")
    st.bar_chart(plan_df, color="#4CAF50")  # Green color for the chart
    
    # Referral Statistics
    referrals = supabase.table("referrals").select("referrer_id").execute()
    total_referrals = len(referrals.data)
    referrer_counts = pd.Series([ref["referrer_id"] for ref in referrals.data]).value_counts()
    
    # Get usernames for top referrers
    top_referrers = {}
    for referrer_id, count in referrer_counts.head(5).items():
        user_data = supabase.table("users").select("username").eq("id", referrer_id).execute()
        if user_data.data:
            top_referrers[user_data.data[0]["username"]] = count
    
    st.metric("Total Referrals", total_referrals)
    st.write("Top Referrers")
    
    # Use st.bar_chart for Top Referrers
    if top_referrers:
        referrer_df = pd.DataFrame({
            "Referrer Username": list(top_referrers.keys()),
            "Number of Referrals": list(top_referrers.values())
        }).set_index("Referrer Username")
        st.bar_chart(referrer_df, color="#1DA1F2")  # Twitter blue color for the chart
    else:
        st.write("No referrals yet.")
        