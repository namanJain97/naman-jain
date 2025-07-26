import streamlit as st
import re
import random
import string
from supabase import Client

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_pattern, email))

def validate_name(name):
    if len(name) < 2:
        return False
    name_pattern = r'^[a-zA-Z\s]+$'
    return bool(re.match(name_pattern, name))

def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    username_pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(username_pattern, username))

def check_username_unique(supabase: Client, username):
    try:
        normalized_username = username.lower()
        response = supabase.table("users").select("username").eq("username", normalized_username).execute()
        return len(response.data) == 0
    except Exception as e:
        st.error(f"Error checking username availability: {str(e)}")
        return False

def check_password_strength(password):
    length_ok = len(password) >= 8
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_number = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    score = sum([length_ok, has_upper, has_lower, has_number, has_special])
    
    if score <= 2:
        strength = "weak"
        suggestions = []
        if not length_ok:
            suggestions.append("Make the password at least 8 characters long.")
        if not has_upper:
            suggestions.append("Add an uppercase letter.")
        if not has_lower:
            suggestions.append("Add a lowercase letter.")
        if not has_number:
            suggestions.append("Add a number.")
        if not has_special:
            suggestions.append("Add a special character (e.g., !@#$).")
    elif score <= 4:
        strength = "medium"
        suggestions = ["Consider adding more variety (e.g., special characters, numbers) for a stronger password."]
    else:
        strength = "strong"
        suggestions = []  # No suggestions needed for a strong password
    
    return strength, suggestions

def generate_referral_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def check_referral_code_unique(supabase: Client, referral_code):
    try:
        response = supabase.table("users").select("id").eq("referral_code", referral_code).execute()
        return len(response.data) == 0
    except Exception as e:
        st.error(f"Error checking referral code: {str(e)}")
        return False

def get_user_by_referral_code(supabase: Client, referral_code):
    try:
        response = supabase.table("users").select("*").eq("referral_code", referral_code).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error retrieving user by referral code: {str(e)}")
        return None

def reward_referral(supabase: Client, referrer_id, referred_id):
    try:
        # Insert referral record
        supabase.table("referrals").insert({
            "referrer_id": referrer_id,
            "referred_id": referred_id
        }).execute()
        # Grant 3 extra generations to both referrer and referred user
        for user_id in [referrer_id, referred_id]:
            response = supabase.table("users").select("extra_generations").eq("id", user_id).execute()
            if response.data:
                current_extra = response.data[0]["extra_generations"]
                supabase.table("users").update({"extra_generations": current_extra + 3}).eq("id", user_id).execute()
    except Exception as e:
        st.error(f"Failed to reward referral: {str(e)}")

def validate_and_refresh_session(supabase: Client):
    # Only attempt to validate if tokens exist in session state
    if 'supabase_access_token' not in st.session_state or 'supabase_refresh_token' not in st.session_state:
        st.session_state.authentication_status = False
        return False

    try:
        # Attempt to get the current session
        session = supabase.auth.get_session()
        if session and session.access_token == st.session_state['supabase_access_token']:
            return True  # Session is valid

        # If session is invalid, try to refresh it
        supabase.auth.set_session(
            st.session_state['supabase_access_token'],
            st.session_state['supabase_refresh_token']
        )
        new_session = supabase.auth.get_session()
        if new_session:
            st.session_state['supabase_access_token'] = new_session.access_token
            st.session_state['supabase_refresh_token'] = new_session.refresh_token
            st.session_state.authentication_status = True
            return True
        else:
            raise Exception("Failed to refresh session")
    except Exception as e:
        # If session validation fails, clear session state and log out
        st.error(f"Session validation failed: {str(e)}. Please log in again.")
        supabase.auth.sign_out()
        st.session_state.clear()
        st.session_state.menu = "🏠 Home"
        st.session_state.authentication_status = False
        st.rerun()
        return False

def handle_authentication(supabase: Client):
    with st.sidebar:
        st.markdown("<h2>Writeaidaily.com</h2>", unsafe_allow_html=True)
        authentication_status = st.session_state.get('authentication_status', False)

        if not authentication_status:
            auth_option = st.radio("Choose an option", ["Login", "Signup"], label_visibility="collapsed")
            
            if auth_option == "Signup":
                st.subheader("Create an Account")
                new_email = st.text_input("Email", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_password")
                new_name = st.text_input("Full Name", key="signup_name")
                new_username = st.text_input("Username", key="signup_username")
                referral_code_input = st.text_input("Referral Code (optional)", key="signup_referral_code")

                email_valid = validate_email(new_email)
                if new_email and not email_valid:
                    st.markdown('<p class="error-message">Invalid email format.</p>', unsafe_allow_html=True)

                password_strength, password_suggestions = check_password_strength(new_password) if new_password else ("weak", ["Enter a password."])
                if new_password:
                    if password_strength == "weak":
                        st.markdown('<p class="strength-weak">Password Strength: Weak</p>', unsafe_allow_html=True)
                    elif password_strength == "medium":
                        st.markdown('<p class="strength-medium">Password Strength: Medium</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="strength-strong">Password Strength: Strong</p>', unsafe_allow_html=True)
                    for suggestion in password_suggestions:
                        st.markdown(f'<p class="error-message">{suggestion}</p>', unsafe_allow_html=True)

                name_valid = validate_name(new_name) if new_name else False
                if new_name and not name_valid:
                    st.markdown('<p class="error-message">Name must be at least 2 characters long and contain only letters and spaces.</p>', unsafe_allow_html=True)

                username_valid = validate_username(new_username) if new_username else False
                username_unique = check_username_unique(supabase, new_username) if new_username else False
                if new_username and not username_valid:
                    st.markdown('<p class="error-message">Username must be 3-20 characters long and contain only letters, numbers, underscores, or hyphens.</p>', unsafe_allow_html=True)
                elif new_username and not username_unique:
                    st.markdown('<p class="error-message">Username already taken. Please choose another.</p>', unsafe_allow_html=True)

                form_valid = all([
                    email_valid,
                    password_strength != "weak",
                    name_valid,
                    username_valid,
                    username_unique
                ])

                if st.button("Register", disabled=not form_valid):
                    try:
                        response = supabase.auth.sign_up({
                            "email": new_email,
                            "password": new_password,
                            "options": {"data": {"username": new_username, "full_name": new_name}}
                        })
                        if response.user:
                            from database import save_user
                            if save_user(supabase, response.user.id, new_email, new_username, new_name):
                                st.success(f"Welcome aboard, {new_username}!")
                                if referral_code_input:
                                    referrer = get_user_by_referral_code(supabase, referral_code_input)
                                    if referrer:
                                        reward_referral(supabase, referrer['id'], response.user.id)
                                        st.success("Referral bonus applied! You and your referrer get 3 extra generations.")
                            else:
                                st.error("Signup successful, but failed to save user data. Please try logging in.")
                        else:
                            st.error("Signup failed.")
                    except Exception as e:
                        st.error(f"Signup error: {str(e)}")
            
            else:
                st.subheader("Log In")
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                if st.button("Log In"):
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if response.user and response.session.refresh_token:
                            supabase.auth.set_session(response.session.access_token, response.session.refresh_token)
                            st.session_state['supabase_user'] = response.user
                            st.session_state['supabase_access_token'] = response.session.access_token
                            st.session_state['supabase_refresh_token'] = response.session.refresh_token
                            st.session_state['authentication_status'] = True
                            st.session_state['name'] = response.user.user_metadata.get('full_name', 'User')
                            st.session_state['username'] = response.user.user_metadata.get('username', email)
                            st.rerun()
                        else:
                            st.error("Login failed. Check your credentials.")
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
        else:
            from database import get_user_plan
            name = st.session_state.get('name', 'User')
            user = st.session_state.get('supabase_user')
            plan = get_user_plan(supabase, user.id) if user else "free"
            st.write(f"Welcome, {name}! ({plan.capitalize()} Plan)")
            response = supabase.table("users").select("referral_code").eq("id", user.id).execute()
            if response.data:
                referral_code = response.data[0]["referral_code"]
                st.write(f"Your Referral Code: **{referral_code}**")
                st.write("Share this code with friends to earn 3 extra generations per day.")
            if st.button("Log Out"):
                supabase.auth.sign_out()
                st.session_state.clear()
                st.session_state.menu = "🏠 Home"
                st.session_state.authentication_status = False
                st.rerun()

            menu_options = ["🏠 Home", "✍️ Generate Content", "⭐ Favorites", "ℹ️ About"]
            if user and user.user_metadata.get('username') == "admin":
                menu_options.append("🛠️ Admin Dashboard")
            st.session_state.menu = st.selectbox("Navigation", menu_options, index=menu_options.index(st.session_state.menu))

    return authentication_status
