"""Download and cache MediaPipe task models."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from config.settings import DEFAULT_ASSETS_DIR

FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
FACE_LANDMARKER_PATH = DEFAULT_ASSETS_DIR / "models" / "face_landmarker.task"
HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
HAND_LANDMARKER_PATH = DEFAULT_ASSETS_DIR / "models" / "hand_landmarker.task"


def _ensure_model(url: str, path: Path, label: str) -> Path:
    """Baixa o arquivo ``.task`` se ainda não existir em disco."""
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[VSE] Baixando modelo {label} em {path} ...")
    urllib.request.urlretrieve(url, path)
    return path


def ensure_face_landmarker_model(path: Path = FACE_LANDMARKER_PATH) -> Path:
    """Caminho local do modelo Face Landmarker (download sob demanda)."""
    return _ensure_model(FACE_LANDMARKER_URL, path, "Face Landmarker")


def ensure_hand_landmarker_model(path: Path = HAND_LANDMARKER_PATH) -> Path:
    """Caminho local do modelo Hand Landmarker (download sob demanda)."""
    return _ensure_model(HAND_LANDMARKER_URL, path, "Hand Landmarker")
