"""Loop principal do VSE: captura → gestos → filtros → saída virtual."""

from __future__ import annotations

import cv2

from config.settings import DEFAULT_STREAM_CONFIG, StreamConfig
from core.camera_stream import CameraStream
from core.frame_processor import FrameProcessor
from core.gesture_events import apply_gesture_events
from core.gesture_hub import GestureHub
from core.keyboard_handler import KeyboardHandler
from core.preview import show_preview
from core.virtual_cam_output import VirtualCamOutput
from filters.actions.disappear_fade import DisappearFadeAction
from filters.face_mesh_filter import FaceMeshFilter
from filters.registry import FilterFactoryContext, build_filters


class VirtualStreamEngine:
    """Monta dependências, executa o loop e garante shutdown limpo."""

    def __init__(self, config: StreamConfig | None = None) -> None:
        self._config = config or DEFAULT_STREAM_CONFIG
        self._input = CameraStream(
            self._config.device_id,
            self._config.width,
            self._config.height,
            self._config.fps,
        )
        background = self._input.capture_static_background(
            self._config.background_capture_seconds
        )
        filters = build_filters(FilterFactoryContext(config=self._config))
        ar_filter = filters["ar"]
        assert isinstance(ar_filter, FaceMeshFilter)

        self._disappear = DisappearFadeAction(background)
        self._gestures = GestureHub(self._config)
        self._keyboard = KeyboardHandler(
            self._disappear,
            show_landmarks_initial=self._config.show_landmarks,
        )
        self._pipeline = FrameProcessor(filters["normal"], ar_filter, self._disappear)
        self._filters = filters
        self._output = VirtualCamOutput(
            self._config.width,
            self._config.height,
            self._config.fps,
        )
        self._running = True
        self._shutdown_done = False

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
                apply_gesture_events(snap, self._gestures, self._disappear)

                key = cv2.waitKey(1) & 0xFF
                if key not in (0, 255) and not self._keyboard.handle(key):
                    break

                frame_out = self._pipeline.process(
                    frame,
                    snap,
                    self._gestures.ar_enabled,
                )
                self._output.send(frame_out)

                if self._config.preview_window:
                    show_preview(
                        frame_out,
                        snap,
                        show_landmarks=self._keyboard.show_landmarks,
                        ar_enabled=self._gestures.ar_enabled,
                        fade_active=self._disappear.is_active,
                    )
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
