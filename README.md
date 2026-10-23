# Virtual Stream Engine (VSE)

Webcam → filtros modulares → câmera virtual (Teams, Zoom, Discord).

## Requisitos

- Python **3.12+**
- [Poetry](https://python-poetry.org/)
- Linux: módulo `v4l2loopback` e dispositivo `/dev/video*` para a câmera virtual

```bash
# Exemplo (Debian/Ubuntu)
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="VSE Virtual Cam"
```

## Instalação

```bash
poetry install
poetry run python scripts/generate_default_overlay.py   # asset AR padrão
# O modelo Face Landmarker é baixado automaticamente na 1ª execução do filtro AR.
```

## Uso

```bash
poetry run vse
# ou
poetry run python main.py
```

| Tecla | Ação |
|-------|------|
| `1` | Filtro normal |
| `2` | Meme (fade) — `S` some, `A` volta |
| `3` | AR (óculos) |
| `Q` | Sair |

Na inicialização, saia do quadro por ~2s para capturar o fundo do filtro meme.

## Estrutura

```
src/vse/
  engine.py              # orquestrador
  camera_stream.py         # entrada
  virtual_cam_output.py    # saída
  config.py              # defaults (futuro: YAML)
  filters/
    base_filter.py
    identity_filter.py
    fade_meme_filter.py
    face_mesh_filter.py
    __init__.py            # registry de filtros
  utils/overlay.py
assets/                    # PNGs de overlay
```

Para um novo filtro: implemente `VideoFilter`, registre em `filters/__init__.py` (`FILTER_FACTORIES`) e adicione hotkey em `keys.py` + `engine.py` se necessário.
