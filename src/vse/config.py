"""Central configuration defaults (expandable to YAML later)."""

from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
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


DEFAULT_STREAM_CONFIG = StreamConfig()
