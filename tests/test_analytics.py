"""
tests/test_analytics.py — Tests for user analytics calculations and empty states
"""

import pytest
from db.database import (
    init_db,
    create_user,
    start_practice_session,
    end_practice_session,
    log_recognition_result,
)
from analytics.session_analytics import (
    get_user_overview_metrics,
    get_confidence_trend_df,
    get_performance_trend_df,
    get_mudra_distribution_df,
    get_recent_sessions_df,
)
from utils.auth import hash_password


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_empty_user_analytics():
    # User with no sessions
    user_id = create_user("Empty User", "empty_user@example.com", hash_password("pass123"), "local") or 9999
    metrics = get_user_overview_metrics(user_id)
    assert metrics["has_data"] is False
    assert metrics["total_sessions"] == 0
    assert metrics["total_practice_seconds"] == 0.0
    assert metrics["average_confidence"] == 0.0
    assert metrics["best_performance_score"] == 0.0

    conf_df = get_confidence_trend_df(user_id)
    assert conf_df.empty

    dist_df = get_mudra_distribution_df(user_id)
    assert dist_df.empty

    recent_df = get_recent_sessions_df(user_id)
    assert recent_df.empty


def test_user_with_sessions_analytics():
    email = "active_dancer@example.com"
    user_id = create_user("Active Dancer", email, hash_password("pass123"), "local")
    if not user_id:
        from db.database import get_user_by_email
        existing = get_user_by_email(email)
        assert existing is not None
        user_id = existing["id"]

    # Session 1: Pataka (id=1)
    s1 = start_practice_session(user_id, mudra_id=1)
    assert s1 is not None
    log_recognition_result(s1, 1, 0.90)
    end_practice_session(s1, duration=20.0, average_confidence=0.90, performance_score=88.0, dominant_mudra_id=1)

    # Session 2: Tripataka (id=2)
    s2 = start_practice_session(user_id, mudra_id=2)
    assert s2 is not None
    log_recognition_result(s2, 2, 0.94)
    end_practice_session(s2, duration=35.0, average_confidence=0.94, performance_score=94.0, dominant_mudra_id=2)

    # Overview metrics
    metrics = get_user_overview_metrics(user_id)
    assert metrics["has_data"] is True
    assert metrics["total_sessions"] >= 2
    assert metrics["total_practice_seconds"] >= 55.0
    assert metrics["average_confidence"] > 0.91
    assert metrics["best_performance_score"] >= 94.0

    # Trend DataFrames
    conf_df = get_confidence_trend_df(user_id)
    assert not conf_df.empty
    assert "Confidence" in conf_df.columns

    perf_df = get_performance_trend_df(user_id)
    assert not perf_df.empty
    assert "Performance Score" in perf_df.columns

    dist_df = get_mudra_distribution_df(user_id)
    assert not dist_df.empty
    assert "Mudra" in dist_df.columns
    assert "Sessions" in dist_df.columns

    recent_df = get_recent_sessions_df(user_id, limit=5)
    assert len(recent_df) >= 2
