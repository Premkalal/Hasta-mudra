"""
pages/2_Explore_Mudras.py — Public Educational Mudra Library for HastaAI
Public Page: Accessible without login.
"""

from pathlib import Path
import streamlit as st
from db.database import get_all_mudras_db
from utils.helpers import render_brand_header, inject_custom_css
from utils.auth import is_authenticated

st.set_page_config(
    page_title="Explore Mudras — HastaAI",
    page_icon="🖐️",
    layout="wide",
)

inject_custom_css()
render_brand_header("Explore Mudras")

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Natyashastra & Abhinaya Darpana Reference
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
            Classical Asamyuta Hasta Mudra Library
        </h1>
        <p style="color: #5A5D5A; font-size: 1.05rem;">
            Explore the 28 classical single-hand gestures. Learn their Sanskrit roots, iconographic significance, and exact geometric instructions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Search & Filter Controls ──────────────────────────────────────────────────
all_mudras = get_all_mudras_db()

c_search, c_filter, c_count = st.columns([2, 1, 1])
with c_search:
    query = st.text_input("Search Mudras by English or Sanskrit Name", placeholder="e.g. Pataka, पताका, Tripataka...").strip().lower()

with c_filter:
    category = st.selectbox("Category", ["All Asamyuta Mudras (Single Hand)"])

filtered_mudras = all_mudras
if query:
    filtered_mudras = [
        m for m in all_mudras
        if query in m["name"].lower() or query in m["sanskrit"].lower() or query in m["description"].lower() or query in m["significance"].lower()
    ]

with c_count:
    st.markdown(f"<div style='padding-top: 1.8rem; font-weight: 600; color: #722F37;'>{len(filtered_mudras)} Mudras Found</div>", unsafe_allow_html=True)

st.markdown('<hr class="heritage-divider" style="margin: 1.5rem 0;" />', unsafe_allow_html=True)

# ── Grid Layout ───────────────────────────────────────────────────────────────
if not filtered_mudras:
    st.info("No mudras matched your search. Please check the spelling or clear the filter.")
else:
    COLS = 3
    for i in range(0, len(filtered_mudras), COLS):
        cols = st.columns(COLS)
        for col_idx, mudra in enumerate(filtered_mudras[i : i + COLS]):
            with cols[col_idx]:
                st.markdown(
                    f"""
                    <div class="hasta-card mudra-library-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                            <span style="color: #C5A059; font-weight: 700; font-size: 0.95rem;">{mudra['sanskrit']}</span>
                            <span style="font-size: 0.75rem; background: #F3EFEA; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 600; color: #722F37;">{mudra['category']}</span>
                        </div>
                        <div class="card-title" style="font-size: 1.4rem; margin-bottom: 0.4rem;">{mudra['name']}</div>
                        <div class="card-desc" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.8rem;">
                            {mudra['description']}
                        </div>
                        <div style="font-size: 0.85rem; color: #722F37; font-weight: 600; margin-top: auto; padding-top: 0.6rem; border-top: 1px dashed rgba(197, 160, 89, 0.3);">
                            Significance: <span style="color: #5A5D5A; font-weight: 400;">{mudra['significance'][:80]}...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander(f"View Details: {mudra['name']}"):
                    st.markdown(f"**Sanskrit Name:** {mudra['sanskrit']}")
                    st.markdown(f"**Gestural Description:** {mudra['description']}")
                    st.markdown(f"**Cultural Significance:** {mudra['significance']}")
                    st.markdown(f"**Practice Guidance:** {mudra['instructions']}")
                    if is_authenticated():
                        if st.button(f"Practice {mudra['name']}", key=f"btn_prac_{mudra['id']}"):
                            st.switch_page("pages/1_Live_Recognition.py")
                    else:
                        st.caption("Sign in to record a practice session for this mudra.")
