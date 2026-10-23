"""Teclas globais do VSE (debug, fallback de fade, sair)."""

from core.keys import (
    KEY_DEBUG_LANDMARKS,
    KEY_DEBUG_LANDMARKS_UPPER,
    KEY_FADE_IN,
    KEY_FADE_IN_UPPER,
    KEY_QUIT,
    KEY_QUIT_UPPER,
)
from filters.actions.disappear_fade import DisappearFadeAction


class KeyboardHandler:
    """Estado de debug e callbacks de teclado fora do game loop."""

    def __init__(
        self,
        disappear: DisappearFadeAction,
        show_landmarks_initial: bool = False,
    ) -> None:
        self.show_landmarks = show_landmarks_initial
        self._disappear = disappear

    def handle(self, key: int) -> bool:
        """Processa uma tecla. Retorna ``False`` para encerrar a aplicação."""
        if key in (KEY_QUIT, KEY_QUIT_UPPER):
            return False
        if key in (KEY_DEBUG_LANDMARKS, KEY_DEBUG_LANDMARKS_UPPER):
            self.show_landmarks = not self.show_landmarks
            state = "ON" if self.show_landmarks else "OFF"
            print(f"[VSE] Debug landmarks: {state}")
        if key in (KEY_FADE_IN, KEY_FADE_IN_UPPER):
            self._disappear.start_fade_in()
        return True
