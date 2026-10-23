"""Generate a simple thug-life style glasses PNG for local development."""

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "oculos_thug_life.png"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    w, h = 420, 120
    canvas = np.zeros((h, w, 4), dtype=np.uint8)

    # Lenses (dark) + bridge + arms.
    cv2.ellipse(canvas, (110, 60), (70, 42), 0, 0, 360, (20, 20, 20, 230), -1)
    cv2.ellipse(canvas, (310, 60), (70, 42), 0, 0, 360, (20, 20, 20, 230), -1)
    cv2.rectangle(canvas, (175, 52), (245, 68), (30, 30, 30, 255), -1)
    cv2.line(canvas, (40, 58), (40, 60), (0, 0, 0, 255), 8)
    cv2.line(canvas, (380, 58), (380, 60), (0, 0, 0, 255), 8)

    cv2.imwrite(str(OUT), canvas)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
