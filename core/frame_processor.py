"""Cadeia de processamento de um frame (filtros + ações)."""

from __future__ import annotations

import numpy as np

from core.gestures.types import GestureSnapshot
from filters.actions.disappear_fade import DisappearFadeAction
from filters.base_filter import VideoFilter
from filters.face_mesh_filter import FaceMeshFilter


class FrameProcessor:
    """Aplica pass-through, AR opcional e fade meme sobre o frame de entrada."""

    def __init__(
        self,
        identity: VideoFilter,
        ar_filter: FaceMeshFilter,
        disappear: DisappearFadeAction,
    ) -> None:
        self._identity = identity
        self._ar = ar_filter
        self._disappear = disappear

    def process(
        self,
        frame: np.ndarray,
        snap: GestureSnapshot,
        ar_enabled: bool,
    ) -> np.ndarray:
        """Retorna frame BGR pronto para a câmera virtual."""
        out = self._identity.apply(frame)
        if ar_enabled:
            out = self._ar.apply(out, snap.face_landmarks)
        return self._disappear.apply(out)
