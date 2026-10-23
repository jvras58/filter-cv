"""Global keyboard contract (orchestrator + filters)."""

KEY_NORMAL = ord("1")
KEY_AR = ord("3")
KEY_QUIT = ord("q")
KEY_FADE_IN = ord("a")

KEY_QUIT_UPPER = ord("Q")
KEY_FADE_IN_UPPER = ord("A")

FILTER_HOTKEYS: dict[int, str] = {
    KEY_NORMAL: "normal",
    KEY_AR: "ar",
}

PREVIEW_WINDOW_NAME = "VSE Preview"
