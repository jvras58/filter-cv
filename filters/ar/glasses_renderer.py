"""Renderização do overlay de óculos a partir de landmarks."""

from __future__ import annotations

import math

import numpy as np

from filters.ar.landmarks import (
    LANDMARK_LEFT_EYE,
    LANDMARK_NOSE_BRIDGE,
    LANDMARK_RIGHT_EYE,
    FaceLandmarkList,
    landmark_xy,
)
from utils.bgra.assets import transform_overlay
from utils.bgra.blend import blend_bgra_on_bgr

OVERLAY_WIDTH_FACTOR = 2.8


def render_glasses(
    frame_bgr: np.ndarray,
    face_landmarks: FaceLandmarkList,
    overlay_asset_bgra: np.ndarray,
) -> np.ndarray:
    """Alinha e compõe o asset BGRA no frame usando olhos e ponte nasal."""
    h, w = frame_bgr.shape[:2]
    left_pt = np.array(
        landmark_xy(face_landmarks, LANDMARK_LEFT_EYE, w, h), dtype=np.float32
    )
    right_pt = np.array(
        landmark_xy(face_landmarks, LANDMARK_RIGHT_EYE, w, h), dtype=np.float32
    )
    nose_x, nose_y = landmark_xy(face_landmarks, LANDMARK_NOSE_BRIDGE, w, h)
    nose_pt = (int(nose_x), int(nose_y))

    delta = right_pt - left_pt
    eye_distance = float(np.linalg.norm(delta))
    if eye_distance < 1.0:
        return frame_bgr

    angle_deg = math.degrees(math.atan2(delta[1], delta[0]))
    target_width = eye_distance * OVERLAY_WIDTH_FACTOR
    overlay = transform_overlay(overlay_asset_bgra, target_width, angle_deg)
    return blend_bgra_on_bgr(frame_bgr, overlay, nose_pt[0], nose_pt[1])
