"""
pages/1_Live_Recognition.py — Real-Time Hasta Mudra Recognition & Practice Session
Protected Page: Requires user authentication.
"""

import time
from datetime import datetime
import cv2
import numpy as np
import streamlit as st

from core.detection import HandDetector
from core.landmarks import LandmarkExtractor
from core.classifier import MudraClassifier, MudraResult
from db.database import (
    start_practice_session,
    end_practice_session,
    log_recognition_result,
    get_mudra_by_name_db,
)
from utils.auth import require_auth, get_current_user
from utils.helpers import render_brand_header, inject_custom_css, bgr_to_rgb, overlay_text

st.set_page_config(
    page_title="Live Recognition — HastaAI",
    page_icon="🖐️",
    layout="wide",
)

inject_custom_css()
render_brand_header("Live Recognition")

if not require_auth("Live Recognition"):
    st.stop()

user = get_current_user()
user_id = user["id"]

# ── Session State Initialisation ──────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None
if "session_detections" not in st.session_state:
    st.session_state.session_detections = []
if "dominant_mudra" not in st.session_state:
    st.session_state.dominant_mudra = None

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Real-Time Computer Vision
        </div>
        <h1 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 2.2rem; margin: 0.2rem 0;">
            Live Hasta Mudra Recognition
        </h1>
        <p style="color: #5A5D5A; font-size: 1.05rem;">
            Click <strong>Open Camera</strong> and hold your hand inside the frame. The AI will extract 21 3D landmarks in real time and evaluate your mudra.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

main_col, side_col = st.columns([1.3, 0.7], gap="large")

with main_col:
    st.markdown("<div class='hasta-card'>", unsafe_allow_html=True)
    ctrl_c1, ctrl_c2 = st.columns(2)
    start_clicked = ctrl_c1.button("🎥 Open Camera", type="primary", disabled=st.session_state.is_running, use_container_width=True)
    stop_clicked = ctrl_c2.button("⏹ Close Camera", disabled=not st.session_state.is_running, use_container_width=True)

    video_placeholder = st.empty()
    status_banner = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

with side_col:
    result_box = st.empty()
    tips_box = st.empty()

# Initial side panel state
if not st.session_state.is_running and not st.session_state.session_detections:
    result_box.markdown(
        """
        <div class="hasta-card" style="text-align: center; padding: 2.5rem 1.5rem;">
            <div style="color: #C5A059; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Awaiting Camera</div>
            <div class="card-title" style="margin-top: 0.5rem;">Ready to Practice</div>
            <p class="card-desc">Click <strong>Open Camera</strong> above to begin real-time mudra recognition.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tips_box.markdown(
        """
        <div class="hasta-card" style="margin-top: 1rem;">
            <div class="card-title" style="font-size: 1rem;">Quick Practice Tips</div>
            <ul style="font-size: 0.88rem; color: #5A5D5A; line-height: 1.7; padding-left: 1.2rem;">
                <li>Ensure clear ambient lighting on your hand.</li>
                <li>Keep the hand centered at roughly 1.5 to 2.5 feet from the lens.</li>
                <li>Try classical mudras such as <strong>Pataka, Tripataka, Mushti, Shikhara, Hamsasya, or Alapadma</strong>.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Start Button Trigger
if start_clicked:
    st.session_state.is_running = True
    st.session_state.session_start_time = time.time()
    st.session_state.session_detections = []
    st.session_state.session_id = start_practice_session(user_id=user_id)
    st.rerun()

# Stop Button Trigger
if stop_clicked:
    st.session_state.is_running = False
    if st.session_state.session_id:
        duration = round(time.time() - (st.session_state.session_start_time or time.time()), 1)
        confs = [d["confidence"] for d in st.session_state.session_detections if d.get("confidence")]
        avg_conf = float(np.mean(confs)) if confs else 0.0
        mudras = [d["name"] for d in st.session_state.session_detections if d.get("detected")]
        dominant = max(set(mudras), key=mudras.count) if mudras else None

        # Compute score out of 100 based on consistency and confidence
        valid_ratio = len(mudras) / max(1, len(st.session_state.session_detections))
        score = round((avg_conf * 70.0) + (valid_ratio * 30.0), 1)

        dominant_db_id = None
        if dominant:
            m_row = get_mudra_by_name_db(dominant)
            if m_row:
                dominant_db_id = m_row["id"]

        end_practice_session(
            session_id=st.session_state.session_id,
            duration=duration,
            average_confidence=avg_conf,
            performance_score=score,
            dominant_mudra_id=dominant_db_id,
        )
        st.success(f"Practice session finalized! Duration: {duration}s | Score: {score}/100")
        st.session_state.session_id = None
        st.rerun()

# Active Video Loop
if st.session_state.is_running:
    status_banner.info("Initializing camera and neural hand landmarker...")

    detector = HandDetector()
    extractor = LandmarkExtractor()
    classifier = MudraClassifier()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        status_banner.error(
            "Unable to open default webcam (index 0). Please check device camera permissions and ensure no other application is using it."
        )
        st.session_state.is_running = False
    else:
        status_banner.success("Camera active. Position hand inside frame.")
        frame_count = 0

        while st.session_state.is_running:
            ret, frame = cap.read()
            if not ret:
                status_banner.warning("Video stream ended or frame unavailable.")
                break

            frame = cv2.flip(frame, 1)  # Mirror view
            h, w = frame.shape[:2]

            results = detector.detect(frame)
            annotated = detector.draw(frame, results)
            hand = extractor.extract(results, frame.shape)

            current_result = None

            if hand:
                current_result = classifier.classify(hand)
                # Overlay Mudra name and confidence on top left of video
                overlay_text(annotated, f"{current_result.name} ({current_result.confidence:.0%})", (20, 45), (55, 29, 114), 1.0, 2)
                
                # Log detection to database periodically (every 5 frames to avoid DB flood)
                if frame_count % 5 == 0 and st.session_state.session_id:
                    m_row = get_mudra_by_name_db(current_result.name)
                    m_id = m_row["id"] if m_row else None
                    log_recognition_result(st.session_state.session_id, m_id, current_result.confidence)
                    st.session_state.session_detections.append({
                        "name": current_result.name,
                        "confidence": current_result.confidence,
                        "detected": current_result.detected,
                    })

                # Render Right Panel with Recognition Details
                badge_cls = "badge-excellent" if current_result.status_label == "Excellent Match" else "badge-good" if current_result.status_label == "Good Match" else "badge-adjusting"
                result_box.markdown(
                    f"""
                    <div class="hasta-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span class="badge-status {badge_cls}">{current_result.status_label}</span>
                            <span style="font-size: 0.85rem; color: #C5A059; font-weight: 700;">{current_result.sanskrit}</span>
                        </div>
                        <div class="card-title" style="font-size: 1.8rem; margin: 0.2rem 0;">{current_result.name}</div>
                        <div style="margin: 0.8rem 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.3rem;">
                                <span style="font-weight: 600; color: #722F37;">Match Confidence</span>
                                <span style="font-weight: 700; color: #722F37;">{current_result.confidence:.0%}</span>
                            </div>
                            <div style="width: 100%; background: #F3EFEA; height: 10px; border-radius: 5px; overflow: hidden;">
                                <div style="width: {int(current_result.confidence * 100)}%; background: #722F37; height: 100%;"></div>
                            </div>
                        </div>
                        <div class="card-desc" style="margin-top: 0.8rem;">
                            <strong>Description:</strong> {current_result.description}
                        </div>
                        <div class="card-desc" style="margin-top: 0.5rem;">
                            <strong>Significance:</strong> {current_result.significance}
                        </div>
                        <div style="margin-top: 0.8rem; padding: 0.8rem; background: #FAF8F5; border-radius: 8px; border-left: 3px solid #C5A059; font-size: 0.85rem; color: #444;">
                            <strong>Practice Guidance:</strong> {current_result.instructions}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                overlay_text(annotated, "Place Hand in Frame", (20, 45), (100, 100, 100), 0.9, 2)
                result_box.markdown(
                    """
                    <div class="hasta-card" style="text-align: center; padding: 2rem;">
                        <span class="badge-status badge-adjusting">Searching</span>
                        <div class="card-title" style="margin-top: 0.8rem;">No Hand Detected</div>
                        <p class="card-desc">Raise your hand into the camera view with your palm facing the lens.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Render video frame
            video_placeholder.image(bgr_to_rgb(annotated), channels="RGB")
            frame_count += 1
            time.sleep(0.03)  # Approx 30 FPS yield

        cap.release()
        detector.release()
