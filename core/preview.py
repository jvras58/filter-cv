"""Janela de preview local (não vai para a câmera virtual)."""

from __future__ import annotations

import cv2
import numpy as np

from core.gestures.types import GestureSnapshot
from core.keys import PREVIEW_WINDOW_NAME
from utils.mediapipe.debug_draw import draw_face_landmarks, draw_hand_landmarks


def show_preview(
    frame_out: np.ndarray,
    snap: GestureSnapshot,
    *,
    show_landmarks: bool,
    ar_enabled: bool,
    fade_active: bool,
) -> None:
    """Desenha HUD e landmarks opcionais e exibe com ``imshow``."""
    preview = frame_out.copy()
    if show_landmarks:
        draw_hand_landmarks(preview, snap.hand_landmarks)
        if snap.face_landmarks:
            draw_face_landmarks(preview, snap.face_landmarks)

    mode = "ar" if ar_enabled else "normal"
    cv2.putText(
        preview,
        f"modo: {mode}",
        (16, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    if fade_active:
        cv2.putText(
            preview,
            "acao: fade",
            (16, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 200, 255),
            2,
            cv2.LINE_AA,
        )
    cv2.imshow(PREVIEW_WINDOW_NAME, preview)
