"""
pages/7_Profile.py — My Profile & Account Settings for HastaAI
Protected Page: Requires user authentication.
"""

from datetime import datetime
import streamlit as st
from utils.auth import require_auth, get_current_user, logout_user, hash_password, verify_password
from utils.helpers import render_brand_header, inject_custom_css
from db.database import get_user_by_id, update_user_name, update_user_password_by_id
from analytics.session_analytics import get_user_overview_metrics

st.set_page_config(
    page_title="My Profile — HastaAI",
    page_icon="assets/favicon.png",
    layout="wide",
)

inject_custom_css()
render_brand_header("Profile")

if not require_auth("My Profile"):
    st.stop()

current_user = get_current_user()
user_db = get_user_by_id(current_user["id"])
if not user_db:
    user_db = current_user

user_id = user_db["id"]
user_name = user_db.get("name", "User")
user_email = user_db.get("email", "")
is_guest = user_db.get("auth_provider") == "guest"
auth_provider = "Guest (Temporary)" if is_guest else user_db.get("auth_provider", "local").capitalize()
created_at_raw = user_db.get("created_at", "")

try:
    created_date = datetime.fromisoformat(created_at_raw).strftime("%B %d, %Y")
except Exception:
    created_date = "Recently joined"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Account & Preferences
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
            My Profile
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

p_col1, p_col2 = st.columns([1.2, 0.8], gap="large")

with p_col1:
    st.markdown("<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.5rem; margin-bottom: 0.5rem;'>Personal Information</h2>", unsafe_allow_html=True)
    with st.form("update_profile_form"):
        new_name = st.text_input("Full Name", value=user_name)
        st.text_input("Email Address", value=user_email, disabled=True)
        st.text_input("Authentication Method", value=auth_provider, disabled=True)
        st.text_input("Member Since", value=created_date, disabled=True)

        update_submitted = st.form_submit_button("Update Profile Name", type="primary")

    if update_submitted:
        if new_name.strip() and len(new_name.strip()) >= 2:
            ok = update_user_name(user_id, new_name.strip())
            if ok:
                st.session_state.user["name"] = new_name.strip()
                st.success("Your profile name has been updated.")
                st.rerun()
            else:
                st.error("Failed to update profile name. Please try again.")
        else:
            st.error("Please enter a valid name (at least 2 characters).")

    # ── Security & Password Section ───────────────────────────────────────────
    if not is_guest:
        st.markdown("<h2 style='font-family: Cinzel; color: #722F37; font-size: 1.5rem; margin-top: 1.75rem; margin-bottom: 0.5rem;'>Change Password</h2>", unsafe_allow_html=True)
        st.caption("Keep your account secure with a strong password of at least 8 characters.")

        with st.form("change_password_form", clear_on_submit=True):
            current_pw = st.text_input("Current Password", type="password", placeholder="Enter your current password")
            new_pw = st.text_input("New Password (min. 8 characters)", type="password", placeholder="Enter new password")
            confirm_new_pw = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")
            change_pw_submitted = st.form_submit_button("Update Password", type="primary")

        if change_pw_submitted:
            if not current_pw:
                st.error("Please enter your current password.")
            elif not verify_password(current_pw, user_db.get("password_hash", "")):
                st.error("Incorrect current password. Please try again.")
            elif not new_pw or len(new_pw) < 8:
                st.error("New password must be at least 8 characters.")
            elif new_pw != confirm_new_pw:
                st.error("New passwords do not match.")
            else:
                new_hash = hash_password(new_pw)
                updated = update_user_password_by_id(user_id, new_hash)
                if updated:
                    st.success("Your password has been updated successfully in the database!")
                else:
                    st.error("Failed to update password. Please try again.")
    else:
        st.info("You are currently using an isolated Guest Session. Your practice analytics are private to this session.")
        if st.button("Create Permanent Account to Save History", type="primary", use_container_width=True):
            logout_user()
            st.switch_page("pages/6_Authentication.py")

with p_col2:
    metrics = get_user_overview_metrics(user_id)
    st.markdown(
        f"""
        <div class="hasta-card" style="margin-bottom: 1.5rem;">
            <div class="card-title">Practice Summary</div>
            <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.95rem;">
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F3EFEA; padding-bottom: 0.4rem;">
                    <span style="color: #777;">Total Sessions:</span>
                    <strong style="color: #722F37;">{metrics['total_sessions']}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F3EFEA; padding-bottom: 0.4rem;">
                    <span style="color: #777;">Mudras Explored:</span>
                    <strong style="color: #722F37;">{metrics['unique_mudras_practiced']} / 28</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F3EFEA; padding-bottom: 0.4rem;">
                    <span style="color: #777;">Total Practice Time:</span>
                    <strong style="color: #722F37;">{metrics['total_practice_display']}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F3EFEA; padding-bottom: 0.4rem;">
                    <span style="color: #777;">Average Accuracy:</span>
                    <strong style="color: #722F37;">{metrics['average_confidence']:.0%}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hasta-card">
            <div class="card-title">Account Actions</div>
            <p style="font-size: 0.9rem; color: #5A5D5A; margin-bottom: 1.2rem;">
                Sign out of your current session on this browser.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign Out from HastaAI", key="profile_signout_btn", use_container_width=True):
        logout_user()
        st.success("Signed out successfully. Redirecting to Home...")
        st.switch_page("app.py")
