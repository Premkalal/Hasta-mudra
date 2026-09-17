"""
pages/1_Live_Recognition.py — Real-Time Hasta Mudra Recognition & Practice Session
Protected Page: Requires user authentication.
"""

import time
import numpy as np
import streamlit as st

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
    page_icon="assets/favicon.png",
    layout="wide",
)

inject_custom_css()

# ── Hide webrtc device-selector UI & style the video feed ─────────────────────
st.markdown(
    """
    <style>
    /* Hide the source/device selector dropdown from streamlit-webrtc */
    div[data-testid="stCustomComponentV1"] select,
    .webrtc-source-select, .css-source-select { display: none !important; }
    /* Make webrtc video fill its container naturally */
    div[data-testid="stCustomComponentV1"] video {
        border-radius: 12px;
        width: 100% !important;
    }
    div[data-testid="stCustomComponentV1"] { min-height: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

render_brand_header("Live Recognition")

if not require_auth("Live Recognition"):
    st.stop()

user = get_current_user()
assert user is not None
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
if "last_session_summary" not in st.session_state:
    st.session_state.last_session_summary = None
if "live_result" not in st.session_state:
    st.session_state.live_result = None

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
            Select <strong>Start Practice</strong> and position your hand clearly within the camera frame. HastaAI will analyze your gesture in real time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── PRACTICE COMPLETE STATE ────────────────────────────────────────────────────
if st.session_state.last_session_summary and not st.session_state.is_running:
    summary = st.session_state.last_session_summary

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FFFFFF 0%, #FAF4EB 100%);
                    border: 1px solid rgba(197, 160, 89, 0.5);
                    border-radius: 20px;
                    padding: 2.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 8px 30px rgba(114, 47, 55, 0.06);">
            <div style="color: #C5A059; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.3rem;">
                Session Complete
            </div>
            <h2 style="font-family: 'Cinzel', serif; color: #722F37; font-size: 1.9rem; margin: 0 0 1.5rem 0;">
                Practice Summary
            </h2>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: #FFFFFF; border: 1px solid rgba(197,160,89,0.3); border-radius: 12px; padding: 1.1rem; text-align: center;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #C5A059; letter-spacing: 0.06em; margin-bottom: 0.3rem;">Duration</div>
                    <div style="font-family: 'Cinzel', serif; font-size: 1.6rem; font-weight: 700; color: #722F37;">{summary["duration"]}s</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid rgba(197,160,89,0.3); border-radius: 12px; padding: 1.1rem; text-align: center;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #C5A059; letter-spacing: 0.06em; margin-bottom: 0.3rem;">Avg Confidence</div>
                    <div style="font-family: 'Cinzel', serif; font-size: 1.6rem; font-weight: 700; color: #722F37;">{summary["avg_conf"]:.0%}</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid rgba(197,160,89,0.3); border-radius: 12px; padding: 1.1rem; text-align: center;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #C5A059; letter-spacing: 0.06em; margin-bottom: 0.3rem;">Score</div>
                    <div style="font-family: 'Cinzel', serif; font-size: 1.6rem; font-weight: 700; color: #722F37;">{summary["score"]:.0f}<span style="font-size: 1rem; color: #888;">/100</span></div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid rgba(197,160,89,0.3); border-radius: 12px; padding: 1.1rem; text-align: center;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #C5A059; letter-spacing: 0.06em; margin-bottom: 0.3rem;">Dominant Mudra</div>
                    <div style="font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 700; color: #722F37; margin-top: 0.3rem;">{summary["dominant"] or "Mixed"}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    act_c1, act_c2, act_c3 = st.columns([1, 1, 1])
    with act_c1:
        if st.button("Practice Again", type="primary", key="practice_again_btn", use_container_width=True):
            st.session_state.last_session_summary = None
            st.session_state.session_detections = []
            st.session_state.session_id = None
            st.session_state.live_result = None
            st.rerun()
    with act_c2:
        if st.button("View Analytics", key="post_session_analytics_btn", use_container_width=True):
            st.switch_page("pages/3_Analytics.py")
    with act_c3:
        if st.button("Practice History", key="post_session_history_btn", use_container_width=True):
            st.switch_page("pages/4_Practice_History.py")

    st.markdown('<hr class="heritage-divider" style="margin: 2rem 0;" />', unsafe_allow_html=True)

# ── ACTIVE / IDLE PRACTICE INTERFACE ─────────────────────────────────────────
main_col, side_col = st.columns([1.3, 0.7], gap="large")

with main_col:
    ctrl_c1, ctrl_c2 = st.columns(2)
    start_clicked = ctrl_c1.button(
        "Start Practice",
        type="primary",
        disabled=st.session_state.is_running,
        use_container_width=True,
        key="start_practice_btn",
    )
    stop_clicked = ctrl_c2.button(
        "Stop Practice",
        disabled=not st.session_state.is_running,
        use_container_width=True,
        key="stop_practice_btn",
    )

    video_placeholder = st.empty()
    status_banner = st.empty()

with side_col:
    result_box = st.empty()
    tips_box = st.empty()

# Initial side panel state
if not st.session_state.is_running and not st.session_state.session_detections:
    result_box.markdown(
        """
        <div class="hasta-card" style="text-align: center; padding: 2.5rem 1.5rem;">
            <div style="color: #C5A059; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">Awaiting Session</div>
            <div class="card-title" style="margin-top: 0.5rem;">Ready to Practice</div>
            <p class="card-desc">Select <strong>Start Practice</strong> to begin real-time mudra recognition.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tips_box.markdown(
        """
        <div class="hasta-card" style="margin-top: 1rem;">
            <div class="card-title" style="font-size: 1rem;">Practice Guidance</div>
            <ul style="font-size: 0.88rem; color: #5A5D5A; line-height: 1.7; padding-left: 1.2rem; margin-top: 0.5rem;">
                <li>Ensure clear ambient lighting on your hand.</li>
                <li>Position your hand 1.5 to 2.5 feet from the camera lens.</li>
                <li>Try classical mudras such as <strong>Pataka, Tripataka, Mushti, Shikhara, Hamsasya, or Alapadma</strong>.</li>
                <li>Hold each gesture steady for best results.</li>
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
    st.session_state.last_session_summary = None
    st.session_state.live_result = None
    st.session_state.session_id = start_practice_session(user_id=user_id)
    st.rerun()

# Stop Button Trigger
if stop_clicked:
    st.session_state.is_running = False
    if st.session_state.session_id:
        detections = st.session_state.session_detections
        confs = [d["confidence"] for d in detections if d.get("confidence")]

        if not confs:
            # No detections recorded — discard the empty session silently
            from db.database import delete_practice_session
            delete_practice_session(st.session_state.session_id)
            st.session_state.session_id = None
            st.session_state.session_detections = []
            st.warning("No hand detected during the session. Session was not saved.")
        else:
            duration = round(time.time() - (st.session_state.session_start_time or time.time()), 1)
            avg_conf = float(np.mean(confs))
            mudras = [d["name"] for d in detections if d.get("detected")]
            dominant = max(set(mudras), key=mudras.count) if mudras else None

            valid_ratio = len(mudras) / max(1, len(detections))
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

            st.session_state.last_session_summary = {
                "duration": duration,
                "avg_conf": avg_conf,
                "score": score,
                "dominant": dominant,
            }
            st.session_state.session_id = None
    st.rerun()

# ── Active Video Stream ───────────────────────────────────────────────────────
if st.session_state.is_running:
    import cv2
    from core.detection import HandDetector
    from core.landmarks import LandmarkExtractor
    from core.classifier import MudraClassifier

    # Lazy-load ML models once per session
    if "ml_detector" not in st.session_state or st.session_state.ml_detector is None:
        with st.spinner("Loading AI models..."):
            st.session_state.ml_detector = HandDetector()
            st.session_state.ml_extractor = LandmarkExtractor()
            st.session_state.ml_classifier = MudraClassifier()

    detector = st.session_state.ml_detector
    extractor = st.session_state.ml_extractor
    classifier = st.session_state.ml_classifier

    # ── Try OpenCV first (local) then WebRTC (cloud) ──────────────────────────
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        # ── LOCAL PATH: original cv2.VideoCapture loop ─────────────────────
        status_banner.success("Camera active — position your hand within the frame.")
        frame_count = 0

        while st.session_state.is_running:
            ret, frame = cap.read()
            if not ret:
                status_banner.warning("Video stream interrupted. Please stop and try again.")
                break

            frame = cv2.flip(frame, 1)

            results = detector.detect(frame)
            annotated = detector.draw(frame, results)
            hand = extractor.extract(results, frame.shape)

            if hand:
                current_result = classifier.classify(hand)
                overlay_text(
                    annotated,
                    f"{current_result.name} ({current_result.confidence:.0%})",
                    (20, 45),
                    (55, 29, 114),
                    1.0,
                    2,
                )

                if frame_count % 5 == 0 and st.session_state.session_id:
                    m_row = get_mudra_by_name_db(current_result.name)
                    m_id = m_row["id"] if m_row else None
                    log_recognition_result(st.session_state.session_id, m_id, current_result.confidence)
                    st.session_state.session_detections.append({
                        "name": current_result.name,
                        "confidence": current_result.confidence,
                        "detected": current_result.detected,
                    })

                if current_result.status_label == "Excellent Match":
                    badge_cls = "badge-excellent"
                elif current_result.status_label == "Good Match":
                    badge_cls = "badge-good"
                else:
                    badge_cls = "badge-adjusting"

                low_conf_html = ""
                if current_result.confidence < 0.65:
                    low_conf_html = """
                    <div style="margin-top: 0.8rem; padding: 0.7rem 0.9rem; background: #FEF7E6;
                                border-left: 3px solid #C5A059; border-radius: 6px;
                                font-size: 0.83rem; color: #7A5400;">
                        Recognition confidence is low. Try adjusting your hand position or lighting.
                    </div>
                    """

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
                                <div style="width: {int(current_result.confidence * 100)}%; background: linear-gradient(90deg, #722F37, #C5A059); height: 100%; transition: width 0.3s ease;"></div>
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
                        {low_conf_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                overlay_text(annotated, "Position Hand in Frame", (20, 45), (100, 100, 100), 0.9, 2)
                result_box.markdown(
                    """
                    <div class="hasta-card" style="text-align: center; padding: 2rem;">
                        <span class="badge-status badge-adjusting">Searching</span>
                        <div class="card-title" style="margin-top: 0.8rem;">No Hand Detected</div>
                        <p class="card-desc">Position your hand clearly within the camera frame with your palm facing the lens.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            video_placeholder.image(bgr_to_rgb(annotated), channels="RGB")
            frame_count += 1
            time.sleep(0.03)

        cap.release()
        detector.release()

    else:
        # ── CLOUD PATH: WebRTC stream via browser ─────────────────────────────
        cap.release()
        status_banner.info("📷 Browser camera mode — allow camera access when prompted.")

        try:
            import av
            from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

            _frame_counter = {"n": 0}

            class _MudraProcessor(VideoProcessorBase):
                def __init__(self):
                    self._detector = detector
                    self._extractor = extractor
                    self._classifier = classifier
                    self._fc = 0

                def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
                    import cv2 as _cv2
                    bgr = frame.to_ndarray(format="bgr24")
                    bgr = _cv2.flip(bgr, 1)

                    results = self._detector.detect(bgr)
                    annotated = self._detector.draw(bgr, results)
                    hand = self._extractor.extract(results, bgr.shape)

                    if hand:
                        res = self._classifier.classify(hand)
                        overlay_text(annotated, f"{res.name} ({res.confidence:.0%})", (20, 45), (55, 29, 114), 1.0, 2)
                        if self._fc % 5 == 0 and st.session_state.session_id:
                            m_row = get_mudra_by_name_db(res.name)
                            m_id = m_row["id"] if m_row else None
                            log_recognition_result(st.session_state.session_id, m_id, res.confidence)
                            st.session_state.session_detections.append({
                                "name": res.name,
                                "confidence": res.confidence,
                                "detected": res.detected,
                            })
                        st.session_state.live_result = res
                    else:
                        overlay_text(annotated, "Position Hand in Frame", (20, 45), (100, 100, 100), 0.9, 2)
                        st.session_state.live_result = None

                    self._fc += 1
                    rgb = _cv2.cvtColor(annotated, _cv2.COLOR_BGR2RGB)
                    return av.VideoFrame.from_ndarray(rgb, format="rgb24")

            rtc_cfg = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

            with video_placeholder:
                webrtc_streamer(
                    key="hasta_webrtc",
                    video_processor_factory=_MudraProcessor,
                    rtc_configuration=rtc_cfg,
                    media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
                    async_processing=True,
                )

            # Show live result in sidebar
            live = st.session_state.get("live_result")
            if live:
                badge_cls = (
                    "badge-excellent" if live.status_label == "Excellent Match"
                    else "badge-good" if live.status_label == "Good Match"
                    else "badge-adjusting"
                )
                low_conf_html = ""
                if live.confidence < 0.65:
                    low_conf_html = """
                    <div style="margin-top: 0.8rem; padding: 0.7rem 0.9rem; background: #FEF7E6;
                                border-left: 3px solid #C5A059; border-radius: 6px;
                                font-size: 0.83rem; color: #7A5400;">
                        Recognition confidence is low. Try adjusting your hand position or lighting.
                    </div>
                    """
                result_box.markdown(
                    f"""
                    <div class="hasta-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span class="badge-status {badge_cls}">{live.status_label}</span>
                            <span style="font-size: 0.85rem; color: #C5A059; font-weight: 700;">{live.sanskrit}</span>
                        </div>
                        <div class="card-title" style="font-size: 1.8rem; margin: 0.2rem 0;">{live.name}</div>
                        <div style="margin: 0.8rem 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.3rem;">
                                <span style="font-weight: 600; color: #722F37;">Match Confidence</span>
                                <span style="font-weight: 700; color: #722F37;">{live.confidence:.0%}</span>
                            </div>
                            <div style="width: 100%; background: #F3EFEA; height: 10px; border-radius: 5px; overflow: hidden;">
                                <div style="width: {int(live.confidence * 100)}%; background: linear-gradient(90deg, #722F37, #C5A059); height: 100%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        <div class="card-desc" style="margin-top: 0.8rem;"><strong>Description:</strong> {live.description}</div>
                        <div class="card-desc" style="margin-top: 0.5rem;"><strong>Significance:</strong> {live.significance}</div>
                        <div style="margin-top: 0.8rem; padding: 0.8rem; background: #FAF8F5; border-radius: 8px; border-left: 3px solid #C5A059; font-size: 0.85rem; color: #444;">
                            <strong>Practice Guidance:</strong> {live.instructions}
                        </div>
                        {low_conf_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                result_box.markdown(
                    """
                    <div class="hasta-card" style="text-align: center; padding: 2rem;">
                        <span class="badge-status badge-adjusting">Searching</span>
                        <div class="card-title" style="margin-top: 0.8rem;">No Hand Detected</div>
                        <p class="card-desc">Position your hand clearly within the camera frame with your palm facing the lens.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        except ImportError:
            status_banner.error(
                "Camera unavailable. On Streamlit Cloud, ensure `streamlit-webrtc` and `aiortc` "
                "are in requirements.txt."
            )
