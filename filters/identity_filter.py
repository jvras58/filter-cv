"""Pass-through filter (normal / camera with no effect)."""

import numpy as np

from filters.base_filter import VideoFilter


class IdentityFilter(VideoFilter):
    def handle_input(self, key: int) -> None:
        return

    def apply(
        self,
        frame: np.ndarray,
        face_landmarks: list[tuple[float, float, float]] | None = None,
    ) -> np.ndarray:
        return frame
