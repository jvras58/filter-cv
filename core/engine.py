"""Loop principal do VSE: captura → gestos → filtros → ações → saída virtual."""

from __future__ import annotations

import cv2

from config.settings import DEFAULT_STREAM_CONFIG, StreamConfig
from core.camera_stream import CameraStream
from core.gesture_hub import GestureHub
from core.keys import (
    KEY_DEBUG_LANDMARKS,
    KEY_DEBUG_LANDMARKS_UPPER,
    KEY_FADE_IN,
    KEY_FADE_IN_UPPER,
    KEY_QUIT,
    KEY_QUIT_UPPER,
    PREVIEW_WINDOW_NAME,
)
from core.virtual_cam_output import VirtualCamOutput
from filters.actions.disappear_fade import DisappearFadeAction
from filters.base_filter import VideoFilter
from filters.face_mesh_filter import FaceMeshFilter
from filters.registry import FilterFactoryContext, build_filters
from utils.landmark_debug import draw_face_landmarks, draw_hand_landmarks


class VirtualStreamEngine:
    """Compõe hardware, gestos, filtros de vídeo e ações pós-processamento."""

    def __init__(self, config: StreamConfig | None = None) -> None:
        self._config = config or DEFAULT_STREAM_CONFIG
        self._show_landmarks = self._config.show_landmarks
        self._input = CameraStream(
            self._config.device_id,
            self._config.width,
            self._config.height,
            self._config.fps,
        )
        background = self._input.capture_static_background(
            self._config.background_capture_seconds
        )
        ctx = FilterFactoryContext(config=self._config)
        self._filters: dict[str, VideoFilter] = build_filters(ctx)
        self._identity = self._filters["normal"]
        self._ar = self._filters["ar"]
        assert isinstance(self._ar, FaceMeshFilter)
        self._disappear = DisappearFadeAction(background)
        self._gestures = GestureHub(self._config)
        self._output = VirtualCamOutput(
            self._config.width,
            self._config.height,
            self._config.fps,
        )
        self._running = True
        self._shutdown_done = False

    def _handle_keys(self, key: int) -> bool:
        """Teclas globais. Retorna False para encerrar o loop."""
        if key in (KEY_QUIT, KEY_QUIT_UPPER):
            return False
        if key in (KEY_DEBUG_LANDMARKS, KEY_DEBUG_LANDMARKS_UPPER):
            self._show_landmarks = not self._show_landmarks
            state = "ON" if self._show_landmarks else "OFF"
            print(f"[VSE] Debug landmarks: {state}")
        if key in (KEY_FADE_IN, KEY_FADE_IN_UPPER):
            self._disappear.start_fade_in()
        return True

    def run(self) -> None:
        """Executa o game loop até ``Q`` ou falha de captura."""
        print(
            "[VSE] Gestos: ✌️=sumir | punho=voltar | toque no olho=óculos on/off | "
            "D=landmarks | A=voltar (teclado) | Q=sair\n"
        )

        try:
            while self._running:
                frame = self._input.read_frame()
                if frame is None:
                    continue

                snap = self._gestures.update(frame)

                if snap.peace_out:
                    print("[VSE] Ação: peace out — sumindo...")
                    self._disappear.start_fade_out()
                if snap.fade_in:
                    print("[VSE] Ação: punho — voltando...")
                    self._disappear.start_fade_in()
                if snap.toggle_ar:
                    state = "ON" if self._gestures.ar_enabled else "OFF"
                    print(f"[VSE] Óculos AR: {state}")

                key = cv2.waitKey(1) & 0xFF
                if key not in (0, 255) and not self._handle_keys(key):
                    break

                frame_out = self._identity.apply(frame)
                if self._gestures.ar_enabled:
                    frame_out = self._ar.apply(frame_out, snap.face_landmarks)
                frame_out = self._disappear.apply(frame_out)
                self._output.send(frame_out)

                if self._config.preview_window:
                    preview = frame_out.copy()
                    if self._show_landmarks:
                        draw_hand_landmarks(preview, snap.hand_landmarks)
                        if snap.face_landmarks:
                            draw_face_landmarks(preview, snap.face_landmarks)

                    mode = "ar" if self._gestures.ar_enabled else "normal"
                    cv2.putText(
                        preview,
                        f"modo: {mode}",
                        (16, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    if self._disappear.is_active:
                        cv2.putText(
                            preview,
                            "acao: fade",
                            (16, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 200, 255),
                            2,
                            cv2.LINE_AA,
                        )
                    cv2.imshow(PREVIEW_WINDOW_NAME, preview)
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Libera câmera, modelos e janelas (idempotente)."""
        if self._shutdown_done:
            return
        self._shutdown_done = True
        self._gestures.close()
        for filt in self._filters.values():
            filt.close()
        self._input.release()
        self._output.close()
        if self._config.preview_window:
            cv2.destroyAllWindows()
