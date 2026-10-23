"""Tipos compartilhados na construção de filtros."""

from dataclasses import dataclass
from typing import Callable

from config.settings import StreamConfig
from filters.base_filter import VideoFilter


@dataclass(frozen=True)
class FilterFactoryContext:
    """Dependências passadas ao construir cada filtro."""

    config: StreamConfig


FilterFactory = Callable[[FilterFactoryContext], VideoFilter]
