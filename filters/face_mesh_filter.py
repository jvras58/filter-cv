"""AR overlay aligned to MediaPipe Face Landmarker landmarks."""

from __future__ import annotations

import math

import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python.core import base_options as base_options_module
from mediapipe.tasks.python.vision import face_landmarker as face_landmarker_module
from mediapipe.tasks.python.vision.core import vision_task_running_mode as running_mode_module

from filters.base_filter import VideoFilter
from utils.mediapipe_models import ensure_face_landmarker_model
from utils.overlay import blend_bgra_on_bgr, load_bgra_asset, transform_overlay

_LANDMARK_LEFT_EYE = 33
_LANDMARK_RIGHT_EYE = 263
_LANDMARK_NOSE_BRIDGE = 1
_OVERLAY_WIDTH_FACTOR = 2.8


class FaceMeshFilter(VideoFilter):
    def __init__(self, overlay_path: str, fps: int = 30) -> None:
        self._overlay_asset = load_bgra_asset(overlay_path)
        model_path = ensure_face_landmarker_model()
        options = face_landmarker_module.FaceLandmarkerOptions(
            base_options=base_options_module.BaseOptions(model_asset_path=str(model_path)),
            running_mode=running_mode_module.VisionTaskRunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = face_landmarker_module.FaceLandmarker.create_from_options(
            options
        )
        self._frame_index = 0
        self._fps_hint_ms = max(1, int(1000 / fps))

    def handle_input(self, key: int) -> None:
        return

    def apply(self, frame: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        timestamp_ms = self._frame_index * self._fps_hint_ms
        self._frame_index += 1

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.face_landmarks:
            return frame

        landmarks = result.face_landmarks[0]
        h, w = frame.shape[:2]

        left = landmarks[_LANDMARK_LEFT_EYE]
        right = landmarks[_LANDMARK_RIGHT_EYE]
        nose = landmarks[_LANDMARK_NOSE_BRIDGE]

        left_pt = np.array([left.x * w, left.y * h], dtype=np.float32)
        right_pt = np.array([right.x * w, right.y * h], dtype=np.float32)
        nose_pt = (int(nose.x * w), int(nose.y * h))

        delta = right_pt - left_pt
        eye_distance = float(np.linalg.norm(delta))
        if eye_distance < 1.0:
            return frame

        angle_deg = math.degrees(math.atan2(delta[1], delta[0]))
        target_width = eye_distance * _OVERLAY_WIDTH_FACTOR
        overlay = transform_overlay(self._overlay_asset, target_width, angle_deg)
        return blend_bgra_on_bgr(frame, overlay, nose_pt[0], nose_pt[1])

    def close(self) -> None:
        self._landmarker.close()
