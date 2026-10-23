"""Tipos compartilhados do pipeline de gestos."""

from dataclasses import dataclass, field

Landmark3D = tuple[float, float, float]
HandLandmarks = list[Landmark3D]
FaceLandmarks = list[Landmark3D]


@dataclass
class GestureSnapshot:
    """Resultado de um frame: landmarks + eventos disparados neste tick."""

    hand_landmarks: list[HandLandmarks] = field(default_factory=list)
    face_landmarks: FaceLandmarks | None = None
    peace_out: bool = False
    fade_in: bool = False
    toggle_ar: bool = False
