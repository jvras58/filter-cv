"""Central configuration defaults (expandable to YAML later)."""

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ASSETS_DIR = PROJECT_ROOT / "assets"
DEFAULT_OVERLAY_PATH = DEFAULT_ASSETS_DIR / "oculos_thug_life.png"


@dataclass(frozen=True)
class StreamConfig:
    device_id: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30
    preview_window: bool = True
    background_capture_seconds: float = 2.0
    overlay_asset_path: Path = DEFAULT_OVERLAY_PATH
    show_landmarks: bool = False
    gesture_stable_frames: int = 7
    min_hand_span_ratio: float = 0.12
    eye_touch_radius_factor: float = 0.55


DEFAULT_STREAM_CONFIG = StreamConfig()
