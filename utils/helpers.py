"""
utils/helpers.py — Shared UI & Formatting Helpers for HastaAI
"""

from datetime import datetime
from pathlib import Path
from typing import Tuple
import numpy as np
import cv2
import streamlit as st


def inject_custom_css():
    """Inject the global HastaAI Indian heritage + Modern AI stylesheet."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_brand_header(current_page_title: str = ""):
    """Renders the top branding and authentication status bar."""
    user = st.session_state.get("user")

    user_info_html = ""
    if user:
        user_info_html = f"""
        <div style="text-align: right;">
            <div style="font-weight: 600; font-size: 0.95rem; color: #722F37;">{user.get('name', 'Student')}</div>
            <div style="font-size: 0.8rem; color: #777;">{user.get('email', '')}</div>
        </div>
        """
    else:
        user_info_html = """
        <div style="text-align: right;">
            <span style="font-size: 0.85rem; color: #888; font-weight: 500;">Guest Mode</span>
        </div>
        """

    st.markdown(
        f"""
        <div class="brand-header">
            <div>
                <div class="brand-logo-text">HastaAI</div>
                <div class="brand-tagline">Classical Hasta Mudra AI Recognition & Analytics</div>
            </div>
            {user_info_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def timestamp_filename(prefix: str = "session", ext: str = "csv") -> str:
    """Return a timestamped filename, e.g. session_20260910_120000.csv"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


def confidence_bar(confidence: float, width: int = 20) -> str:
    """Return a clean text progress bar for a confidence value in [0, 1]."""
    filled = int(confidence * width)
    return "[" + "█" * filled + "░" * (width - filled) + f"] {confidence:.0%}"


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a float between lo and hi."""
    return max(lo, min(hi, value))


def bgr_to_rgb(bgr_frame: np.ndarray) -> np.ndarray:
    """
    Convert an OpenCV BGR image to RGB for display in Streamlit st.image().
    Returns a copy of the frame in RGB colour order.
    """
    return cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)


def overlay_text(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int],
    color_bgr: Tuple[int, int, int] = (255, 255, 255),
    font_scale: float = 0.9,
    thickness: int = 2,
):
    """
    Draw text onto a video frame with a soft dark shadow for readability.
    Mutates `frame` in-place.
    """
    font = cv2.FONT_HERSHEY_DUPLEX
    shadow_color = (0, 0, 0)
    # Shadow offset
    cv2.putText(frame, text, (position[0] + 2, position[1] + 2), font, font_scale, shadow_color, thickness + 1, cv2.LINE_AA)
    # Foreground text
    cv2.putText(frame, text, position, font, font_scale, color_bgr, thickness, cv2.LINE_AA)
