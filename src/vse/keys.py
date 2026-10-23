"""Global keyboard contract (orchestrator + filters)."""

KEY_NORMAL = ord("1")
KEY_MEME = ord("2")
KEY_AR = ord("3")
KEY_QUIT = ord("q")
KEY_FADE_OUT = ord("s")
KEY_FADE_IN = ord("a")

# Aliases for uppercase (cv2.waitKey returns the key code as-is on most platforms).
KEY_QUIT_UPPER = ord("Q")
KEY_FADE_OUT_UPPER = ord("S")
KEY_FADE_IN_UPPER = ord("A")

FILTER_HOTKEYS: dict[int, str] = {
    KEY_NORMAL: "normal",
    KEY_MEME: "meme",
    KEY_AR: "ar",
}

PREVIEW_WINDOW_NAME = "VSE Preview"
