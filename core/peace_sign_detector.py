"""Detecta ✌️ (sumir) e mão aberta (voltar) via MediaPipe Hand Landmarker."""

from __future__ import annotations

import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

from utils.mediapipe_models import ensure_hand_landmarker_model

# Índices do landmark da mão (MediaPipe).
_WRIST = 0
_THUMB_TIP = 4
_INDEX_TIP = 8
_INDEX_PIP = 6
_INDEX_MCP = 5
_MIDDLE_TIP = 12
_MIDDLE_PIP = 10
_MIDDLE_MCP = 9
_RING_TIP = 16
_RING_PIP = 14
_PINKY_TIP = 20
_PINKY_PIP = 18

_STABLE_FRAMES = 4


class PeaceSignDetector:
    def __init__(self, fps: int = 30) -> None:
        model_path = ensure_hand_landmarker_model()
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        self._frame_index = 0
        self._fps_hint_ms = max(1, int(1000 / fps))
        self._peace_stable = 0
        self._palm_stable = 0
        self._cooldown_until_frame = 0

    def close(self) -> None:
        self._landmarker.close()

    def _landmark_list(self, hand) -> list[tuple[float, float, float]]:
        return [(lm.x, lm.y, lm.z) for lm in hand]

    def _dist(self, a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return float(np.linalg.norm(np.array(a) - np.array(b)))

    def _finger_extended(
        self,
        landmarks: list[tuple[float, float, float]],
        tip: int,
        pip: int,
    ) -> bool:
        wrist = landmarks[_WRIST]
        return self._dist(landmarks[tip], wrist) > self._dist(landmarks[pip], wrist) * 1.05

    def _is_peace_sign(self, landmarks: list[tuple[float, float, float]]) -> bool:
        index_up = self._finger_extended(landmarks, _INDEX_TIP, _INDEX_PIP)
        middle_up = self._finger_extended(landmarks, _MIDDLE_TIP, _MIDDLE_PIP)
        ring_down = not self._finger_extended(landmarks, _RING_TIP, _RING_PIP)
        pinky_down = not self._finger_extended(landmarks, _PINKY_TIP, _PINKY_PIP)

        if not (index_up and middle_up and ring_down and pinky_down):
            return False

        # ✌️ de lado: dedos separados o suficiente (V).
        spread = self._dist(landmarks[_INDEX_TIP], landmarks[_MIDDLE_TIP])
        palm = self._dist(landmarks[_INDEX_MCP], landmarks[_MIDDLE_MCP])
        return spread > palm * 0.35

    def _is_open_palm(self, landmarks: list[tuple[float, float, float]]) -> bool:
        fingers = (
            (_INDEX_TIP, _INDEX_PIP),
            (_MIDDLE_TIP, _MIDDLE_PIP),
            (_RING_TIP, _RING_PIP),
            (_PINKY_TIP, _PINKY_PIP),
        )
        extended = sum(
            1 for tip, pip in fingers if self._finger_extended(landmarks, tip, pip)
        )
        thumb_out = self._dist(landmarks[_THUMB_TIP], landmarks[_WRIST]) > self._dist(
            landmarks[3], landmarks[_WRIST]
        )
        return extended >= 4 and thumb_out

    def update(self, frame_bgr: np.ndarray) -> tuple[bool, bool]:
        """Retorna (disparar_sumir, disparar_voltar) neste frame."""
        trigger_out = False
        trigger_in = False

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        timestamp_ms = self._frame_index * self._fps_hint_ms
        self._frame_index += 1

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        peace_now = False
        palm_now = False

        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                lm = self._landmark_list(hand)
                if self._is_peace_sign(lm):
                    peace_now = True
                if self._is_open_palm(lm):
                    palm_now = True

        if peace_now:
            self._peace_stable += 1
        else:
            self._peace_stable = 0

        if palm_now:
            self._palm_stable += 1
        else:
            self._palm_stable = 0

        if (
            self._peace_stable >= _STABLE_FRAMES
            and self._frame_index > self._cooldown_until_frame
        ):
            trigger_out = True
            self._peace_stable = 0
            self._cooldown_until_frame = self._frame_index + int(0.8 * 1000 / self._fps_hint_ms)

        if self._palm_stable >= _STABLE_FRAMES:
            trigger_in = True
            self._palm_stable = 0

        return trigger_out, trigger_in
