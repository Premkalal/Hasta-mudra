"""
utils/auth.py — Authentication & Session Management for HastaAI
Handles:
- Password hashing (PBKDF2-HMAC-SHA256 with cryptographically secure salt)
- Input validation (email regex, password length, password matching)
- Session state management (login, logout, active user)
- Protected route redirection / guard
- Google OAuth architecture and environment configuration
"""

import os
import re
import hashlib
import secrets
from typing import Optional, Tuple, Dict, Any
import streamlit as st
from db.database import create_user, get_user_by_email, get_user_by_id


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a 16-byte random salt."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plain password against the stored PBKDF2 hash."""
    try:
        algorithm, iterations_str, salt, expected_key_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        test_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return secrets.compare_digest(test_key.hex(), expected_key_hex)
    except Exception:
        return False


# ── Validation ────────────────────────────────────────────────────────────────

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_registration(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
    """Validate registration fields."""
    if not name or len(name.strip()) < 2:
        return False, "Full Name must be at least 2 characters."
    if not email or not EMAIL_REGEX.match(email.strip()):
        return False, "Please enter a valid email address."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, ""


# ── Session State Helpers ─────────────────────────────────────────────────────

def init_auth_state():
    """Ensure authentication keys are initialized in session state."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False


def is_authenticated() -> bool:
    """Check if the current session has an authenticated user."""
    init_auth_state()
    return bool(st.session_state.authenticated and st.session_state.user)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return the active user dictionary, or None."""
    init_auth_state()
    return st.session_state.user


def login_user(user: Dict[str, Any]):
    """Set the authenticated user session."""
    init_auth_state()
    # Strip password hash for security in session state
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    st.session_state.user = safe_user
    st.session_state.authenticated = True


def logout_user():
    """Clear user session completely."""
    st.session_state.user = None
    st.session_state.authenticated = False
    if "session_id" in st.session_state:
        st.session_state.session_id = None
    if "running" in st.session_state:
        st.session_state.running = False


def require_auth(page_name: str = "this page") -> bool:
    """
    Guard for protected pages.
    Returns True if authenticated, else renders an alert and returns False.
    """
    if not is_authenticated():
        st.warning(f"🔒 Access to {page_name} requires you to sign in.")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Go to Sign In", key="guard_login_btn"):
                st.switch_page("pages/6_Authentication.py")
        return False
    return True


# ── Google OAuth Architecture ─────────────────────────────────────────────────

def _get_secret(key: str, default: str = "") -> str:
    """Safely retrieve a Streamlit secret, returning default if no secrets.toml exists."""
    try:
        return st.secrets.get(key, default) or default
    except Exception:
        return default


def is_google_oauth_configured() -> bool:
    """Check if Google OAuth client ID is configured in env or secrets."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID") or _get_secret("GOOGLE_CLIENT_ID")
    return bool(client_id and client_id.strip())


def get_google_auth_config() -> Dict[str, str]:
    """Retrieve Google OAuth configuration."""
    return {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID") or _get_secret("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET") or _get_secret("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501/pages/6_Authentication.py"),
    }


def get_google_oauth_url() -> Optional[str]:
    """Generate the OAuth consent URL if configured."""
    config = get_google_auth_config()
    if not config["client_id"]:
        return None
    params = (
        f"client_id={config['client_id']}"
        f"&redirect_uri={config['redirect_uri']}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
