"""Desenha landmarks de mão/rosto no preview (debug)."""

from __future__ import annotations

import cv2
import numpy as np

_HAND_CONNECTIONS = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (5, 9),
    (9, 13),
    (13, 17),
)


def _to_px(
    landmarks: list[tuple[float, float, float]], width: int, height: int
) -> list[tuple[int, int]]:
    return [(int(x * width), int(y * height)) for x, y, _ in landmarks]


def draw_hand_landmarks(
    frame_bgr: np.ndarray,
    hands: list[list[tuple[float, float, float]]],
) -> None:
    """Desenha conexões e pontos da mão no frame (mutação in-place)."""
    h, w = frame_bgr.shape[:2]
    for hand in hands:
        pts = _to_px(hand, w, h)
        for a, b in _HAND_CONNECTIONS:
            cv2.line(frame_bgr, pts[a], pts[b], (0, 255, 255), 1, cv2.LINE_AA)
        for x, y in pts:
            cv2.circle(frame_bgr, (x, y), 3, (0, 128, 255), -1, cv2.LINE_AA)


def draw_face_landmarks(
    frame_bgr: np.ndarray,
    face: list[tuple[float, float, float]],
    indices: tuple[int, ...] = (1, 33, 133, 263, 362, 61, 291),
) -> None:
    """Destaca landmarks faciais usados por gestos e AR."""
    h, w = frame_bgr.shape[:2]
    for idx in indices:
        if idx >= len(face):
            continue
        x, y, _ = face[idx]
        px, py = int(x * w), int(y * h)
        cv2.circle(frame_bgr, (px, py), 4, (255, 80, 80), -1, cv2.LINE_AA)
