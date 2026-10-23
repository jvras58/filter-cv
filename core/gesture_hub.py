"""Facade: importe ``GestureHub`` daqui (implementação em ``core.gestures``)."""

from core.gestures.hub import GestureHub
from core.gestures.types import GestureSnapshot

__all__ = ["GestureHub", "GestureSnapshot"]
