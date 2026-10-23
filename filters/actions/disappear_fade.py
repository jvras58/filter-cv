"""Ação meme: some no fundo congelado (estilo peace-out)."""

import numpy as np

_ALPHA_STEP = 0.05


class DisappearFadeAction:
    """Interpola opacidade da pessoa sobre um frame de fundo capturado no início."""

    def __init__(self, background_frame: np.ndarray) -> None:
        self._background = background_frame.copy()
        self._alpha = 1.0
        self._fading_out = False

    def start_fade_out(self) -> None:
        """Inicia redução gradual da opacidade (peace out)."""
        self._fading_out = True

    def start_fade_in(self) -> None:
        """Restaura opacidade total (punho ou tecla ``A``)."""
        self._fading_out = False

    @property
    def is_active(self) -> bool:
        """True enquanto o fade não terminou ou ainda está em movimento."""
        return self._alpha < 1.0 or self._fading_out

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Compõe o frame atual sobre o fundo conforme ``alpha``."""
        if not self.is_active and self._alpha >= 1.0:
            return frame

        if self._fading_out and self._alpha > 0.0:
            self._alpha = max(0.0, self._alpha - _ALPHA_STEP)
        elif not self._fading_out and self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + _ALPHA_STEP)

        beta = 1.0 - self._alpha
        blended = (frame.astype(np.float32) * self._alpha) + (
            self._background.astype(np.float32) * beta
        )
        return np.clip(blended, 0, 255).astype(np.uint8)
