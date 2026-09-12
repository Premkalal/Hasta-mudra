"""
pages/6_Authentication.py — Sign In and Registration for HastaAI
"""

import streamlit as st
from db.database import create_user, get_user_by_email
from utils.auth import (
    hash_password,
    verify_password,
    validate_registration,
    login_user,
    is_authenticated,
)
from utils.helpers import render_brand_header, inject_custom_css

st.set_page_config(
    page_title="Sign In / Register — HastaAI",
    page_icon="🖐️",
    layout="centered",
)

inject_custom_css()
render_brand_header("Authentication")

if is_authenticated():
    user = st.session_state.user
    st.success(f"You are currently signed in as **{user.get('name', 'Student')}** ({user.get('email')}).")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/0_Dashboard.py")
    with col2:
        if st.button("Sign Out", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()
    st.stop()

# ── Tabs for Login & Register ──────────────────────────────────────────────────
tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

with tab_login:
    st.markdown("<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Welcome Back</h2>", unsafe_allow_html=True)
    st.caption("Sign in to access your dashboard, live recognition, and practice analytics.")

    with st.form("login_form", clear_on_submit=False):
        login_email = st.text_input("Email Address", placeholder="e.g. dancer@example.com").strip()
        login_password = st.text_input("Password", type="password", placeholder="Enter your password")
        remember_me = st.checkbox("Remember me on this browser", value=True)
        login_submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

    if login_submitted:
        if not login_email or not login_password:
            st.error("Please enter both email and password.")
        else:
            user_record = get_user_by_email(login_email)
            if not user_record:
                st.error("No account found with this email address. Please register.")
            elif not verify_password(login_password, user_record["password_hash"]):
                st.error("Incorrect password. Please verify and try again.")
            else:
                login_user(user_record)
                st.success(f"Welcome back, {user_record['name']}! Redirecting to Dashboard...")
                st.switch_page("pages/0_Dashboard.py")

    st.markdown('<hr class="heritage-divider" style="margin: 1.5rem 0;" />', unsafe_allow_html=True)
    st.caption("For rapid testing or academic project demonstration:")
    if st.button("⚡ Continue with Student Demo Profile", key="demo_login_btn", use_container_width=True):
        demo_email = "demo.dancer@hastaai.org"
        demo_user = get_user_by_email(demo_email)
        if not demo_user:
            demo_pw_hash = hash_password("DemoPassword123")
            demo_uid = create_user("Devika Natarajan", demo_email, demo_pw_hash, "demo")
            demo_user = {"id": demo_uid, "name": "Devika Natarajan", "email": demo_email, "auth_provider": "demo"}
        login_user(demo_user)
        st.success("Signed in with Student Demo Profile! Redirecting...")
        st.switch_page("pages/0_Dashboard.py")

with tab_register:
    st.markdown("<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Create Student Account</h2>", unsafe_allow_html=True)
    st.caption("Join HastaAI to track and master the 28 classical Asamyuta Hasta Mudras.")

    with st.form("register_form", clear_on_submit=False):
        reg_name = st.text_input("Full Name", placeholder="e.g. Ananya Sharma").strip()
        reg_email = st.text_input("Email Address", placeholder="e.g. ananya@example.com").strip()
        reg_password = st.text_input("Password (min. 6 characters)", type="password", placeholder="Choose a secure password")
        reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        reg_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

    if reg_submitted:
        is_valid, err_msg = validate_registration(reg_name, reg_email, reg_password, reg_confirm)
        if not is_valid:
            st.error(err_msg)
        else:
            existing = get_user_by_email(reg_email)
            if existing:
                st.error("An account with this email address already exists. Please sign in.")
            else:
                pw_hash = hash_password(reg_password)
                user_id = create_user(reg_name, reg_email, pw_hash, "local")
                if user_id:
                    new_user = {"id": user_id, "name": reg_name, "email": reg_email, "auth_provider": "local"}
                    login_user(new_user)
                    st.success("Account created successfully! Redirecting to Dashboard...")
                    st.switch_page("pages/0_Dashboard.py")
                else:
                    st.error("Registration failed due to a database error. Please try again.")
