"""Webcam input via OpenCV VideoCapture."""

from __future__ import annotations

import time

import cv2
import numpy as np


class CameraStream:
    def __init__(
        self,
        device_id: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ) -> None:
        self._capture = cv2.VideoCapture(device_id)
        if not self._capture.isOpened():
            raise RuntimeError(f"Could not open camera device {device_id}")

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._capture.set(cv2.CAP_PROP_FPS, fps)
        self._width = width
        self._height = height

    def read_frame(self) -> np.ndarray | None:
        ok, frame = self._capture.read()
        return frame if ok else None

    def capture_static_background(
        self,
        seconds: float = 2.0,
        preview_window: str | None = "VSE — capture background",
    ) -> np.ndarray:
        """Guide the user to leave the frame, then grab a reference background."""
        print(
            f"\n[VSE] Saia do quadro da webcam. "
            f"Capturando fundo em {seconds:.0f}s...\n"
        )
        deadline = time.monotonic() + seconds
        last_frame: np.ndarray | None = None

        while time.monotonic() < deadline:
            frame = self.read_frame()
            if frame is not None:
                last_frame = frame
            if preview_window:
                if frame is not None:
                    cv2.imshow(preview_window, frame)
                cv2.waitKey(1)

        if preview_window:
            cv2.destroyWindow(preview_window)

        if last_frame is None:
            raise RuntimeError("Failed to capture background frame from camera")

        print("[VSE] Fundo capturado. Volte ao quadro e use 1/2/3 para filtros.\n")
        return last_frame

    def release(self) -> None:
        self._capture.release()
