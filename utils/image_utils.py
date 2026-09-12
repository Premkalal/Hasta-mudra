"""
utils/image_utils.py — OpenCV / image helper functions.
"""

import cv2
import numpy as np
from pathlib import Path


def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize a BGR frame to (width, height)."""
    return cv2.resize(frame, (width, height))


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """Convert BGR (OpenCV default) to RGB (Streamlit / PIL default)."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def overlay_text(
    frame: np.ndarray,
    text: str,
    position: tuple = (10, 40),
    font_scale: float = 1.0,
    color: tuple = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """Draw white-backed text onto a frame (in-place)."""
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA,
    )
    return frame


def load_image(path: str) -> np.ndarray | None:
    """Load an image from disk; returns None if file not found."""
    p = Path(path)
    if not p.exists():
        return None
    return cv2.imread(str(p))


def save_snapshot(frame: np.ndarray, out_dir: str, filename: str) -> str:
    """Save a BGR frame as JPEG. Returns the saved file path."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fp = str(out / filename)
    cv2.imwrite(fp, frame)
    return fp
