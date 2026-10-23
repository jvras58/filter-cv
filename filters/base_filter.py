"""Contrato ABC para estágios do pipeline de vídeo."""

from abc import ABC, abstractmethod

import numpy as np


class VideoFilter(ABC):
    """Um estágio: entrada opcional de teclado + transformação por frame."""

    @abstractmethod
    def handle_input(self, key: int) -> None:
        """Reage a teclas não consumidas pelo orquestrador."""

    @abstractmethod
    def apply(
        self,
        frame: np.ndarray,
        face_landmarks: list[tuple[float, float, float]] | None = None,
    ) -> np.ndarray:
        """Retorna frame BGR ``uint8``."""

    def close(self) -> None:
        """Libera recursos nativos (sobrescrever se necessário)."""
