"""Abstract video filter contract."""

from abc import ABC, abstractmethod

import numpy as np


class VideoFilter(ABC):
    """Pipeline stage: optional input handling + per-frame transform."""

    @abstractmethod
    def handle_input(self, key: int) -> None:
        """React to a key press not consumed by the orchestrator."""

    @abstractmethod
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Return a BGR uint8 frame."""

    def close(self) -> None:
        """Release resources (override when the filter owns native handles)."""
