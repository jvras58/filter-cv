"""Detecção unificada: gestos de filtro/ação + landmarks para debug e AR."""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

from config.settings import StreamConfig
from utils.mediapipe_models import ensure_face_landmarker_model, ensure_hand_landmarker_model

_WRIST = 0
_THUMB_TIP = 4
_THUMB_IP = 3
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

_FACE_LEFT_EYE = 33
_FACE_RIGHT_EYE = 263


@dataclass
class GestureSnapshot:
    hand_landmarks: list[list[tuple[float, float, float]]] = field(default_factory=list)
    face_landmarks: list[tuple[float, float, float]] | None = None
    peace_out: bool = False
    fade_in: bool = False
    toggle_ar: bool = False


class GestureHub:
    def __init__(self, config: StreamConfig) -> None:
        self._config = config
        hand_path = ensure_hand_landmarker_model()
        face_path = ensure_face_landmarker_model()
        self._hands = HandLandmarker.create_from_options(
            HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(hand_path)),
                running_mode=RunningMode.VIDEO,
                num_hands=2,
            )
        )
        self._face = FaceLandmarker.create_from_options(
            FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(face_path)),
                running_mode=RunningMode.VIDEO,
                num_faces=1,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
            )
        )
        self._frame_index = 0
        self._fps_hint_ms = max(1, int(1000 / config.fps))
        self._peace_stable = 0
        self._fist_stable = 0
        self._eye_touch_stable = 0
        self._peace_cooldown_until = 0
        self._eye_touch_cooldown_until = 0
        self._ar_enabled = False

    @property
    def ar_enabled(self) -> bool:
        return self._ar_enabled

    def close(self) -> None:
        self._hands.close()
        self._face.close()

    def _landmark_list(self, hand) -> list[tuple[float, float, float]]:
        return [(lm.x, lm.y, lm.z) for lm in hand]

    def _dist(self, a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return float(np.linalg.norm(np.array(a) - np.array(b)))

    def _finger_extended(
        self,
        landmarks: list[tuple[float, float, float]],
        tip: int,
        pip: int,
        ratio: float = 1.12,
    ) -> bool:
        wrist = landmarks[_WRIST]
        return self._dist(landmarks[tip], wrist) > self._dist(landmarks[pip], wrist) * ratio

    def _hand_span_px(
        self, landmarks: list[tuple[float, float, float]], width: int, height: int
    ) -> float:
        xs = [lm[0] * width for lm in landmarks]
        return max(xs) - min(xs)

    def _hand_large_enough(
        self, landmarks: list[tuple[float, float, float]], width: int, height: int
    ) -> bool:
        span = self._hand_span_px(landmarks, width, height)
        return span >= width * self._config.min_hand_span_ratio

    def _is_peace_sign(self, landmarks: list[tuple[float, float, float]]) -> bool:
        index_up = self._finger_extended(landmarks, _INDEX_TIP, _INDEX_PIP)
        middle_up = self._finger_extended(landmarks, _MIDDLE_TIP, _MIDDLE_PIP)
        ring_down = not self._finger_extended(
            landmarks, _RING_TIP, _RING_PIP, ratio=1.05
        )
        pinky_down = not self._finger_extended(
            landmarks, _PINKY_TIP, _PINKY_PIP, ratio=1.05
        )
        if not (index_up and middle_up and ring_down and pinky_down):
            return False
        spread = self._dist(landmarks[_INDEX_TIP], landmarks[_MIDDLE_TIP])
        palm = self._dist(landmarks[_INDEX_MCP], landmarks[_MIDDLE_MCP])
        return spread > palm * 0.4

    def _is_fist(self, landmarks: list[tuple[float, float, float]]) -> bool:
        fingers = (
            (_INDEX_TIP, _INDEX_PIP),
            (_MIDDLE_TIP, _MIDDLE_PIP),
            (_RING_TIP, _RING_PIP),
            (_PINKY_TIP, _PINKY_PIP),
        )
        curled = all(
            not self._finger_extended(landmarks, tip, pip, ratio=1.08) for tip, pip in fingers
        )
        thumb_in = self._dist(landmarks[_THUMB_TIP], landmarks[_WRIST]) < self._dist(
            landmarks[_THUMB_IP], landmarks[_WRIST]
        ) * 1.15
        return curled and thumb_in

    def _is_eye_touch_pose(self, hand: list[tuple[float, float, float]]) -> bool:
        """Indicador estendido, demais dedos fechados (toque intencional no rosto)."""
        if not self._finger_extended(hand, _INDEX_TIP, _INDEX_PIP):
            return False
        others_down = not self._finger_extended(
            hand, _MIDDLE_TIP, _MIDDLE_PIP, ratio=1.05
        ) and not self._finger_extended(hand, _RING_TIP, _RING_PIP, ratio=1.05)
        return others_down and not self._finger_extended(
            hand, _PINKY_TIP, _PINKY_PIP, ratio=1.05
        )

    def _index_near_eyes(
        self,
        hand: list[tuple[float, float, float]],
        face: list[tuple[float, float, float]],
        width: int,
        height: int,
    ) -> bool:
        idx = np.array([hand[_INDEX_TIP][0] * width, hand[_INDEX_TIP][1] * height])
        left = np.array([face[_FACE_LEFT_EYE][0] * width, face[_FACE_LEFT_EYE][1] * height])
        right = np.array(
            [face[_FACE_RIGHT_EYE][0] * width, face[_FACE_RIGHT_EYE][1] * height]
        )
        eye_dist = float(np.linalg.norm(right - left))
        if eye_dist < 20:
            return False
        max_dist = eye_dist * self._config.eye_touch_radius_factor
        return (
            float(np.linalg.norm(idx - left)) < max_dist
            or float(np.linalg.norm(idx - right)) < max_dist
        )

    def update(self, frame_bgr: np.ndarray) -> GestureSnapshot:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        ts = self._frame_index * self._fps_hint_ms
        self._frame_index += 1

        hand_result = self._hands.detect_for_video(mp_image, ts)
        face_result = self._face.detect_for_video(mp_image, ts)

        hands_norm: list[list[tuple[float, float, float]]] = []
        if hand_result.hand_landmarks:
            for hand in hand_result.hand_landmarks:
                hands_norm.append(self._landmark_list(hand))

        face_norm: list[tuple[float, float, float]] | None = None
        if face_result.face_landmarks:
            face_norm = [(lm.x, lm.y, lm.z) for lm in face_result.face_landmarks[0]]

        snap = GestureSnapshot(hand_landmarks=hands_norm, face_landmarks=face_norm)
        stable = self._config.gesture_stable_frames

        peace_now = False
        fist_now = False
        eye_touch_now = False

        for hand in hands_norm:
            if not self._hand_large_enough(hand, w, h):
                continue
            if self._is_peace_sign(hand):
                peace_now = True
            if self._is_fist(hand):
                fist_now = True
            if face_norm and self._is_eye_touch_pose(hand):
                if self._index_near_eyes(hand, face_norm, w, h):
                    eye_touch_now = True

        self._peace_stable = self._peace_stable + 1 if peace_now else 0
        self._fist_stable = self._fist_stable + 1 if fist_now else 0
        self._eye_touch_stable = self._eye_touch_stable + 1 if eye_touch_now else 0

        if (
            self._peace_stable >= stable
            and self._frame_index > self._peace_cooldown_until
        ):
            snap.peace_out = True
            self._peace_stable = 0
            self._peace_cooldown_until = self._frame_index + int(
                1.2 * 1000 / self._fps_hint_ms
            )

        if self._fist_stable >= stable:
            snap.fade_in = True
            self._fist_stable = 0

        if (
            self._eye_touch_stable >= stable
            and self._frame_index > self._eye_touch_cooldown_until
        ):
            snap.toggle_ar = True
            self._ar_enabled = not self._ar_enabled
            self._eye_touch_stable = 0
            self._eye_touch_cooldown_until = self._frame_index + int(
                1.5 * 1000 / self._fps_hint_ms
            )

        return snap
