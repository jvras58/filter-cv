"""Montagem do conjunto de filtros a partir do catálogo."""

from filters.base_filter import VideoFilter
from filters.catalog import FILTER_FACTORIES
from filters.context import FilterFactory, FilterFactoryContext

__all__ = [
    "FilterFactory",
    "FilterFactoryContext",
    "build_filters",
]


def build_filters(ctx: FilterFactoryContext) -> dict[str, VideoFilter]:
    """Instancia todos os filtros registrados em ``FILTER_FACTORIES``."""
    return {name: factory(ctx) for name, factory in FILTER_FACTORIES.items()}
