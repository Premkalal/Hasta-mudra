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
    assert "at least 6" in msg

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
