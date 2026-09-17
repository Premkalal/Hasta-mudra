"""
tests/test_database.py — Tests for database operations and authentication
"""

import uuid
import pytest
from db.database import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_name,
    get_all_mudras_db,
    start_practice_session,
    end_practice_session,
    log_recognition_result,
    get_user_sessions,
    get_session_details,
    get_session_results,
)
from utils.auth import hash_password, verify_password, validate_registration


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_password_hashing():
    pw = "SecretPassword123"
    hashed = hash_password(pw)
    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_registration_validation():
    valid, msg = validate_registration("A", "invalid-email", "123", "123")
    assert valid is False
    assert "Full Name" in msg

    valid, msg = validate_registration("Ananya", "invalid-email", "123", "123")
    assert valid is False
    assert "valid email" in msg

    valid, msg = validate_registration("Ananya", "ananya@example.com", "123", "123")
    assert valid is False
    assert "at least 8" in msg

    valid, msg = validate_registration("Ananya", "ananya@example.com", "secret123", "different")
    assert valid is False
    assert "do not match" in msg

    valid, msg = validate_registration("Ananya", "ananya@example.com", "secret123", "secret123")
    assert valid is True
    assert msg == ""


def test_create_and_fetch_user():
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_dancer_{unique_id}@example.com"
    pw_hash = hash_password("DanceSecret123")
    user_id = create_user("Test Dancer", email, pw_hash, "local")
    assert user_id is not None

    user = get_user_by_email(email)
    assert user is not None
    assert user["name"] == "Test Dancer"
    assert user["email"] == email

    # Duplicate should fail
    dup_id = create_user("Test Dancer", email, pw_hash, "local")
    assert dup_id is None

    # Update name
    ok = update_user_name(user_id, "Updated Dancer")
    assert ok is True
    updated = get_user_by_id(user_id)
    assert updated is not None
    assert updated["name"] == "Updated Dancer"


def test_mudras_seeded():
    mudras = get_all_mudras_db()
    assert len(mudras) >= 28
    names = [m["name"] for m in mudras]
    assert "Pataka" in names
    assert "Tripataka" in names
    assert "Alapadma" in names


def test_practice_session_lifecycle():
    unique_id = uuid.uuid4().hex[:8]
    email = f"session_test_user_{unique_id}@example.com"
    user_id = create_user("Session User", email, hash_password("Pass123"), "local")

    assert user_id is not None
    # Start session
    sess_id = start_practice_session(user_id=user_id)
    assert sess_id is not None

    # Log recognition results
    log_recognition_result(sess_id, 1, 0.95)
    log_recognition_result(sess_id, 1, 0.92)

    # End session
    end_practice_session(
        session_id=sess_id,
        duration=15.5,
        average_confidence=0.935,
        performance_score=92.0,
        dominant_mudra_id=1,
    )

    # Verify session details
    details = get_session_details(sess_id)
    assert details is not None
    assert details["duration"] == 15.5
    assert details["average_confidence"] == 0.935
    assert details["performance_score"] == 92.0

    # Verify results
    results = get_session_results(sess_id)
    assert len(results) == 2
    assert results[0]["confidence"] == 0.95

    # Verify user sessions
    user_sessions = get_user_sessions(user_id)
    assert len(user_sessions) >= 1
    assert user_sessions[0]["id"] == sess_id


def test_password_update_functions():
    from db.database import update_user_password, update_user_password_by_id, get_user_by_id
    from utils.auth import hash_password, verify_password

    uid_token = uuid.uuid4().hex[:8]
    email = f"pw_test_{uid_token}@example.com"
    orig_pw = "OriginalPass123"
    user_id = create_user("PW User", email, hash_password(orig_pw), "local")
    assert user_id is not None

    # Test update by email
    new_pw1 = "UpdatedPass456"
    assert update_user_password(email, hash_password(new_pw1)) is True
    u1 = get_user_by_id(user_id)
    assert u1 is not None
    assert verify_password(new_pw1, u1["password_hash"]) is True
    assert verify_password(orig_pw, u1["password_hash"]) is False

    # Test update by ID
    new_pw2 = "FinalPass789"
    assert update_user_password_by_id(user_id, hash_password(new_pw2)) is True
    u2 = get_user_by_id(user_id)
    assert u2 is not None
    assert verify_password(new_pw2, u2["password_hash"]) is True


def test_guest_session_isolation():
    from utils.auth import create_guest_session
    from analytics.session_analytics import get_user_overview_metrics, get_recent_sessions_df

    guest1 = create_guest_session()
    guest2 = create_guest_session()

    assert guest1["id"] != guest2["id"]
    assert guest1["auth_provider"] == "guest"
    assert guest2["auth_provider"] == "guest"

    # Verify both start with clean analytics
    m1 = get_user_overview_metrics(guest1["id"])
    assert m1["total_sessions"] == 0
    assert m1["unique_mudras_practiced"] == 0
    assert m1["has_data"] is False

    m2 = get_user_overview_metrics(guest2["id"])
    assert m2["total_sessions"] == 0
    assert m2["unique_mudras_practiced"] == 0

    # Verify recent sessions are empty
    df1 = get_recent_sessions_df(guest1["id"])
    assert df1.empty

