"""Orquestra MediaPipe (mão + rosto) e converte poses em eventos estáveis."""

from __future__ import annotations

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
from core.gestures.eye_touch import index_near_eyes
from core.gestures.hand_pose import (
    hand_large_enough,
    is_eye_touch_pose,
    is_fist,
    is_peace_sign,
)
from core.gestures.types import GestureSnapshot, HandLandmarks
from utils.mediapipe_models import ensure_face_landmarker_model, ensure_hand_landmarker_model


class GestureHub:
    """Uma inferência por frame; mantém estado de AR e debounce dos gestos."""

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
        """Se o overlay de óculos deve ser aplicado neste frame."""
        return self._ar_enabled

    def close(self) -> None:
        """Libera modelos MediaPipe."""
        self._hands.close()
        self._face.close()

    @staticmethod
    def _normalize_hand(hand) -> HandLandmarks:
        return [(lm.x, lm.y, lm.z) for lm in hand]

    def _detect_landmarks(
        self, frame_bgr: np.ndarray, timestamp_ms: int
    ) -> tuple[list[HandLandmarks], list[tuple[float, float, float]] | None]:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        hand_result = self._hands.detect_for_video(mp_image, timestamp_ms)
        face_result = self._face.detect_for_video(mp_image, timestamp_ms)

        hands: list[HandLandmarks] = []
        if hand_result.hand_landmarks:
            for hand in hand_result.hand_landmarks:
                hands.append(self._normalize_hand(hand))

        face = None
        if face_result.face_landmarks:
            face = [(lm.x, lm.y, lm.z) for lm in face_result.face_landmarks[0]]

        return hands, face

    def _poses_this_frame(
        self,
        hands: list[HandLandmarks],
        face: list[tuple[float, float, float]] | None,
        width: int,
        height: int,
    ) -> tuple[bool, bool, bool]:
        peace_now = False
        fist_now = False
        eye_touch_now = False
        min_span = self._config.min_hand_span_ratio

        for hand in hands:
            if not hand_large_enough(hand, width, min_span):
                continue
            if is_peace_sign(hand):
                peace_now = True
            if is_fist(hand):
                fist_now = True
            if face and is_eye_touch_pose(hand):
                if index_near_eyes(
                    hand,
                    face,
                    width,
                    height,
                    self._config.eye_touch_radius_factor,
                ):
                    eye_touch_now = True

        return peace_now, fist_now, eye_touch_now

    def _apply_stability(
        self, snap: GestureSnapshot, peace_now: bool, fist_now: bool, eye_touch_now: bool
    ) -> None:
        stable = self._config.gesture_stable_frames

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

    def update(self, frame_bgr: np.ndarray) -> GestureSnapshot:
        """Processa o frame BGR e retorna landmarks + eventos (borda) deste tick."""
        h, w = frame_bgr.shape[:2]
        ts = self._frame_index * self._fps_hint_ms
        self._frame_index += 1

        hands, face = self._detect_landmarks(frame_bgr, ts)
        snap = GestureSnapshot(hand_landmarks=hands, face_landmarks=face)

        peace_now, fist_now, eye_touch_now = self._poses_this_frame(hands, face, w, h)
        self._apply_stability(snap, peace_now, fist_now, eye_touch_now)
        return snap
