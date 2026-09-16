"""
pages/5_About.py — Educational & User-Oriented Information about HastaAI
Public Page: Accessible without login.
"""

import streamlit as st
from utils.helpers import render_brand_header, inject_custom_css

st.set_page_config(
    page_title="About — HastaAI",
    page_icon="assets/favicon.png",
    layout="wide",
)

inject_custom_css()
render_brand_header("About")

st.markdown(
    """
    <div style="max-width: 900px; margin: 0 auto;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Heritage Meets Artificial Intelligence
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.3rem; margin: 0.2rem 0 1.5rem 0;">
            About HastaAI
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

content_col, visual_col = st.columns([1.6, 0.8], gap="large")

with content_col:
    st.markdown(
        """
        <div class="hasta-card" style="margin-bottom: 2rem;">
            <div class="card-title">What are Hasta Mudras?</div>
            <p class="card-desc">
                <strong>Hasta Mudras</strong> are precise, expressive hand and finger gestures that form the bedrock of Indian classical performing arts and spiritual iconography. In classical dance—such as Bharatanatyam, Kathakali, Kuchipudi, and Odissi—mudras are not merely decorative movements; they constitute a sophisticated, highly codified visual language (<em>Angika Abhinaya</em>) capable of expressing complex narratives, poetry, deities, elements of nature, and emotional states.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hasta-card" style="margin-bottom: 2rem;">
            <div class="card-title">Why are Hasta Mudras Important?</div>
            <p class="card-desc">
                Codified centuries ago in master treatises including the <strong>Natyashastra</strong> of Sage Bharata and the <strong>Abhinaya Darpana</strong> of Nandikeshvara, the 28 Asamyuta (single-hand) gestures represent a vital link to India's intangible cultural heritage. Mastering them requires disciplined finger placement, joint angles, and subtle spatial tension. Without accessible, objective feedback, practitioners often struggle to verify whether their finger alignments match traditional standards during independent practice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hasta-card" style="margin-bottom: 2rem;">
            <div class="card-title">What Problem Does This Platform Solve?</div>
            <p class="card-desc">
                Traditional classical dance training requires continuous personal instruction from a Guru. However, during daily home rehearsal, practitioners lack immediate, objective verification. <strong>HastaAI</strong> bridges this gap by acting as an intelligent digital rehearsal companion. By providing instant joint-level feedback and continuous performance analytics, users can refine their technique, build muscle memory, and track their artistic progress over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with visual_col:
    st.markdown(
        """
        <div class="hasta-card" style="text-align: center; margin-bottom: 1.5rem;">
            <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
                Codified Traditions
            </div>
            <div class="card-title" style="margin-top: 0.5rem;">28 Classical Mudras</div>
            <p class="card-desc" style="font-size: 0.88rem;">
                Based on the authoritative 28 Asamyuta Hasta Mudras defined in the Sanskrit text <em>Abhinaya Darpana</em>.
            </p>
            <div style="margin-top: 1rem; padding: 0.6rem; background: #FAF8F5; border-radius: 8px; font-size: 0.82rem; color: #722F37; font-weight: 600;">
                Single-Hand Classical Gestures
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hasta-card" style="text-align: center;">
            <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
                Strict Privacy
            </div>
            <div class="card-title" style="margin-top: 0.5rem;">Privacy by Design</div>
            <p class="card-desc" style="font-size: 0.88rem;">
                All computer vision analysis occurs in real time. Video streams are never recorded, transmitted to external servers, or permanently stored.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider" style="margin: 2rem 0;" />', unsafe_allow_html=True)

# ── HOW RECOGNITION WORKS AT A HIGH LEVEL ─────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            High-Level Recognition Architecture
        </div>
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 1.9rem; margin-top: 0.3rem;">
            How AI Recognition Works
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

flow_c1, flow_c2, flow_c3, flow_c4, flow_c5, flow_c6 = st.columns(6)

with flow_c1:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">1</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">Camera</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">Captures user's hand video stream</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with flow_c2:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">2</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">Hand Detection</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">MediaPipe locates hand region</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with flow_c3:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">3</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">21 Landmarks</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">Extracts 3D coordinates & scales</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with flow_c4:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">4</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">Feature Engine</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">Measures angles & pinch distances</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with flow_c5:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">5</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">Mudra Match</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">Temporal voting & confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with flow_c6:
    st.markdown(
        """
        <div class="hasta-card step-flow-card" style="text-align: center;">
            <div class="step-badge">6</div>
            <div style="font-weight: 700; color: #722F37; font-size: 0.9rem;">Analytics</div>
            <div style="font-size: 0.78rem; color: #5A5D5A; margin-top: 0.3rem;">Records progress & trends</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider" style="margin: 2.5rem 0;" />', unsafe_allow_html=True)

# ── PRIVACY POLICY ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background: #FFFFFF; border: 1px solid rgba(197, 160, 89, 0.3); border-radius: 14px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
        <h3 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 1.3rem; margin-bottom: 0.6rem;">
            User Privacy & Data Ethics
        </h3>
        <p style="font-size: 0.95rem; line-height: 1.7; color: #5A5D5A;">
            HastaAI strictly respects user privacy. All video capture and neural landmark extraction execute locally within your system environment. Only numerical session metadata—such as session duration, identified mudra name, and calculated confidence scores—are recorded in the local database to generate your practice analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
