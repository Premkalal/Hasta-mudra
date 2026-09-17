"""
core/detection.py — Hand Landmark Detection for HastaAI
Wraps MediaPipe Hand Landmarker to detect 21 3D landmarks in video frames.
Draws aesthetic skeletal overlays matching the HastaAI heritage design palette.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
import cv2
from config import cfg

mp = None

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (9, 10), (10, 11), (11, 12),           # Middle
    (13, 14), (14, 15), (15, 16),          # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17),             # Palm Knuckles
    (0, 5), (0, 17),                       # Palm base
]


@dataclass
class _NormalizedPoint:
    x: float
    y: float
    z: float


class _HandLandmarksCompat:
    def __init__(self, landmarks):
        self.landmark = [_NormalizedPoint(lm.x, lm.y, getattr(lm, "z", 0.0)) for lm in landmarks]


class _ClassificationCompat:
    def __init__(self, label: str, score: float = 1.0):
        self.label = label
        self.score = score


class _HandednessCompat:
    def __init__(self, label: str, score: float = 1.0):
        self.classification = [_ClassificationCompat(label, score)]


class _TasksResultAdapter:
    """Adapts MediaPipe Tasks API output to a uniform structure."""
    def __init__(self, tasks_result):
        if tasks_result and tasks_result.hand_landmarks:
            self.multi_hand_landmarks = [
                _HandLandmarksCompat(lms) for lms in tasks_result.hand_landmarks
            ]
        else:
            self.multi_hand_landmarks = None

        if tasks_result and getattr(tasks_result, "handedness", None):
            self.multi_handedness = []
            for category_list in tasks_result.handedness:
                cat = category_list[0] if category_list else None
                label = getattr(cat, "category_name", None) or getattr(cat, "display_name", "Right")
                score = getattr(cat, "score", 1.0)
                self.multi_handedness.append(_HandednessCompat(label, score))
        else:
            self.multi_handedness = None


class HandDetector:
    """
    Detects hands in BGR frames using MediaPipe Hand Landmarker.
    Automatically initializes using the local model asset.
    """

    def __init__(self):
        global mp
        if mp is None:
            import mediapipe as mp
        self.use_legacy = hasattr(mp, "solutions")

        if self.use_legacy:
            self._mp_hands = mp.solutions.hands  # type: ignore[attr-defined]
            self._mp_draw = mp.solutions.drawing_utils  # type: ignore[attr-defined]
            self._mp_style = mp.solutions.drawing_styles  # type: ignore[attr-defined]

            self.hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=cfg.mediapipe.max_num_hands,
                min_detection_confidence=cfg.mediapipe.min_detection_confidence,
                min_tracking_confidence=cfg.mediapipe.min_tracking_confidence,
                model_complexity=cfg.mediapipe.model_complexity,
            )
        else:
            # Modern MediaPipe Tasks API
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            model_path = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"
            if not model_path.exists():
                import urllib.request
                model_path.parent.mkdir(parents=True, exist_ok=True)
                url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
                urllib.request.urlretrieve(url, str(model_path))

            base_options = python.BaseOptions(model_asset_path=str(model_path))
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=cfg.mediapipe.max_num_hands,
                min_hand_detection_confidence=cfg.mediapipe.min_detection_confidence,
                min_hand_presence_confidence=cfg.mediapipe.min_tracking_confidence,
                min_tracking_confidence=cfg.mediapipe.min_tracking_confidence,
                running_mode=vision.RunningMode.IMAGE,
            )
            self.hands = vision.HandLandmarker.create_from_options(options)

    def detect(self, bgr_frame):
        """Run hand detection on a BGR OpenCV frame."""
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        if self.use_legacy:
            rgb.flags.writeable = False
            results = self.hands.process(rgb)
            rgb.flags.writeable = True
            return results
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)  # type: ignore[attr-defined]
            raw_result = self.hands.detect(mp_image)
            return _TasksResultAdapter(raw_result)

    def draw(self, frame, results):
        """
        Draw landmark skeleton using the HastaAI palette:
        - Deep maroon / wine joint nodes (BGR: 55, 29, 114)
        - Muted gold bone connections (BGR: 70, 160, 212)
        - Highlighted fingertips
        """
        annotated = frame.copy()
        if not (results and results.multi_hand_landmarks):
            return annotated

        h, w = annotated.shape[:2]
        for hand_lms in results.multi_hand_landmarks:
            points = [(int(pt.x * w), int(pt.y * h)) for pt in hand_lms.landmark]

            # Draw bones (Muted Gold: BGR (89, 160, 212))
            for start_idx, end_idx in HAND_CONNECTIONS:
                if start_idx < len(points) and end_idx < len(points):
                    cv2.line(annotated, points[start_idx], points[end_idx], (89, 160, 212), 3, cv2.LINE_AA)

            # Draw joint nodes
            for idx, pt in enumerate(points):
                if idx in [4, 8, 12, 16, 20]:
                    # Fingertips: Wine/Maroon with gold center
                    cv2.circle(annotated, pt, 6, (55, 29, 114), -1, cv2.LINE_AA)
                    cv2.circle(annotated, pt, 3, (120, 210, 255), -1, cv2.LINE_AA)
                else:
                    # Inner joints
                    cv2.circle(annotated, pt, 4, (55, 29, 114), -1, cv2.LINE_AA)
                    cv2.circle(annotated, pt, 2, (250, 250, 250), -1, cv2.LINE_AA)

        return annotated

    def hand_detected(self, results) -> bool:
        """Returns True if at least one hand was found."""
        return bool(results and results.multi_hand_landmarks)

    def release(self):
        """Close the MediaPipe graph/landmarker."""
        if self.hands and hasattr(self.hands, "close"):
            self.hands.close()
