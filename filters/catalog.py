"""Mapa nome → factory de cada filtro (hot-swap / registro)."""

from filters.base_filter import VideoFilter
from filters.context import FilterFactory, FilterFactoryContext
from filters.face_mesh_filter import FaceMeshFilter
from filters.identity_filter import IdentityFilter


def _identity_factory(_ctx: FilterFactoryContext) -> VideoFilter:
    return IdentityFilter()


def _ar_factory(ctx: FilterFactoryContext) -> VideoFilter:
    return FaceMeshFilter(str(ctx.config.overlay_asset_path))


FILTER_FACTORIES: dict[str, FilterFactory] = {
    "normal": _identity_factory,
    "ar": _ar_factory,
}
