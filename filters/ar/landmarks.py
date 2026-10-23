"""Índices e helpers de landmarks faciais (MediaPipe)."""

from __future__ import annotations

LANDMARK_LEFT_EYE = 33
LANDMARK_RIGHT_EYE = 263
LANDMARK_NOSE_BRIDGE = 1

FaceLandmarkList = list[tuple[float, float, float]]


def landmark_xy(face: FaceLandmarkList, index: int, width: int, height: int) -> tuple[float, float]:
    """Converte landmark normalizado em coordenadas de pixel."""
    x, y, _ = face[index]
    return x * width, y * height
