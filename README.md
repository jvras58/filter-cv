# Virtual Stream Engine (VSE)

Webcam → gestos → filtros/ações → câmera virtual (Teams, Zoom, Discord).

## Requisitos

- Python **3.12+**
- [Poetry](https://python-poetry.org/)
- Linux: módulo `v4l2loopback` e dispositivo `/dev/video*` para a câmera virtual

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="VSE Virtual Cam"
```

## Instalação

```bash
poetry install
poetry run python scripts/generate_default_overlay.py
```

## Uso

```bash
poetry run vse
# ou
poetry run python main.py
```

### Gestos

| Gesto | Efeito |
|-------|--------|
| ✌️ (peace, mão grande no quadro) | Some no fundo congelado |
| Punho fechado | Volta a aparecer |
| Toque no olho (indicador perto do olho) | Liga/desliga óculos AR |

### Teclado

| Tecla | Ação |
|-------|------|
| `D` | Liga/desliga pontos de mão/rosto (debug) |
| `A` | Voltar do fade (fallback) |
| `Q` | Sair |

Na inicialização, saia do quadro ~2s para capturar o fundo do fade.

---

## Guia de manutenção

Use esta tabela para saber **onde editar** sem percorrer o projeto inteiro.

| O que você quer fazer | Arquivo(s) | Notas |
|----------------------|------------|--------|
| **Novo gesto** (ex.: acenar) | `core/gestures/hand_pose.py` ou `eye_touch.py` | Heurística pura em landmarks normalizados |
| **Disparar ação ao reconhecer gesto** | `core/gestures/hub.py` | Debounce, cooldown, flags no `GestureSnapshot` |
| **Novo campo no resultado do frame** | `core/gestures/types.py` | `GestureSnapshot` |
| **Log / efeito ao disparar evento** | `core/gesture_events.py` | Peace, punho, toggle AR |
| **Sensibilidade dos gestos** | `config/settings.py` | `gesture_stable_frames`, `min_hand_span_ratio`, `eye_touch_radius_factor` |
| **Novo filtro de vídeo** | `filters/catalog.py` + classe em `filters/` | Implemente `VideoFilter` (`base_filter.py`) |
| **Tipos do factory de filtros** | `filters/context.py` | `FilterFactoryContext` |
| **Montar lista de filtros** | `filters/registry.py` | `build_filters()` — raramente precisa mudar |
| **Óculos / overlay AR** | `filters/ar/glasses_renderer.py`, asset em `assets/` | Landmarks em `filters/ar/landmarks.py` |
| **Ação “sumir” (fade)** | `filters/actions/disappear_fade.py` | Velocidade: `_ALPHA_STEP` |
| **Ordem do pipeline** | `core/frame_processor.py` | normal → AR → fade |
| **Preview / HUD** | `core/preview.py` | Não vai para a câmera virtual |
| **Teclas globais** | `core/keyboard_handler.py`, constantes em `core/keys.py` |
| **Loop principal** | `core/engine.py` | Só orquestração; lógica pesada fica nos módulos acima |
| **Webcam entrada** | `core/camera_stream.py` | Resolução/FPS também em `config/settings.py` |
| **Câmera virtual saída** | `core/virtual_cam_output.py` |
| **Download modelos MediaPipe** | `utils/mediapipe/models.py` | URLs dos `.task` em `assets/models/` |
| **Desenho debug landmarks** | `utils/mediapipe/debug_draw.py` | Ligado com `D` no preview |
| **Composição PNG transparente** | `utils/bgra/assets.py`, `utils/bgra/blend.py` |
| **Resolução, device, paths** | `config/settings.py` | Futuro: YAML pode substituir este módulo |
| **Entrada CLI** | `main.py` | Delega para `core/engine.py` |
| **Spec / requisitos de produto** | `docs/spec.md` | Referência histórica do MVP |

### Fluxo de um frame (leitura rápida)

```
camera_stream.read_frame()
  → gesture_hub.update()     # mão + rosto, eventos no snapshot
  → gesture_events           # fade / log AR
  → keyboard_handler         # D, A, Q
  → frame_processor          # identity → AR (se on) → disappear
  → virtual_cam_output.send()
  → preview (opcional)
```

### Estrutura de pastas

```
main.py
config/settings.py
docs/spec.md

core/
  engine.py
  frame_processor.py
  gesture_events.py
  keyboard_handler.py
  preview.py
  camera_stream.py
  virtual_cam_output.py
  keys.py
  gesture_hub.py          # reexport: GestureHub, GestureSnapshot
  gestures/
    hub.py
    hand_pose.py
    eye_touch.py
    types.py

filters/
  context.py
  catalog.py
  registry.py
  base_filter.py
  identity_filter.py
  face_mesh_filter.py
  ar/
    landmarks.py
    glasses_renderer.py
  actions/
    disappear_fade.py

utils/
  mediapipe/
    models.py
    debug_draw.py
  bgra/
    assets.py
    blend.py

assets/
scripts/
```

### Checklist: novo filtro

1. Criar `filters/meu_filtro.py` herdando `VideoFilter`.
2. Registrar factory em `filters/catalog.py` (`FILTER_FACTORIES`).
3. Se o filtro depende de gesto, estender `GestureSnapshot` + `hub.py` + `gesture_events.py` + `frame_processor.py`.
4. Rodar `poetry run pyright .` na raiz do projeto.

### Checklist: novo gesto

1. Função de detecção em `hand_pose.py` ou `eye_touch.py`.
2. Usar em `gestures/hub.py` (`_poses_this_frame` + estabilidade em `_apply_stability`).
3. Se gera ação nova, campo em `types.py` e handler em `gesture_events.py` (e pipeline se alterar vídeo).
