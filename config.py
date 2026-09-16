"""
config.py — Central configuration loader
Reads config/settings.yaml and exposes a typed AppConfig object.
Import this module anywhere in the project to access settings.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field

_CONFIG_PATH = Path(__file__).parent / "config" / "settings.yaml"


# ── Nested config dataclasses ─────────────────────────────────────────────────

@dataclass
class CameraConfig:
    device_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    fps: int = 30


@dataclass
class MediaPipeConfig:
    max_num_hands: int = 1
    min_detection_confidence: float = 0.75
    min_tracking_confidence: float = 0.75
    model_complexity: int = 1


@dataclass
class RecognitionConfig:
    engine: str = "rule_based"
    confidence_threshold: float = 0.80
    smoothing_frames: int = 5


@dataclass
class DatabaseConfig:
    path: str = "db/hasta_mudra.db"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/app.log"


@dataclass
class AppConfig:
    name: str = "HastaAI"
    version: str = "1.0.0"
    debug: bool = False
    camera: CameraConfig = field(default_factory=CameraConfig)
    mediapipe: MediaPipeConfig = field(default_factory=MediaPipeConfig)
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


# ── Loader ────────────────────────────────────────────────────────────────────

def load_config(path: Path = _CONFIG_PATH) -> AppConfig:
    """Load and parse settings.yaml into an AppConfig object."""
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    app_raw = raw.get("app", {})
    return AppConfig(
        name=app_raw.get("name", "HastaAI"),
        version=app_raw.get("version", "1.0.0"),
        debug=app_raw.get("debug", False),
        camera=CameraConfig(**raw.get("camera", {})),
        mediapipe=MediaPipeConfig(**raw.get("mediapipe", {})),
        recognition=RecognitionConfig(**raw.get("recognition", {})),
        database=DatabaseConfig(**raw.get("database", {})),
        logging=LoggingConfig(**raw.get("logging", {})),
    )


# Singleton — import this across the project
cfg: AppConfig = load_config()
