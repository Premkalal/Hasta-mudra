"""db/__init__.py — Database package exports"""
from .database import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_name,
    get_all_mudras_db,
    get_mudra_by_name_db,
    get_mudra_by_id_db,
    start_practice_session,
    end_practice_session,
    log_recognition_result,
    get_user_sessions,
    get_session_details,
    get_session_results,
)

# Backward-compat aliases
start_session = start_practice_session
end_session = end_practice_session
log_detection = log_recognition_result

__all__ = [
    "init_db",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user_name",
    "get_all_mudras_db",
    "get_mudra_by_name_db",
    "get_mudra_by_id_db",
    "start_practice_session",
    "end_practice_session",
    "log_recognition_result",
    "get_user_sessions",
    "get_session_details",
    "get_session_results",
    "start_session",
    "end_session",
    "log_detection",
]
