"""Abstract video filter contract."""

from abc import ABC, abstractmethod

import numpy as np


class VideoFilter(ABC):
    @abstractmethod
    def handle_input(self, key: int) -> None:
        """React to a key press not consumed by the orchestrator."""

    @abstractmethod
    def apply(
        self,
        frame: np.ndarray,
        face_landmarks: list[tuple[float, float, float]] | None = None,
    ) -> np.ndarray:
        """Return a BGR uint8 frame."""

    def close(self) -> None:
        """Release resources (override when the filter owns native handles)."""
