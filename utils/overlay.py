"""BGRA overlay compositing helpers."""

from __future__ import annotations

import cv2
import numpy as np


def load_bgra_asset(path: str) -> np.ndarray:
    """Carrega PNG (ou similar) garantindo canal alpha."""
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Overlay asset not found: {path}")
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
    elif image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    return image


def transform_overlay(
    asset_bgra: np.ndarray,
    target_width: float,
    angle_deg: float,
) -> np.ndarray:
    """Redimensiona pela largura alvo e rotaciona em torno do centro."""
    if target_width <= 1:
        return asset_bgra

    h, w = asset_bgra.shape[:2]
    scale = target_width / float(w)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = cv2.resize(asset_bgra, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    center = (new_w // 2, new_h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    return cv2.warpAffine(
        resized,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )


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
