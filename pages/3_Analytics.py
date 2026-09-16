"""
pages/3_Analytics.py — Performance Analytics for HastaAI
Protected Page: Requires user authentication.
"""

import streamlit as st
import pandas as pd
from utils.auth import require_auth, get_current_user
from utils.helpers import render_brand_header, inject_custom_css
from analytics.session_analytics import (
    get_user_overview_metrics,
    get_confidence_trend_df,
    get_performance_trend_df,
    get_mudra_distribution_df,
    get_recent_sessions_df,
)

st.set_page_config(
    page_title="Performance Analytics — HastaAI",
    page_icon="assets/favicon.png",
    layout="wide",
)

inject_custom_css()
render_brand_header("Performance Analytics")

if not require_auth("Performance Analytics"):
    st.stop()

user = get_current_user()
user_id = user["id"]
user_name = user.get("name", "User")

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Verified Performance Metrics
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
            Practice Analytics & Progress
        </h1>
        <p style="color: #5A5D5A; font-size: 1.05rem;">
            Real-time analytics computed strictly from your verified practice sessions and landmark confidence scores.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metrics = get_user_overview_metrics(user_id)

# ── EMPTY STATE CHECK ─────────────────────────────────────────────────────────
if not metrics["has_data"]:
    st.markdown(
        """
        <div class="hasta-card" style="text-align: center; padding: 4rem 2rem; margin-top: 1rem;">
            <div style="color: #C5A059; font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
                Empty Analytics
            </div>
            <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2rem; margin: 0.5rem 0 1rem 0;">
                No Practice Data Yet
            </h2>
            <p class="card-desc" style="max-width: 500px; margin: 0 auto 1.5rem auto;">
                Complete your first recognition session using your webcam to generate real-time confidence trends, practice distributions, and mastery scores.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("Start First Practice Session", type="primary", key="empty_start_btn"):
            st.switch_page("pages/1_Live_Recognition.py")
    st.stop()

# ── 1. OVERVIEW METRICS ───────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)

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
            <div class="metric-label">Practice Time</div>
            <div class="metric-val">{metrics['total_practice_display']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Mudras Practiced</div>
            <div class="metric-val">{metrics['unique_mudras_practiced']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Avg Confidence</div>
            <div class="metric-val">{metrics['average_confidence']:.0%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m5:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Best Score</div>
            <div class="metric-val">{metrics['best_performance_score']:.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider" style="margin: 2.5rem 0;" />', unsafe_allow_html=True)

# ── 2. CHARTS SECTION ─────────────────────────────────────────────────────────
ch1, ch2 = st.columns(2, gap="large")

with ch1:
    st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.3rem;'>Confidence Trend (%)</h3>", unsafe_allow_html=True)
    conf_df = get_confidence_trend_df(user_id)
    if not conf_df.empty:
        st.line_chart(conf_df.set_index("Date")["Confidence"], color="#722F37")
    else:
        st.caption("Not enough data points yet for confidence trend.")

with ch2:
    st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.3rem;'>Mudra Practice Distribution</h3>", unsafe_allow_html=True)
    dist_df = get_mudra_distribution_df(user_id)
    if not dist_df.empty:
        st.bar_chart(dist_df.set_index("Mudra")["Sessions"], color="#C5A059")
    else:
        st.caption("No mudra session distribution data.")

st.markdown('<hr class="heritage-divider" style="margin: 2.5rem 0;" />', unsafe_allow_html=True)

# ── 3. PERFORMANCE OVER TIME & RECENT SESSIONS ────────────────────────────────
p1, p2 = st.columns([1, 1], gap="large")

with p1:
    st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.3rem;'>Performance Score Trend (0-100)</h3>", unsafe_allow_html=True)
    perf_df = get_performance_trend_df(user_id)
    if not perf_df.empty:
        st.area_chart(perf_df.set_index("Date")["Performance Score"], color="#8C3B45")
    else:
        st.caption("Performance score curve will populate after multiple sessions.")

with p2:
    st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.3rem;'>Recent Activity</h3>", unsafe_allow_html=True)
    recent_df = get_recent_sessions_df(user_id, limit=5)
    if not recent_df.empty:
        st.dataframe(recent_df, hide_index=True)
    else:
        st.caption("No recent sessions available.")
