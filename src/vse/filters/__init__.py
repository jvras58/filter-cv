"""Filter registry — add new filters here without touching capture/output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from vse.config import StreamConfig
from vse.filters.base_filter import VideoFilter
from vse.filters.face_mesh_filter import FaceMeshFilter
from vse.filters.fade_meme_filter import FadeMemeFilter
from vse.filters.identity_filter import IdentityFilter


@dataclass(frozen=True)
class FilterFactoryContext:
    """Dependencies injected when constructing filters."""

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


# Register new filters by adding an entry (hot-swap key is defined in vse.keys).
FILTER_FACTORIES: dict[str, FilterFactory] = {
    "normal": _identity_factory,
    "meme": _meme_factory,
    "ar": _ar_factory,
}


def build_filters(ctx: FilterFactoryContext) -> dict[str, VideoFilter]:
    return {name: factory(ctx) for name, factory in FILTER_FACTORIES.items()}
