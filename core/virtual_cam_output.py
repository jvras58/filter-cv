"""Virtual camera output via pyvirtualcam."""

from __future__ import annotations

import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat


class VirtualCamOutput:
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30) -> None:
        self._camera = pyvirtualcam.Camera(
            width=width,
            height=height,
            fps=fps,
            fmt=PixelFormat.BGR,
        )
        print(f"[VSE] Virtual camera: {self._camera.device}")

    def send(self, frame_bgr: np.ndarray) -> None:
        if frame_bgr.dtype != np.uint8:
            frame_bgr = np.clip(frame_bgr, 0, 255).astype(np.uint8)
        self._camera.send(frame_bgr)
        self._camera.sleep_until_next_frame()

    def close(self) -> None:
        self._camera.close()
