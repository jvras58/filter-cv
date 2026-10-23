"""Reage aos eventos do ``GestureSnapshot`` (log + side effects)."""

from core.gestures.hub import GestureHub
from core.gestures.types import GestureSnapshot
from filters.actions.disappear_fade import DisappearFadeAction


def apply_gesture_events(
    snap: GestureSnapshot,
    gestures: GestureHub,
    disappear: DisappearFadeAction,
) -> None:
    """Dispara ações de fade e imprime mudanças de modo AR."""
    if snap.peace_out:
        print("[VSE] Ação: peace out — sumindo...")
        disappear.start_fade_out()
    if snap.fade_in:
        print("[VSE] Ação: punho — voltando...")
        disappear.start_fade_in()
    if snap.toggle_ar:
        state = "ON" if gestures.ar_enabled else "OFF"
        print(f"[VSE] Óculos AR: {state}")
