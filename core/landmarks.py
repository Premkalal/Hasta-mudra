"""
core/landmarks.py — Landmark Extraction
Converts raw MediaPipe results into clean, normalised feature vectors
that can be consumed by the classifier or saved to a database.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple


# MediaPipe provides 21 landmarks per hand
NUM_LANDMARKS = 21


@dataclass
class HandLandmarks:
    """
    Structured representation of one detected hand's landmarks.

    Attributes:
        raw_points : List of (x, y, z) normalised to [0,1] in image space.
        feature_vector : Flat 63-element array (21 × xyz) used for classification.
        handedness : "Left" or "Right" as reported by MediaPipe.
        wrist      : (x, y) pixel coordinates of the wrist (landmark 0).
    """
    raw_points: List[Tuple[float, float, float]]
    feature_vector: np.ndarray          # shape (63,)
    handedness: str
    wrist: Tuple[float, float]


class LandmarkExtractor:
    """
    Extracts and normalises hand landmarks from MediaPipe results.

    Usage:
        extractor = LandmarkExtractor()
        hand = extractor.extract(results, frame_shape)
    """

    # ── Public API ────────────────────────────────────────────────────────────

    def extract(self, results, frame_shape: Tuple[int, int]) -> Optional[HandLandmarks]:
        """
        Extract landmarks from the FIRST detected hand in results.

        Args:
            results     : Output of HandDetector.detect().
            frame_shape : (height, width) of the source frame — used to
                          convert normalised coords to pixel coords for wrist.

        Returns:
            HandLandmarks dataclass, or None if no hand in results.
        """
        if not (results and results.multi_hand_landmarks):
            return None

        hand_lms   = results.multi_hand_landmarks[0]
        handedness = self._get_handedness(results, index=0)
        h, w       = frame_shape[:2]

        raw_points = [
            (lm.x, lm.y, lm.z) for lm in hand_lms.landmark
        ]

        feature_vector = self._normalise(raw_points)

        wrist = (
            int(hand_lms.landmark[0].x * w),
            int(hand_lms.landmark[0].y * h),
        )

        return HandLandmarks(
            raw_points=raw_points,
            feature_vector=feature_vector,
            handedness=handedness,
            wrist=wrist,
        )

    def extract_all(self, results, frame_shape: Tuple[int, int]) -> List[HandLandmarks]:
        """Extract landmarks for ALL detected hands (up to max_num_hands)."""
        if not (results and results.multi_hand_landmarks):
            return []
        return [
            self._build(results, i, frame_shape)
            for i in range(len(results.multi_hand_landmarks))
        ]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build(self, results, index: int, frame_shape) -> HandLandmarks:
        hand_lms   = results.multi_hand_landmarks[index]
        handedness = self._get_handedness(results, index)
        h, w       = frame_shape[:2]
        raw_points = [(lm.x, lm.y, lm.z) for lm in hand_lms.landmark]
        return HandLandmarks(
            raw_points=raw_points,
            feature_vector=self._normalise(raw_points),
            handedness=handedness,
            wrist=(int(hand_lms.landmark[0].x * w), int(hand_lms.landmark[0].y * h)),
        )

    @staticmethod
    def _get_handedness(results, index: int) -> str:
        try:
            return results.multi_handedness[index].classification[0].label
        except (AttributeError, IndexError):
            return "Unknown"

    @staticmethod
    def _normalise(raw_points: List[Tuple[float, float, float]]) -> np.ndarray:
        """
        Translate landmark coordinates so that the wrist (landmark 0)
        is at the origin, then scale by the palm diagonal so the vector
        is scale-invariant. Returns a flat (63,) float32 array.
        """
        pts = np.array(raw_points, dtype=np.float32)      # (21, 3)

        # Translate: wrist to origin
        pts -= pts[0]

        # Scale: divide by the maximum absolute value (avoid /0)
        scale = np.max(np.abs(pts))
        if scale > 0:
            pts /= scale

        return pts.flatten()                              # (63,)
