"""
core/classifier.py — Geometric Feature Extraction & Mudra Recognition
HastaAI Computer Vision Classification Engine.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from collections import deque

from core.landmarks import HandLandmarks
from data.mudra_registry import get_all_mudras, get_mudra_by_name, MudraInfo
from config import cfg


@dataclass
class MudraResult:
    """Output of the classifier for a single frame."""
    name: str               # e.g. "Pataka"
    sanskrit: str           # e.g. "पताका"
    confidence: float       # 0.0 – 1.0
    description: str        # Short English description
    significance: str       # Cultural meaning
    instructions: str       # How to perform
    detected: bool          # True if confidence >= threshold
    status_label: str       # "Excellent Match", "Good Match", etc.


def _dist(p1, p2) -> float:
    """Euclidean distance between two 3D or 2D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)


class MudraClassifier:
    """
    Classifies HandLandmarks into classical Hasta Mudras.
    Combines rotation-invariant joint geometry, pinch distances, and temporal smoothing.
    """

    FINGER_TIPS = [4, 8, 12, 16, 20]
    FINGER_MCPS = [2, 5, 9, 13, 17]

    def __init__(self):
        self._mudras = get_all_mudras()
        self._threshold = cfg.recognition.confidence_threshold
        self._smoothing_window = cfg.recognition.smoothing_frames or 5
        self._name_buffer = deque(maxlen=self._smoothing_window)
        self._conf_buffer = deque(maxlen=self._smoothing_window)

    def classify(self, hand: HandLandmarks) -> MudraResult:
        """
        Classify landmarks with geometric analysis and temporal smoothing.
        """
        if not hand or not hand.raw_points or len(hand.raw_points) < 21:
            return MudraResult(
                name="Unknown",
                sanskrit="",
                confidence=0.0,
                description="No hand landmarks available.",
                significance="",
                instructions="",
                detected=False,
                status_label="No Hand Detected",
            )

        pts = hand.raw_points
        features = self._extract_geometric_features(pts)
        raw_result = self._evaluate_mudras(features)

        # Temporal smoothing
        self._name_buffer.append(raw_result.name)
        self._conf_buffer.append(raw_result.confidence)

        # Dominant mudra by frequency in buffer
        names = list(self._name_buffer)
        dominant_name = max(set(names), key=names.count)

        # Average confidence for dominant prediction
        dom_confs = [c for n, c in zip(names, self._conf_buffer) if n == dominant_name]
        smoothed_conf = float(np.mean(dom_confs)) if dom_confs else raw_result.confidence

        if dominant_name != raw_result.name:
            info = get_mudra_by_name(dominant_name)
            is_detected = smoothed_conf >= self._threshold and dominant_name != "Unknown"
            status = self._get_status_label(smoothed_conf, is_detected)
            return MudraResult(
                name=dominant_name,
                sanskrit=info.sanskrit if info else "",
                confidence=round(smoothed_conf, 3),
                description=info.description if info else "",
                significance=info.significance if info else "",
                instructions=info.instructions if info else "",
                detected=is_detected,
                status_label=status,
            )

        return raw_result

    def reset_buffer(self):
        """Clear temporal smoothing buffers."""
        self._name_buffer.clear()
        self._conf_buffer.clear()

    # ── Geometric Feature Extraction ──────────────────────────────────────────

    def _extract_geometric_features(self, pts: List[Tuple[float, float, float]]) -> Dict[str, Any]:
        """Extract rotation-invariant features normalized by palm scale."""
        wrist = pts[0]
        middle_mcp = pts[9]
        palm_scale = _dist(wrist, middle_mcp)
        if palm_scale < 1e-4:
            palm_scale = 1.0

        # Finger extension score: combines bone ratio and wrist-tip extension
        def compute_ext(mcp_idx, pip_idx, dip_idx, tip_idx):
            direct = _dist(pts[mcp_idx], pts[tip_idx])
            bones = (
                _dist(pts[mcp_idx], pts[pip_idx])
                + _dist(pts[pip_idx], pts[dip_idx])
                + _dist(pts[dip_idx], pts[tip_idx])
            )
            bone_ratio = direct / bones if bones > 1e-4 else 0.0

            d_wrist_tip = _dist(wrist, pts[tip_idx])
            d_wrist_mcp = _dist(wrist, pts[mcp_idx])
            wrist_ratio = (d_wrist_tip / d_wrist_mcp) if d_wrist_mcp > 1e-4 else 1.0

            # If folded back towards palm, wrist_ratio <= 1.05 and bone_ratio < 0.6
            if wrist_ratio < 1.15 or bone_ratio < 0.55:
                return min(bone_ratio, 0.45)
            return min(1.0, 0.6 * bone_ratio + 0.4 * min(1.0, wrist_ratio / 1.5))

        # Thumb extension: dist(Wrist, ThumbTip) / palm_scale
        thumb_ext = _dist(wrist, pts[4]) / palm_scale
        # Thumb distance to index base (tucked check)
        thumb_to_index_base = _dist(pts[4], pts[5]) / palm_scale

        index_ext = compute_ext(5, 6, 7, 8)
        middle_ext = compute_ext(9, 10, 11, 12)
        ring_ext = compute_ext(13, 14, 15, 16)
        pinky_ext = compute_ext(17, 18, 19, 20)

        # Normalized distances between fingertips
        d_thumb_index = _dist(pts[4], pts[8]) / palm_scale
        d_thumb_middle = _dist(pts[4], pts[12]) / palm_scale
        d_thumb_ring = _dist(pts[4], pts[16]) / palm_scale
        d_thumb_pinky = _dist(pts[4], pts[20]) / palm_scale

        d_index_middle = _dist(pts[8], pts[12]) / palm_scale
        d_middle_ring = _dist(pts[12], pts[16]) / palm_scale
        d_ring_pinky = _dist(pts[16], pts[20]) / palm_scale

        # Cluster distance: average distance from centroid of all 5 tips
        tips = [pts[4], pts[8], pts[12], pts[16], pts[20]]
        centroid = (
            sum(t[0] for t in tips) / 5.0,
            sum(t[1] for t in tips) / 5.0,
            sum(t[2] for t in tips) / 5.0,
        )
        tip_cluster_radius = sum(_dist(t, centroid) for t in tips) / (5.0 * palm_scale)

        # Inter-finger spread
        finger_spread = (d_index_middle + d_middle_ring + d_ring_pinky) / 3.0

        return {
            "palm_scale": palm_scale,
            "thumb_ext": thumb_ext,
            "thumb_to_index_base": thumb_to_index_base,
            "index_ext": index_ext,
            "middle_ext": middle_ext,
            "ring_ext": ring_ext,
            "pinky_ext": pinky_ext,
            "d_thumb_index": d_thumb_index,
            "d_thumb_middle": d_thumb_middle,
            "d_thumb_ring": d_thumb_ring,
            "d_thumb_pinky": d_thumb_pinky,
            "d_index_middle": d_index_middle,
            "d_middle_ring": d_middle_ring,
            "d_ring_pinky": d_ring_pinky,
            "tip_cluster_radius": tip_cluster_radius,
            "finger_spread": finger_spread,
        }

    # ── Mudra Matching Engine ──────────────────────────────────────────────────

    def _evaluate_mudras(self, f: Dict[str, Any]) -> MudraResult:
        """Evaluate geometric signatures and return best matching Mudra."""
        scores: Dict[str, float] = {}

        # 1. Mukula: All 5 tips clustered together
        if f["tip_cluster_radius"] < 0.38 and f["index_ext"] > 0.45:
            mukula_score = max(0.0, 1.0 - (f["tip_cluster_radius"] / 0.38) * 0.3)
            scores["Mukula"] = mukula_score

        # 2. Hamsasya: Thumb and Index tip pinched together, Middle/Ring/Pinky extended
        if f["d_thumb_index"] < 0.35 and f["middle_ext"] > 0.60 and f["ring_ext"] > 0.55:
            pinch_quality = max(0.0, 1.0 - (f["d_thumb_index"] / 0.35) * 0.3)
            ext_quality = (f["middle_ext"] + f["ring_ext"] + f["pinky_ext"]) / 3.0
            scores["Hamsasya"] = 0.6 * pinch_quality + 0.4 * ext_quality

        # 3. Mayura: Thumb and Ring tip touching, Index/Middle/Pinky extended
        if f["d_thumb_ring"] < 0.35 and f["index_ext"] > 0.60 and f["middle_ext"] > 0.60 and f["pinky_ext"] > 0.50:
            pinch_q = max(0.0, 1.0 - (f["d_thumb_ring"] / 0.35) * 0.3)
            scores["Mayura"] = 0.5 * pinch_q + 0.5 * min(1.0, (f["index_ext"] + f["middle_ext"]) / 2.0)

        # 4. Mushti: Full tight fist (all fingers curled, thumb tucked over fingers)
        if (
            f["index_ext"] < 0.50
            and f["middle_ext"] < 0.50
            and f["ring_ext"] < 0.50
            and f["pinky_ext"] < 0.50
            and f["thumb_ext"] < 0.95
        ):
            curl_avg = 1.0 - (f["index_ext"] + f["middle_ext"] + f["ring_ext"] + f["pinky_ext"]) / 4.0
            scores["Mushti"] = min(0.96, curl_avg)

        # 5. Shikhara: Fist with thumb held upright pointing away
        if (
            f["index_ext"] < 0.50
            and f["middle_ext"] < 0.50
            and f["ring_ext"] < 0.50
            and f["pinky_ext"] < 0.50
            and f["thumb_ext"] >= 0.95
        ):
            thumb_erect = min(1.0, (f["thumb_ext"] - 0.8) / 0.5)
            scores["Shikhara"] = 0.6 * thumb_erect + 0.4 * (1.0 - f["index_ext"])

        # 6. Suchi: Index pointing straight up, others curled
        if (
            f["index_ext"] > 0.68
            and f["middle_ext"] < 0.50
            and f["ring_ext"] < 0.50
            and f["pinky_ext"] < 0.50
        ):
            curl_rest = 1.0 - (f["middle_ext"] + f["ring_ext"] + f["pinky_ext"]) / 3.0
            scores["Suchi"] = 0.6 * f["index_ext"] + 0.4 * curl_rest

        # 7. Chandrakala: Thumb and Index extended wide apart like crescent, others curled
        if (
            f["index_ext"] > 0.65
            and f["thumb_ext"] > 1.0
            and f["d_thumb_index"] > 0.65
            and f["middle_ext"] < 0.50
            and f["ring_ext"] < 0.50
            and f["pinky_ext"] < 0.50
        ):
            scores["Chandrakala"] = 0.5 * f["index_ext"] + 0.5 * min(1.0, f["d_thumb_index"])

        # 8. Tripataka: Index, Middle, Pinky extended; Ring bent; Thumb folded
        if (
            f["index_ext"] > 0.65
            and f["middle_ext"] > 0.65
            and f["pinky_ext"] > 0.58
            and f["ring_ext"] < 0.55
        ):
            ring_bent = 1.0 - f["ring_ext"]
            scores["Tripataka"] = 0.5 * ((f["index_ext"] + f["middle_ext"] + f["pinky_ext"]) / 3.0) + 0.5 * ring_bent

        # 9. Ardhapataka: Index and Middle extended; Ring and Pinky folded
        if (
            f["index_ext"] > 0.65
            and f["middle_ext"] > 0.65
            and f["ring_ext"] < 0.50
            and f["pinky_ext"] < 0.50
        ):
            fold_rest = 1.0 - (f["ring_ext"] + f["pinky_ext"]) / 2.0
            scores["Ardhapataka"] = 0.5 * ((f["index_ext"] + f["middle_ext"]) / 2.0) + 0.5 * fold_rest

        # 10. Kartarimukha: Index and Pinky extended; Middle and Ring curled
        if (
            f["index_ext"] > 0.65
            and f["pinky_ext"] > 0.58
            and f["middle_ext"] < 0.50
            and f["ring_ext"] < 0.50
        ):
            scores["Kartarimukha"] = 0.5 * ((f["index_ext"] + f["pinky_ext"]) / 2.0) + 0.5 * (1.0 - f["middle_ext"])

        # 11. Simhamukha: Thumb, Index, Pinky extended; Middle and Ring curled near thumb
        if (
            f["index_ext"] > 0.62
            and f["pinky_ext"] > 0.58
            and f["middle_ext"] < 0.55
            and f["ring_ext"] < 0.55
            and f["thumb_ext"] > 0.95
        ):
            scores["Simhamukha"] = 0.4 * f["thumb_ext"] + 0.3 * f["index_ext"] + 0.3 * (1.0 - f["middle_ext"])

        # 12. Trishula: Index, Middle, Ring extended upright; Thumb holds Pinky down
        if (
            f["index_ext"] > 0.65
            and f["middle_ext"] > 0.65
            and f["ring_ext"] > 0.60
            and f["pinky_ext"] < 0.55
            and f["d_thumb_pinky"] < 0.45
        ):
            prongs = (f["index_ext"] + f["middle_ext"] + f["ring_ext"]) / 3.0
            scores["Trishula"] = 0.6 * prongs + 0.4 * (1.0 - f["d_thumb_pinky"])

        # 13. Alapadma: All 5 fingers spread out wide like an open lotus
        if (
            f["index_ext"] > 0.65
            and f["middle_ext"] > 0.65
            and f["ring_ext"] > 0.65
            and f["pinky_ext"] > 0.60
            and f["finger_spread"] > 0.32
        ):
            spread_score = min(1.0, f["finger_spread"] / 0.40)
            scores["Alapadma"] = 0.5 * spread_score + 0.5 * ((f["index_ext"] + f["middle_ext"] + f["ring_ext"]) / 3.0)

        # 14. Padmakosha: All fingers curved/cupped like a lotus bud
        if (
            0.50 < f["index_ext"] < 0.75
            and 0.50 < f["middle_ext"] < 0.75
            and 0.50 < f["ring_ext"] < 0.75
            and 0.40 < f["tip_cluster_radius"] < 0.65
        ):
            scores["Padmakosha"] = 0.82

        # 15. Ardhachandra: All 4 fingers joined together, Thumb stretched perpendicular
        if (
            f["index_ext"] > 0.68
            and f["middle_ext"] > 0.68
            and f["ring_ext"] > 0.68
            and f["pinky_ext"] > 0.62
            and f["thumb_ext"] > 1.05
            and f["d_thumb_index"] > 0.55
            and f["finger_spread"] < 0.28
        ):
            scores["Ardhachandra"] = 0.88

        # 16. Pataka: All 4 fingers extended together, Thumb tucked/folded against palm
        if (
            f["index_ext"] > 0.68
            and f["middle_ext"] > 0.68
            and f["ring_ext"] > 0.68
            and f["pinky_ext"] > 0.62
            and f["finger_spread"] < 0.30
            and (f["thumb_to_index_base"] < 0.48 or f["thumb_ext"] < 1.0)
        ):
            ext_avg = (f["index_ext"] + f["middle_ext"] + f["ring_ext"] + f["pinky_ext"]) / 4.0
            scores["Pataka"] = min(0.96, ext_avg)

        # Find best candidate
        if scores:
            best_name = max(scores, key=scores.get)
            best_conf = round(float(scores[best_name]), 3)
        else:
            best_name = "Unknown"
            best_conf = 0.0

        is_detected = best_conf >= self._threshold and best_name != "Unknown"
        status = self._get_status_label(best_conf, is_detected)
        info = get_mudra_by_name(best_name)

        return MudraResult(
            name=best_name,
            sanskrit=info.sanskrit if info else "",
            confidence=best_conf,
            description=info.description if info else "Adjust hand position within frame.",
            significance=info.significance if info else "",
            instructions=info.instructions if info else "",
            detected=is_detected,
            status_label=status,
        )

    @staticmethod
    def _get_status_label(confidence: float, detected: bool) -> str:
        if not detected or confidence < 0.5:
            return "Adjusting Pose"
        if confidence >= 0.88:
            return "Excellent Match"
        if confidence >= 0.75:
            return "Good Match"
        return "Fair Match"
