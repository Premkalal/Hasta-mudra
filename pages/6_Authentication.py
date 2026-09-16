"""
pages/6_Authentication.py — Sign In, Create Account, and Forgot Password for HastaAI
"""

import streamlit as st
from db.database import create_user, get_user_by_email, update_user_password
from utils.auth import (
    hash_password,
    verify_password,
    validate_registration,
    login_user,
    create_guest_session,
    is_authenticated,
)
from utils.helpers import render_brand_header, inject_custom_css

st.set_page_config(
    page_title="Sign In / Register — HastaAI",
    page_icon="assets/favicon.png",
    layout="centered",
)

inject_custom_css()
render_brand_header("Authentication")

if is_authenticated():
    user = st.session_state.user
    st.success(f"You are currently signed in as **{user.get('name', 'User')}** ({user.get('email')}).")
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

# ── Mode toggle for Forgot Password ──────────────────────────────────────────
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "signin"

# ── FORGOT PASSWORD VIEW ──────────────────────────────────────────────────────
if st.session_state.auth_mode == "forgot":
    st.markdown(
        "<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Reset Password</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Enter your registered email address. We will verify if an account exists.")

    with st.form("forgot_form"):
        reset_email = st.text_input("Email Address", placeholder="e.g. dancer@example.com").strip()
        reset_submitted = st.form_submit_button("Check Account", type="primary", use_container_width=True)

    if reset_submitted:
        if not reset_email:
            st.error("Please enter your email address.")
        else:
            import re
            EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
            if not EMAIL_REGEX.match(reset_email):
                st.error("Please enter a valid email address.")
            else:
                user_record = get_user_by_email(reset_email)
                if user_record:
                    # For local auth accounts, allow password reset via new password entry
                    if user_record.get("auth_provider") == "local":
                        st.session_state["reset_email"] = reset_email
                        st.session_state.auth_mode = "reset_password"
                        st.rerun()
                    else:
                        st.info(
                            f"This account uses **{user_record.get('auth_provider', 'external').capitalize()}** "
                            "authentication. Please sign in using your original authentication method."
                        )
                else:
                    st.error("No account found with this email address.")

    st.markdown('<hr class="heritage-divider" style="margin: 1.5rem 0;" />', unsafe_allow_html=True)
    if st.button("Back to Sign In", key="back_to_signin_btn", use_container_width=True):
        st.session_state.auth_mode = "signin"
        st.rerun()
    st.stop()

# ── RESET PASSWORD VIEW ───────────────────────────────────────────────────────
if st.session_state.auth_mode == "reset_password":
    reset_email = st.session_state.get("reset_email", "")
    st.markdown(
        "<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Set New Password</h2>",
        unsafe_allow_html=True,
    )
    st.caption(f"Creating a new password for **{reset_email}**.")

    with st.form("reset_pw_form"):
        new_pw = st.text_input("New Password (min. 8 characters)", type="password", placeholder="Enter new password")
        confirm_pw = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")
        reset_pw_submitted = st.form_submit_button("Update Password", type="primary", use_container_width=True)

    if reset_pw_submitted:
        if not new_pw or len(new_pw) < 8:
            st.error("Password must contain at least 8 characters.")
        elif new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            new_hash = hash_password(new_pw)
            ok = update_user_password(reset_email.strip(), new_hash)
            if ok:
                st.session_state["pw_reset_success"] = True
                st.session_state.auth_mode = "signin"
                if "reset_email" in st.session_state:
                    del st.session_state["reset_email"]
                st.rerun()
            else:
                st.error("Password update failed. Please ensure the email address is registered.")

    st.markdown('<hr class="heritage-divider" style="margin: 1.5rem 0;" />', unsafe_allow_html=True)
    if st.button("Back to Sign In", key="back_from_reset_btn", use_container_width=True):
        st.session_state.auth_mode = "signin"
        if "reset_email" in st.session_state:
            del st.session_state["reset_email"]
        st.rerun()
    st.stop()

# ── SIGN IN / CREATE ACCOUNT TABS ────────────────────────────────────────────
tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

with tab_login:
    if st.session_state.pop("pw_reset_success", False):
        st.success("Your password has been updated successfully. Please sign in with your new password below.")

    st.markdown(
        "<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Welcome Back</h2>",
        unsafe_allow_html=True,
    )
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
                st.error("No account found with this email address. Please create an account.")
            elif not verify_password(login_password, user_record["password_hash"]):
                st.error("Incorrect password. Please verify your credentials and try again.")
            else:
                login_user(user_record)
                st.success(f"Welcome back, {user_record['name']}.")
                st.switch_page("pages/0_Dashboard.py")

    st.markdown('<hr class="heritage-divider" style="margin: 1.5rem 0;" />', unsafe_allow_html=True)

    fp_col1, fp_col2 = st.columns(2)
    with fp_col1:
        if st.button("Forgot password?", key="forgot_pw_btn", use_container_width=True):
            st.session_state.auth_mode = "forgot"
            st.rerun()
    with fp_col2:
        if st.button("Continue as Guest (Try App)", key="guest_login_btn", use_container_width=True):
            guest_user = create_guest_session()
            st.success("Guest session started with clean analytics. Redirecting to Dashboard...")
            st.switch_page("pages/0_Dashboard.py")

with tab_register:
    st.markdown(
        "<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.6rem;'>Create Your Account</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Join HastaAI to track and master the 28 classical Asamyuta Hasta Mudras.")

    with st.form("register_form", clear_on_submit=False):
        reg_name = st.text_input("Full Name", placeholder="e.g. Ananya Sharma").strip()
        reg_email = st.text_input("Email Address", placeholder="e.g. ananya@example.com").strip()
        reg_password = st.text_input(
            "Password (min. 8 characters)", type="password", placeholder="Choose a secure password"
        )
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
                    st.success("Account created successfully.")
                    st.switch_page("pages/0_Dashboard.py")
                else:
                    st.error("Registration failed due to a database error. Please try again.")
