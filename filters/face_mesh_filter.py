"""Overlay AR de óculos alinhado a landmarks de rosto (já detectados no hub)."""

from __future__ import annotations

import math

import numpy as np

from filters.base_filter import VideoFilter
from utils.overlay import blend_bgra_on_bgr, load_bgra_asset, transform_overlay

_LANDMARK_LEFT_EYE = 33
_LANDMARK_RIGHT_EYE = 263
_LANDMARK_NOSE_BRIDGE = 1
_OVERLAY_WIDTH_FACTOR = 2.8


def _landmark_xy(
    face: list[tuple[float, float, float]], index: int, w: int, h: int
) -> tuple[float, float]:
    x, y, _ = face[index]
    return x * w, y * h


class FaceMeshFilter(VideoFilter):
    """Desenha PNG BGRA escalado/rotacionado entre os olhos."""

    def __init__(self, overlay_path: str) -> None:
        self._overlay_asset = load_bgra_asset(overlay_path)

    def handle_input(self, key: int) -> None:
        return

    def apply(
        self,
        frame: np.ndarray,
        face_landmarks: list[tuple[float, float, float]] | None = None,
    ) -> np.ndarray:
        """Aplica óculos se ``face_landmarks`` estiver presente."""
        if not face_landmarks:
            return frame

        h, w = frame.shape[:2]
        left_pt = np.array(_landmark_xy(face_landmarks, _LANDMARK_LEFT_EYE, w, h), dtype=np.float32)
        right_pt = np.array(
            _landmark_xy(face_landmarks, _LANDMARK_RIGHT_EYE, w, h), dtype=np.float32
        )
        nose_x, nose_y = _landmark_xy(face_landmarks, _LANDMARK_NOSE_BRIDGE, w, h)
        nose_pt = (int(nose_x), int(nose_y))

        delta = right_pt - left_pt
        eye_distance = float(np.linalg.norm(delta))
        if eye_distance < 1.0:
            return frame

        angle_deg = math.degrees(math.atan2(delta[1], delta[0]))
        target_width = eye_distance * _OVERLAY_WIDTH_FACTOR
        overlay = transform_overlay(self._overlay_asset, target_width, angle_deg)
        return blend_bgra_on_bgr(frame, overlay, nose_pt[0], nose_pt[1])
