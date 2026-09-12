"""
tests/test_landmarks.py — Unit tests for landmark extraction.
Run with: pytest tests/
"""

import numpy as np
import pytest
from core.landmarks import LandmarkExtractor, HandLandmarks


class _FakeLandmark:
    def __init__(self, x, y, z=0.0):
        self.x, self.y, self.z = x, y, z


class _FakeHandedness:
    class _Class:
        label = "Right"
    classification = [_Class()]


class _FakeResults:
    def __init__(self):
        # 21 fake landmarks — wrist at (0.5, 0.8), fingers spread upward
        self.multi_hand_landmarks = [
            type("H", (), {"landmark": [_FakeLandmark(0.5, 0.8)] + [_FakeLandmark(0.5, 0.3)] * 20})()
        ]
        self.multi_handedness = [_FakeHandedness()]


@pytest.fixture
def extractor():
    return LandmarkExtractor()


def test_extract_returns_handlandmarks(extractor):
    results = _FakeResults()
    hand = extractor.extract(results, (480, 640))
    assert isinstance(hand, HandLandmarks)


def test_feature_vector_shape(extractor):
    results = _FakeResults()
    hand = extractor.extract(results, (480, 640))
    assert hand.feature_vector.shape == (63,)


def test_feature_vector_normalised(extractor):
    results = _FakeResults()
    hand = extractor.extract(results, (480, 640))
    assert np.max(np.abs(hand.feature_vector)) <= 1.0 + 1e-6


def test_no_hand_returns_none(extractor):
    class EmptyResults:
        multi_hand_landmarks = None
        multi_handedness = None
    assert extractor.extract(EmptyResults(), (480, 640)) is None
