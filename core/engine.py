"""Virtual Stream Engine orchestrator and main loop."""

from __future__ import annotations

import cv2

from config.settings import DEFAULT_STREAM_CONFIG, StreamConfig
from core.camera_stream import CameraStream
from core.keys import (
    FILTER_HOTKEYS,
    KEY_FADE_IN,
    KEY_FADE_IN_UPPER,
    KEY_QUIT,
    KEY_QUIT_UPPER,
    PREVIEW_WINDOW_NAME,
)
from core.peace_sign_detector import PeaceSignDetector
from core.virtual_cam_output import VirtualCamOutput
from filters.actions.disappear_fade import DisappearFadeAction
from filters.base_filter import VideoFilter
from filters.registry import FilterFactoryContext, build_filters


class VirtualStreamEngine:
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
        ctx = FilterFactoryContext(config=self._config)
        self._filters: dict[str, VideoFilter] = build_filters(ctx)
        self._active_filter: VideoFilter = self._filters["normal"]
        self._active_name = "normal"
        self._disappear = DisappearFadeAction(background)
        self._gestures = PeaceSignDetector(fps=self._config.fps)
        self._output = VirtualCamOutput(
            self._config.width,
            self._config.height,
            self._config.fps,
        )
        self._running = True
        self._shutdown_done = False

    def _handle_global_keys(self, key: int) -> bool:
        if key in (KEY_QUIT, KEY_QUIT_UPPER):
            return False

        filter_name = FILTER_HOTKEYS.get(key)
        if filter_name is not None:
            self._active_filter = self._filters[filter_name]
            self._active_name = filter_name
            print(f"[VSE] Filtro ativo: {filter_name}")

        if key in (KEY_FADE_IN, KEY_FADE_IN_UPPER):
            self._disappear.start_fade_in()

        return True

    def run(self) -> None:
        print(
            "[VSE] 1=normal | 3=AR | ✌️=sumir | mão aberta=voltar | A=volta (teclado) | Q=sair\n"
        )

        try:
            while self._running:
                frame = self._input.read_frame()
                if frame is None:
                    continue

                fade_out, fade_in = self._gestures.update(frame)
                if fade_out:
                    print("[VSE] Ação: peace out — sumindo...")
                    self._disappear.start_fade_out()
                if fade_in:
                    print("[VSE] Ação: mão aberta — voltando...")
                    self._disappear.start_fade_in()

                key = cv2.waitKey(1) & 0xFF
                if key not in (0, 255):
                    if not self._handle_global_keys(key):
                        break
                    if key not in FILTER_HOTKEYS:
                        self._active_filter.handle_input(key)

                frame_out = self._active_filter.apply(frame)
                frame_out = self._disappear.apply(frame_out)
                self._output.send(frame_out)

                if self._config.preview_window:
                    preview = frame_out.copy()
                    cv2.putText(
                        preview,
                        f"filter: {self._active_name}",
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
