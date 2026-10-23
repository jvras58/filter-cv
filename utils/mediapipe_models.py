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


def ensure_face_landmarker_model(path: Path = FACE_LANDMARKER_PATH) -> Path:
    if path.is_file():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[VSE] Baixando modelo Face Landmarker em {path} ...")
    urllib.request.urlretrieve(FACE_LANDMARKER_URL, path)
    return path
