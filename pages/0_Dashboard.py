"""
pages/0_Dashboard.py — User Practice Dashboard for HastaAI
Protected Page: Requires user authentication.
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.helpers import render_brand_header, inject_custom_css
from analytics.session_analytics import get_user_overview_metrics, get_recent_sessions_df

st.set_page_config(
    page_title="Dashboard — HastaAI",
    page_icon="🖐️",
    layout="wide",
)

inject_custom_css()
render_brand_header("Dashboard")

if not require_auth("User Dashboard"):
    st.stop()

user = get_current_user()
user_id = user["id"]
user_name = user.get("name", "Student")

# ── Welcome Header ─────────────────────────────────────────────────────────────
welcome_col1, welcome_col2 = st.columns([2, 1])
with welcome_col1:
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
                Student Practice Dashboard
            </div>
            <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
                Welcome back, {user_name}
            </h1>
            <p style="color: #5A5D5A; font-size: 1.05rem;">
                Ready for your next classical hasta mudra practice session?
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with welcome_col2:
    st.markdown("<div style='text-align: right; padding-top: 1rem;'>", unsafe_allow_html=True)
    if st.button("Start Recognition", type="primary", key="dash_start_rec_btn"):
        st.switch_page("pages/1_Live_Recognition.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Summary Metrics ────────────────────────────────────────────────────────────
metrics = get_user_overview_metrics(user_id)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Total Sessions</div>
            <div class="metric-val">{metrics['total_sessions']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Mudras Practiced</div>
            <div class="metric-val">{metrics['unique_mudras_practiced']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    conf_display = f"{metrics['average_confidence']:.0%}" if metrics["has_data"] else "—"
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Avg Confidence</div>
            <div class="metric-val">{conf_display}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    best_disp = f"{metrics['best_performance_score']:.0f}" if metrics["has_data"] else "—"
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Best Performance</div>
            <div class="metric-val">{best_disp}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider" style="margin: 2rem 0;" />', unsafe_allow_html=True)

# ── Quick Actions ──────────────────────────────────────────────────────────────
st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.4rem;'>Quick Actions</h3>", unsafe_allow_html=True)
qa1, qa2, qa3 = st.columns(3)

with qa1:
    st.markdown(
        """
        <div class="hasta-card">
            <div class="card-title">Live Recognition</div>
            <div class="card-desc" style="margin-bottom: 1rem;">
                Open the real-time webcam to detect hand landmarks and practice supported mudras with immediate feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Webcam", key="qa_rec"):
        st.switch_page("pages/1_Live_Recognition.py")

with qa2:
    st.markdown(
        """
        <div class="hasta-card">
            <div class="card-title">View Analytics</div>
            <div class="card-desc" style="margin-bottom: 1rem;">
                Explore confidence trends over time, mudra practice distributions, and detailed performance scores.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Analytics", key="qa_analytics"):
        st.switch_page("pages/3_Analytics.py")

with qa3:
    st.markdown(
        """
        <div class="hasta-card">
            <div class="card-title">Explore Mudras</div>
            <div class="card-desc" style="margin-bottom: 1rem;">
                Browse the complete reference library of 28 classical Asamyuta Mudras, their Sanskrit names, and meanings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Browse Library", key="qa_library"):
        st.switch_page("pages/2_Explore_Mudras.py")

st.markdown('<hr class="heritage-divider" style="margin: 2.5rem 0;" />', unsafe_allow_html=True)

# ── Recent Sessions ────────────────────────────────────────────────────────────
st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.4rem;'>Recent Practice Sessions</h3>", unsafe_allow_html=True)

recent_df = get_recent_sessions_df(user_id, limit=5)

if recent_df.empty:
    st.info("No sessions recorded yet. Start your first practice session with the webcam to see your history here!")
else:
    st.dataframe(recent_df, hide_index=True)
    if st.button("View Full Practice History", key="dash_full_history"):
        st.switch_page("pages/4_Practice_History.py")
