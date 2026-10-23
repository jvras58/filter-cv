"""Heurísticas de pose da mão (landmarks MediaPipe, coordenadas normalizadas)."""

from __future__ import annotations

import numpy as np

from core.gestures.types import HandLandmarks, Landmark3D

# Índices oficiais da mão (MediaPipe).
WRIST = 0
THUMB_TIP = 4
THUMB_IP = 3
INDEX_TIP = 8
INDEX_PIP = 6
INDEX_MCP = 5
MIDDLE_TIP = 12
MIDDLE_PIP = 10
MIDDLE_MCP = 9
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18


def _dist(a: Landmark3D, b: Landmark3D) -> float:
    return float(np.linalg.norm(np.array(a) - np.array(b)))


def finger_extended(
    landmarks: HandLandmarks,
    tip: int,
    pip: int,
    ratio: float = 1.12,
) -> bool:
    """True se a ponta do dedo está mais afastada do punho que a articulação PIP."""
    wrist = landmarks[WRIST]
    return _dist(landmarks[tip], wrist) > _dist(landmarks[pip], wrist) * ratio


def hand_span_px(landmarks: HandLandmarks, frame_width: int) -> float:
    """Largura da mão em pixels (aproximação pelo span horizontal dos landmarks)."""
    xs = [lm[0] * frame_width for lm in landmarks]
    return max(xs) - min(xs)


def hand_large_enough(
    landmarks: HandLandmarks,
    frame_width: int,
    min_span_ratio: float,
) -> bool:
    """Ignora mãos pequenas/distantes para reduzir falsos positivos."""
    return hand_span_px(landmarks, frame_width) >= frame_width * min_span_ratio


def is_peace_sign(landmarks: HandLandmarks) -> bool:
    """✌️ — indicador e médio estendidos, anelar e mindinho fechados, dedos em V."""
    index_up = finger_extended(landmarks, INDEX_TIP, INDEX_PIP)
    middle_up = finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP)
    ring_down = not finger_extended(landmarks, RING_TIP, RING_PIP, ratio=1.05)
    pinky_down = not finger_extended(landmarks, PINKY_TIP, PINKY_PIP, ratio=1.05)
    if not (index_up and middle_up and ring_down and pinky_down):
        return False
    spread = _dist(landmarks[INDEX_TIP], landmarks[MIDDLE_TIP])
    palm = _dist(landmarks[INDEX_MCP], landmarks[MIDDLE_MCP])
    return spread > palm * 0.4


def is_fist(landmarks: HandLandmarks) -> bool:
    """Punho fechado — usado para voltar do fade."""
    fingers = (
        (INDEX_TIP, INDEX_PIP),
        (MIDDLE_TIP, MIDDLE_PIP),
        (RING_TIP, RING_PIP),
        (PINKY_TIP, PINKY_PIP),
    )
    curled = all(
        not finger_extended(landmarks, tip, pip, ratio=1.08) for tip, pip in fingers
    )
    thumb_in = _dist(landmarks[THUMB_TIP], landmarks[WRIST]) < _dist(
        landmarks[THUMB_IP], landmarks[WRIST]
    ) * 1.15
    return curled and thumb_in


def is_eye_touch_pose(hand: HandLandmarks) -> bool:
    """Indicador estendido e demais dedos recolhidos (gesto de tocar o rosto)."""
    if not finger_extended(hand, INDEX_TIP, INDEX_PIP):
        return False
    middle_down = not finger_extended(hand, MIDDLE_TIP, MIDDLE_PIP, ratio=1.05)
    ring_down = not finger_extended(hand, RING_TIP, RING_PIP, ratio=1.05)
    pinky_down = not finger_extended(hand, PINKY_TIP, PINKY_PIP, ratio=1.05)
    return middle_down and ring_down and pinky_down
