"""Registro de filtros — adicione factories aqui sem alterar captura/saída."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from config.settings import StreamConfig
from filters.base_filter import VideoFilter
from filters.face_mesh_filter import FaceMeshFilter
from filters.identity_filter import IdentityFilter


@dataclass(frozen=True)
class FilterFactoryContext:
    """Dependências passadas ao construir cada filtro."""

    config: StreamConfig


FilterFactory = Callable[[FilterFactoryContext], VideoFilter]


def _identity_factory(_ctx: FilterFactoryContext) -> VideoFilter:
    return IdentityFilter()


def _ar_factory(ctx: FilterFactoryContext) -> VideoFilter:
    return FaceMeshFilter(str(ctx.config.overlay_asset_path))


FILTER_FACTORIES: dict[str, FilterFactory] = {
    "normal": _identity_factory,
    "ar": _ar_factory,
}


def build_filters(ctx: FilterFactoryContext) -> dict[str, VideoFilter]:
    """Instancia todos os filtros registrados em ``FILTER_FACTORIES``."""
    return {name: factory(ctx) for name, factory in FILTER_FACTORIES.items()}
