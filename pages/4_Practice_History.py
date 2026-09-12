"""
pages/4_Practice_History.py — Practice Session History for HastaAI
Protected Page: Requires user authentication.
"""

from datetime import datetime
import pandas as pd
import streamlit as st

from db.database import get_user_sessions, get_session_details, get_session_results
from utils.auth import require_auth, get_current_user
from utils.helpers import render_brand_header, inject_custom_css, timestamp_filename
from analytics.session_analytics import export_session_to_csv

st.set_page_config(
    page_title="Practice History — HastaAI",
    page_icon="🖐️",
    layout="wide",
)

inject_custom_css()
render_brand_header("Practice History")

if not require_auth("Practice History"):
    st.stop()

user = get_current_user()
user_id = user["id"]

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Practice Records
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
            Session History & Export
        </h1>
        <p style="color: #5A5D5A; font-size: 1.05rem;">
            Inspect your past practice sessions, filter by mudra, and export landmark event data to CSV.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

sessions = get_user_sessions(user_id, limit=200)

if not sessions:
    st.markdown(
        """
        <div class="hasta-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="color: #C5A059; font-size: 1rem; font-weight: 700; text-transform: uppercase;">Empty Log</div>
            <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2rem; margin: 0.5rem 0 1rem 0;">
                No Practice Records Found
            </h2>
            <p class="card-desc" style="max-width: 500px; margin: 0 auto 1.5rem auto;">
                Your practice history will appear here after your first session.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("Start Practicing Now", type="primary", key="hist_start_btn"):
            st.switch_page("pages/1_Live_Recognition.py")
    st.stop()

# ── Filter & Search Controls ──────────────────────────────────────────────────
df = pd.DataFrame(sessions)
df["Date"] = pd.to_datetime(df["start_time"]).dt.strftime("%b %d, %Y %I:%M %p")
df["Mudra"] = df["mudra_name"].fillna("Practice Session")
df["Duration"] = df["duration"].apply(lambda d: f"{d:.1f}s")
df["Avg Confidence"] = df["average_confidence"].apply(lambda c: f"{c:.1%}")
df["Score"] = df["performance_score"].apply(lambda s: f"{s:.1f} / 100")

f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

with f_col1:
    search_q = st.text_input("Filter by Mudra Name", placeholder="e.g. Pataka, Mushti...").strip().lower()

with f_col2:
    all_mudra_opts = ["All Mudras"] + sorted([str(m) for m in df["Mudra"].unique() if m])
    selected_filter = st.selectbox("Select Mudra", all_mudra_opts)

with f_col3:
    sort_order = st.selectbox("Sort By Date", ["Newest First", "Oldest First"])

filtered_df = df.copy()

if search_q:
    filtered_df = filtered_df[filtered_df["Mudra"].str.lower().str.contains(search_q)]

if selected_filter != "All Mudras":
    filtered_df = filtered_df[filtered_df["Mudra"] == selected_filter]

if sort_order == "Oldest First":
    filtered_df = filtered_df.iloc[::-1]

st.markdown(f"**Showing {len(filtered_df)} of {len(df)} sessions**")

# Display Table
display_cols = ["id", "Date", "Mudra", "Duration", "Avg Confidence", "Score"]
st.dataframe(
    filtered_df[display_cols].rename(columns={"id": "Session ID"}),
    hide_index=True,
)

st.markdown('<hr class="heritage-divider" style="margin: 2.5rem 0;" />', unsafe_allow_html=True)

# ── Session Inspector & CSV Export ────────────────────────────────────────────
st.markdown("<h3 style='font-family: Cinzel; color: #722F37; font-size: 1.4rem;'>Inspect & Export Session Data</h3>", unsafe_allow_html=True)

inspect_c1, inspect_c2 = st.columns([2, 1])

with inspect_c1:
    session_options = filtered_df["id"].tolist()
    if session_options:
        selected_session_id = st.selectbox(
            "Select Session ID to Inspect",
            options=session_options,
            format_func=lambda s_id: f"Session #{s_id} — {filtered_df.loc[filtered_df['id'] == s_id, 'Date'].values[0]} ({filtered_df.loc[filtered_df['id'] == s_id, 'Mudra'].values[0]})",
        )

        if selected_session_id:
            sess_details = get_session_details(selected_session_id)
            sess_results = get_session_results(selected_session_id)

            if sess_details:
                d1, d2, d3, d4 = st.columns(4)
                d1.metric("Mudra", sess_details["mudra_name"] or "Mixed Practice")
                d2.metric("Duration", f"{sess_details['duration']:.1f}s")
                d3.metric("Avg Confidence", f"{sess_details['average_confidence']:.1%}")
                d4.metric("Score", f"{sess_details['performance_score']:.1f}")

            if sess_results:
                st.markdown(f"**Recognition Data Points ({len(sess_results)} events):**")
                res_df = pd.DataFrame(sess_results)[["id", "timestamp", "mudra_name", "confidence"]]
                res_df["confidence"] = res_df["confidence"].apply(lambda c: f"{c:.1%}")
                st.dataframe(res_df.rename(columns={"id": "Event ID", "timestamp": "Timestamp", "mudra_name": "Recognized Mudra", "confidence": "Confidence"}), hide_index=True)

                # Export CSV button
                csv_bytes = pd.DataFrame(sess_results).to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Session Events as CSV",
                    data=csv_bytes,
                    file_name=f"hastaai_session_{selected_session_id}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No fine-grained landmark detection events recorded for this session.")
