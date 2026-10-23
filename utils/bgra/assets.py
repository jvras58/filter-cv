"""Carregamento e transformação de assets BGRA."""

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
