"""Registro de filtros — adicione novos módulos aqui sem alterar captura/saída."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from config.settings import StreamConfig
from filters.base_filter import VideoFilter
from filters.face_mesh_filter import FaceMeshFilter
from filters.fade_meme_filter import FadeMemeFilter
from filters.identity_filter import IdentityFilter


@dataclass(frozen=True)
class FilterFactoryContext:
    background_frame: np.ndarray
    config: StreamConfig


FilterFactory = Callable[[FilterFactoryContext], VideoFilter]


def _identity_factory(_ctx: FilterFactoryContext) -> VideoFilter:
    return IdentityFilter()


def _meme_factory(ctx: FilterFactoryContext) -> VideoFilter:
    return FadeMemeFilter(ctx.background_frame)


def _ar_factory(ctx: FilterFactoryContext) -> VideoFilter:
    return FaceMeshFilter(
        str(ctx.config.overlay_asset_path),
        fps=ctx.config.fps,
    )


# Novo filtro: implemente VideoFilter e registre aqui (hotkeys em core/keys.py).
FILTER_FACTORIES: dict[str, FilterFactory] = {
    "normal": _identity_factory,
    "meme": _meme_factory,
    "ar": _ar_factory,
}


def build_filters(ctx: FilterFactoryContext) -> dict[str, VideoFilter]:
    return {name: factory(ctx) for name, factory in FILTER_FACTORIES.items()}
