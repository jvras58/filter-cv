"""Proximidade indicador–olho para ligar/desligar filtro AR."""

from __future__ import annotations

import numpy as np

from core.gestures.hand_pose import INDEX_TIP
from core.gestures.types import FaceLandmarks, HandLandmarks

FACE_LEFT_EYE = 33
FACE_RIGHT_EYE = 263


def index_near_eyes(
    hand: HandLandmarks,
    face: FaceLandmarks,
    frame_width: int,
    frame_height: int,
    radius_factor: float,
) -> bool:
    """True se a ponta do indicador está perto de um dos olhos (escala = distância interocular)."""
    idx = np.array([hand[INDEX_TIP][0] * frame_width, hand[INDEX_TIP][1] * frame_height])
    left = np.array(
        [face[FACE_LEFT_EYE][0] * frame_width, face[FACE_LEFT_EYE][1] * frame_height]
    )
    right = np.array(
        [face[FACE_RIGHT_EYE][0] * frame_width, face[FACE_RIGHT_EYE][1] * frame_height]
    )
    eye_dist = float(np.linalg.norm(right - left))
    if eye_dist < 20:
        return False
    max_dist = eye_dist * radius_factor
    return (
        float(np.linalg.norm(idx - left)) < max_dist
        or float(np.linalg.norm(idx - right)) < max_dist
    )
