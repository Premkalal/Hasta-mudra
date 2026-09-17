"""
app.py — HastaAI Application Entry Point & Public Landing Page
Run with:  streamlit run app.py
"""

import streamlit as st
from db import init_db, get_all_mudras_db
from utils.helpers import render_brand_header, inject_custom_css
from utils.auth import is_authenticated, get_current_user

# ── App Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HastaAI — Classical Hasta Mudra AI Recognition & Analytics",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Startup DB initialization
init_db()
inject_custom_css()
render_brand_header("Home")

# ── Sidebar Status & Session ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family: Cinzel; font-size: 1.15rem; color: #722F37; font-weight: 700; margin-bottom: 0.5rem;'>HastaAI Session</div>", unsafe_allow_html=True)
    user = get_current_user()
    if is_authenticated() and user is not None:
        if user.get("auth_provider") == "guest":
            st.info("Active: **Guest Session**\n\nYour practice analytics are isolated to this session.")
        else:
            st.success(f"Signed in as **{user.get('name', 'User')}**")
        if st.button("Sign Out", key="sidebar_logout_btn", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()
    else:
        st.caption("Browsing as guest visitor.")
        if st.button("Sign In / Register", key="sidebar_signin_btn", use_container_width=True):
            st.switch_page("pages/6_Authentication.py")

# ── HERO SECTION ──────────────────────────────────────────────────────────────
hero_col1, hero_col2 = st.columns([1.2, 0.8], gap="large")

with hero_col1:
    st.markdown(
        """
        <div class="hero-container" style="padding: 2rem 2.5rem;">
            <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">
                AI-Powered Indian Classical Heritage
            </div>
            <h1 class="hero-headline" style="margin-bottom: 1rem;">
                Discover the Art of Hasta Mudras with AI
            </h1>
            <p class="hero-subtitle">
                Master ancient Indian classical hand gestures through real-time computer vision.
                Practice authentic Asamyuta Mudras, receive immediate joint-precision feedback, and track your dance journey with deep performance analytics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cta_c1, cta_c2 = st.columns([1, 1])
    with cta_c1:
        if st.button("Start Practicing", type="primary"):
            if is_authenticated():
                st.switch_page("pages/1_Live_Recognition.py")
            else:
                st.switch_page("pages/6_Authentication.py")
    with cta_c2:
        if st.button("Explore Mudras", type="secondary"):
            st.switch_page("pages/2_Explore_Mudras.py")

with hero_col2:
    st.markdown(
        """
<div class="hero-showcase-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
        <span class="live-pill"><span class="live-dot"></span> LIVE VISION ENGINE</span>
        <span style="font-size: 0.8rem; color: #C5A059; font-weight: 700; letter-spacing: 0.05em;">NATYASHASTRA AI</span>
    </div>
    <div style="font-family: 'Cinzel', serif; font-size: 1.45rem; font-weight: 700; color: #722F37; margin-bottom: 0.35rem;">
        Asamyuta Mudra Recognition
    </div>
    <div style="font-size: 0.9rem; color: #5A5D5A; margin-bottom: 1.2rem; line-height: 1.6;">
        Real-time 21 3D joint landmark extraction and geometric spatial verification.
    </div>
    <div class="showcase-grid">
        <div class="showcase-item">
            <div class="showcase-num">28</div>
            <div class="showcase-label">Classical Mudras</div>
        </div>
        <div class="showcase-item">
            <div class="showcase-num">21</div>
            <div class="showcase-label">Joint Landmarks</div>
        </div>
        <div class="showcase-item">
            <div class="showcase-num">30</div>
            <div class="showcase-label">FPS Target Rate</div>
        </div>
        <div class="showcase-item">
            <div class="showcase-num">100%</div>
            <div class="showcase-label">Local Privacy</div>
        </div>
    </div>
    <div style="margin-top: 1rem; padding: 0.85rem 1rem; background: #FAF8F5; border-radius: 10px; border-left: 3px solid #C5A059; font-size: 0.85rem; color: #4A4D4A;">
        <strong>Active Gestures:</strong> Pataka, Tripataka, Mushti, Shikhara, Hamsasya, Alapadma & 22 more.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider"/>', unsafe_allow_html=True)

# ── WHY THIS PLATFORM ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">
            Purpose-Built AI System
        </div>
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2rem; margin-top: 0.3rem;">
            Why HastaAI
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

w1, w2, w3, w4 = st.columns(4)

with w1:
    st.markdown(
        """
        <div class="hasta-card why-card">
            <div class="card-title">Real-Time Recognition</div>
            <div class="card-desc">
                Instant computer vision detection extracting 21 3D hand landmarks at up to 30 frames per second using standard webcams.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with w2:
    st.markdown(
        """
        <div class="hasta-card why-card">
            <div class="card-title">Practice Feedback</div>
            <div class="card-desc">
                Rotation-invariant joint angle analysis delivers accurate confidence scores and real-time guidance on finger placement.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with w3:
    st.markdown(
        """
        <div class="hasta-card why-card">
            <div class="card-title">Performance Analytics</div>
            <div class="card-desc">
                Detailed metrics, practice frequency distributions, and confidence trends computed directly from verified practice sessions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with w4:
    st.markdown(
        """
        <div class="hasta-card why-card">
            <div class="card-title">Heritage Learning</div>
            <div class="card-desc">
                Explore Sanskrit nomenclature, cultural significance, and performance instructions rooted in the Natyashastra tradition.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider"/>', unsafe_allow_html=True)

# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">
            Simple & Transparent Pipeline
        </div>
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2rem; margin-top: 0.3rem;">
            How It Works
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(
        """
        <div class="hasta-card step-card" style="text-align: center;">
            <div class="step-badge">1</div>
            <div class="card-title">Position Hand</div>
            <div class="card-desc">
                Open your webcam and position your hand centered inside the frame under clear lighting.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        """
        <div class="hasta-card step-card" style="text-align: center;">
            <div class="step-badge">2</div>
            <div class="card-title">Extract Landmarks</div>
            <div class="card-desc">
                MediaPipe maps 21 key joint coordinates, automatically normalizing 3D scale and palm angle.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s3:
    st.markdown(
        """
        <div class="hasta-card step-card" style="text-align: center;">
            <div class="step-badge">3</div>
            <div class="card-title">Classify Gesture</div>
            <div class="card-desc">
                Geometric engine measures joint angles and finger curl states with temporal smoothing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s4:
    st.markdown(
        """
        <div class="hasta-card step-card" style="text-align: center;">
            <div class="step-badge">4</div>
            <div class="card-title">Track Mastery</div>
            <div class="card-desc">
                Session duration, accuracy score, and confidence trends are logged to your personal profile.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="heritage-divider"/>', unsafe_allow_html=True)

# ── EXPLORE SELECTED HASTA MUDRAS ─────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">
            Authentic Classical Gestures
        </div>
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2rem; margin-top: 0.3rem;">
            Explore Supported Mudras
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch 6 representative mudras from DB
all_db_mudras = get_all_mudras_db()
showcase_names = ["Pataka", "Tripataka", "Mushti", "Shikhara", "Hamsasya", "Alapadma"]
showcase_mudras = [m for m in all_db_mudras if m["name"] in showcase_names]
if not showcase_mudras:
    showcase_mudras = all_db_mudras[:6]

m_cols1 = st.columns(3)
m_cols2 = st.columns(3)

for idx, mudra in enumerate(showcase_mudras[:3]):
    with m_cols1[idx]:
        st.markdown(
            f"""
            <div class="hasta-card mudra-showcase-card">
                <div style="color: #C5A059; font-size: 0.85rem; font-weight: 600;">{mudra['sanskrit']}</div>
                <div class="card-title">{mudra['name']}</div>
                <div class="card-desc" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{mudra['description']}</div>
                <div style="font-size: 0.82rem; color: #722F37; font-weight: 600; margin-top: auto; padding-top: 0.75rem; border-top: 1px dashed rgba(197, 160, 89, 0.3);">
                    Significance: <span style="color: #5A5D5A; font-weight: 400;">{mudra['significance'][:70]}...</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

for idx, mudra in enumerate(showcase_mudras[3:6]):
    with m_cols2[idx]:
        st.markdown(
            f"""
            <div class="hasta-card mudra-showcase-card">
                <div style="color: #C5A059; font-size: 0.85rem; font-weight: 600;">{mudra['sanskrit']}</div>
                <div class="card-title">{mudra['name']}</div>
                <div class="card-desc" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{mudra['description']}</div>
                <div style="font-size: 0.82rem; color: #722F37; font-weight: 600; margin-top: auto; padding-top: 0.75rem; border-top: 1px dashed rgba(197, 160, 89, 0.3);">
                    Significance: <span style="color: #5A5D5A; font-weight: 400;">{mudra['significance'][:70]}...</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='text-align: center; margin-top: 1.5rem;'>", unsafe_allow_html=True)
if st.button("View All 28 Mudras in Library", key="landing_view_all_btn"):
    st.switch_page("pages/2_Explore_Mudras.py")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr class="heritage-divider"/>', unsafe_allow_html=True)

# ── INDIAN HERITAGE SECTION ───────────────────────────────────────────────────
st.markdown(
    """
    <div style="background: #FFFFFF; border: 1px solid rgba(197, 160, 89, 0.35); border-radius: 16px; padding: 2.5rem; margin: 1.5rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">
            Classical Indian Cultural Heritage
        </div>
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; margin-top: 0.4rem; font-size: 1.8rem;">
            The Sacred Language of Hasta Mudras
        </h2>
        <p style="font-size: 1rem; line-height: 1.8; color: #4A4D4A; margin-top: 1rem;">
            In Indian classical dance traditions—including <strong>Bharatanatyam, Kathakali, Kuchipudi, Odissi, and Mohiniyattam</strong>—the hands serve as the primary instruments of narrative expression (<em>Angika Abhinaya</em>). Codified in ancient treatises such as the <strong>Natyashastra</strong> of Bharata Muni and the <strong>Abhinaya Darpana</strong> of Nandikeshvara, the 28 Asamyuta (single-hand) gestures embody a rich visual language capable of conveying divine emotions, nature, actions, and cosmic principles.
        </p>
        <p style="font-size: 1rem; line-height: 1.8; color: #4A4D4A;">
            <strong>HastaAI</strong> bridges this profound living heritage with state-of-the-art computer vision, offering learners, practitioners, and cultural enthusiasts a respectful, precise, and interactive platform to preserve and practice classical artistry.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── FINAL CALL TO ACTION ──────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; padding: 3rem 1.5rem 2rem 1.5rem;">
        <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin-bottom: 0.8rem;">
            Ready to Begin Your Practice?
        </h2>
        <p style="font-size: 1.1rem; color: #5A5D5A; max-width: 550px; margin: 0 auto 1.5rem auto;">
            Step in front of your camera, position your hand, and experience real-time gesture recognition.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

final_c1, final_c2, final_c3 = st.columns([1.5, 1, 1.5])
with final_c2:
    if st.button("Start Practicing Now", key="final_cta_btn", type="primary"):
        if is_authenticated():
            st.switch_page("pages/1_Live_Recognition.py")
        else:
            st.switch_page("pages/6_Authentication.py")

st.markdown(
    """
    <div style="text-align: center; margin-top: 3rem; font-size: 0.85rem; color: #888;">
        HastaAI • AI-Powered Classical Hasta Mudra Recognition & Performance Analytics
    </div>
    """,
    unsafe_allow_html=True,
)
