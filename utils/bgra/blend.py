"""Composição alpha de overlay BGRA sobre frame BGR."""

from __future__ import annotations

import numpy as np


def blend_bgra_on_bgr(
    frame_bgr: np.ndarray,
    overlay_bgra: np.ndarray,
    anchor_x: int,
    anchor_y: int,
) -> np.ndarray:
    """Alpha-composite in-place; âncora = centro do overlay."""
    frame_h, frame_w = frame_bgr.shape[:2]
    oh, ow = overlay_bgra.shape[:2]

    x1 = anchor_x - ow // 2
    y1 = anchor_y - oh // 2
    x2 = x1 + ow
    y2 = y1 + oh

    if x2 <= 0 or y2 <= 0 or x1 >= frame_w or y1 >= frame_h:
        return frame_bgr

    ox1 = max(0, -x1)
    oy1 = max(0, -y1)
    ox2 = ow - max(0, x2 - frame_w)
    oy2 = oh - max(0, y2 - frame_h)

    fx1 = max(0, x1)
    fy1 = max(0, y1)
    fx2 = min(frame_w, x2)
    fy2 = min(frame_h, y2)

    overlay_crop = overlay_bgra[oy1:oy2, ox1:ox2]
    if overlay_crop.size == 0:
        return frame_bgr

    roi = frame_bgr[fy1:fy2, fx1:fx2]
    alpha = overlay_crop[:, :, 3:4].astype(np.float32) / 255.0
    overlay_rgb = overlay_crop[:, :, :3].astype(np.float32)
    base = roi.astype(np.float32)

    blended = alpha * overlay_rgb + (1.0 - alpha) * base
    frame_bgr[fy1:fy2, fx1:fx2] = np.clip(blended, 0, 255).astype(np.uint8)
    return frame_bgr
