"""utils/__init__.py"""
from .logger import setup_logger
from .image_utils import bgr_to_rgb, overlay_text, resize_frame, load_image, save_snapshot
from .helpers import timestamp_filename, confidence_bar, clamp
from .auth import (
    hash_password,
    verify_password,
    validate_registration,
    is_authenticated,
    get_current_user,
    login_user,
    logout_user,
    require_auth,
    get_google_oauth_url,
    is_google_oauth_configured,
)

__all__ = [
    "setup_logger",
    "bgr_to_rgb", "overlay_text", "resize_frame", "load_image", "save_snapshot",
    "timestamp_filename", "confidence_bar", "clamp",
    "hash_password", "verify_password", "validate_registration",
    "is_authenticated", "get_current_user", "login_user", "logout_user",
    "require_auth", "get_google_oauth_url", "is_google_oauth_configured",
]
