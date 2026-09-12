"""
tests/test_classifier.py — Tests for geometric classifier and temporal smoothing
"""

import pytest
import numpy as np
from core.landmarks import HandLandmarks
from core.classifier import MudraClassifier, MudraResult


def _build_hand(
    thumb_erect=False,
    index_ext=True,
    middle_ext=True,
    ring_ext=True,
    pinky_ext=True,
    thumb_tucked=True,
):
    """
    Build a realistic HandLandmarks object with wrist at (0.5, 0.8) and palm scale 0.25.
    """
    pts = [(0.5, 0.8, 0.0)] * 21
    wrist = (0.5, 0.8, 0.0)
    pts[0] = wrist

    # Thumb: 1(CMC), 2(MCP), 3(IP), 4(TIP)
    if thumb_erect:
        # Extended upright away from palm
        pts[1] = (0.46, 0.76, 0.0)
        pts[2] = (0.42, 0.70, 0.0)
        pts[3] = (0.38, 0.60, 0.0)
        pts[4] = (0.35, 0.48, 0.0)
    elif thumb_tucked:
        # Tucked across palm near index base
        pts[1] = (0.46, 0.75, 0.0)
        pts[2] = (0.44, 0.70, 0.0)
        pts[3] = (0.45, 0.66, 0.0)
        pts[4] = (0.47, 0.62, 0.0)
    else:
        # Natural relaxed thumb
        pts[1] = (0.46, 0.75, 0.0)
        pts[2] = (0.43, 0.70, 0.0)
        pts[3] = (0.42, 0.65, 0.0)
        pts[4] = (0.45, 0.62, 0.0)

    # Fingers definition: (MCP_idx, PIP_idx, DIP_idx, TIP_idx, x_offset, is_extended)
    fingers = [
        (5, 6, 7, 8, 0.45, index_ext),
        (9, 10, 11, 12, 0.50, middle_ext),
        (13, 14, 15, 16, 0.55, ring_ext),
        (17, 18, 19, 20, 0.60, pinky_ext),
    ]

    for mcp, pip, dip, tip, x, ext in fingers:
        pts[mcp] = (x, 0.55, 0.0)
        if ext:
            # Straight extended upwards (y decreases from 0.55 to 0.25)
            pts[pip] = (x, 0.45, 0.0)
            pts[dip] = (x, 0.35, 0.0)
            pts[tip] = (x, 0.25, 0.0)
        else:
            # Curled into palm: PIP at 0.50, TIP folding back to 0.57 (closer to wrist than MCP)
            pts[pip] = (x, 0.50, 0.0)
            pts[dip] = (x, 0.53, 0.05)
            pts[tip] = (x, 0.57, 0.02)

    feature_vec = np.zeros(63, dtype=np.float32)
    return HandLandmarks(
        raw_points=pts,
        feature_vector=feature_vec,
        handedness="Right",
        wrist=(int(wrist[0] * 640), int(wrist[1] * 480)),
    )


@pytest.fixture
def classifier():
    clf = MudraClassifier()
    clf.reset_buffer()
    return clf


def test_classifier_none_hand(classifier):
    res = classifier.classify(None)
    assert res.name == "Unknown"
    assert res.detected is False
    assert res.confidence == 0.0


def test_classifier_pataka(classifier):
    # All 4 fingers extended upright, thumb tucked
    hand = _build_hand(thumb_erect=False, index_ext=True, middle_ext=True, ring_ext=True, pinky_ext=True, thumb_tucked=True)
    res = classifier.classify(hand)
    assert res.name == "Pataka"
    assert res.confidence >= 0.70


def test_classifier_mushti_fist(classifier):
    # Tight fist: all fingers curled, thumb tucked over fingers
    hand = _build_hand(thumb_erect=False, index_ext=False, middle_ext=False, ring_ext=False, pinky_ext=False, thumb_tucked=True)
    res = classifier.classify(hand)
    assert res.name == "Mushti"
    assert res.confidence >= 0.70


def test_classifier_shikhara(classifier):
    # Fist with thumb upright
    hand = _build_hand(thumb_erect=True, index_ext=False, middle_ext=False, ring_ext=False, pinky_ext=False, thumb_tucked=False)
    res = classifier.classify(hand)
    assert res.name == "Shikhara"
    assert res.confidence >= 0.70


def test_classifier_suchi(classifier):
    # Index pointing straight up, other 3 fingers curled into fist
    hand = _build_hand(thumb_erect=False, index_ext=True, middle_ext=False, ring_ext=False, pinky_ext=False, thumb_tucked=True)
    res = classifier.classify(hand)
    assert res.name == "Suchi"
    assert res.confidence >= 0.70


def test_classifier_tripataka(classifier):
    # Index, Middle, Pinky extended; Ring curled
    hand = _build_hand(thumb_erect=False, index_ext=True, middle_ext=True, ring_ext=False, pinky_ext=True, thumb_tucked=True)
    res = classifier.classify(hand)
    assert res.name == "Tripataka"
    assert res.confidence >= 0.70


def test_temporal_smoothing_buffer(classifier):
    # Feed multiple frames and verify smoothing
    hand = _build_hand(thumb_erect=False, index_ext=True, middle_ext=False, ring_ext=False, pinky_ext=False, thumb_tucked=True)
    for _ in range(5):
        res = classifier.classify(hand)
    assert res.name == "Suchi"
