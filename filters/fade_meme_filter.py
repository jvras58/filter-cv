"""Meme fade: frozen background + linear person opacity."""

import numpy as np

from filters.base_filter import VideoFilter
from core.keys import KEY_FADE_IN, KEY_FADE_IN_UPPER, KEY_FADE_OUT, KEY_FADE_OUT_UPPER

_ALPHA_STEP = 0.05


class FadeMemeFilter(VideoFilter):
    def __init__(self, background_frame: np.ndarray) -> None:
        self._background = background_frame.copy()
        self.alpha = 1.0
        self.is_fading_out = False

    def handle_input(self, key: int) -> None:
        if key in (KEY_FADE_OUT, KEY_FADE_OUT_UPPER):
            self.is_fading_out = True
        elif key in (KEY_FADE_IN, KEY_FADE_IN_UPPER):
            self.is_fading_out = False

    def apply(self, frame: np.ndarray) -> np.ndarray:
        if self.is_fading_out and self.alpha > 0.0:
            self.alpha = max(0.0, self.alpha - _ALPHA_STEP)
        elif not self.is_fading_out and self.alpha < 1.0:
            self.alpha = min(1.0, self.alpha + _ALPHA_STEP)

        beta = 1.0 - self.alpha
        blended = (frame.astype(np.float32) * self.alpha) + (
            self._background.astype(np.float32) * beta
        )
        return np.clip(blended, 0, 255).astype(np.uint8)
