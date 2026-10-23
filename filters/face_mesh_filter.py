"""Filtro AR: delega renderização a ``filters.ar.glasses_renderer``."""

from __future__ import annotations

import numpy as np

from filters.ar.glasses_renderer import render_glasses
from filters.ar.landmarks import FaceLandmarkList
from filters.base_filter import VideoFilter
from utils.bgra.assets import load_bgra_asset


class FaceMeshFilter(VideoFilter):
    """Adapter ``VideoFilter`` para o overlay de óculos."""

    def __init__(self, overlay_path: str) -> None:
        self._overlay_asset = load_bgra_asset(overlay_path)

    def handle_input(self, key: int) -> None:
        return

    def apply(
        self,
        frame: np.ndarray,
        face_landmarks: FaceLandmarkList | None = None,
    ) -> np.ndarray:
        if not face_landmarks:
            return frame
        return render_glasses(frame, face_landmarks, self._overlay_asset)
