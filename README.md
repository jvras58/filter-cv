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
| `3` | AR (óculos) |
| ✌️ (gesto) | Ação **peace out** — some no fundo congelado |
| Mão aberta | Volta a aparecer |
| `A` | Voltar (atalho de teclado) |
| `Q` | Sair |

Na inicialização, saia do quadro por ~2s para capturar o fundo do filtro meme.

## Estrutura

```
main.py
core/
  engine.py
  camera_stream.py
  virtual_cam_output.py
  keys.py
config/
  settings.py
filters/
  registry.py
  actions/disappear_fade.py
  …
core/peace_sign_detector.py
utils/
assets/
```

Novo filtro: implemente `VideoFilter`, registre em `filters/registry.py` e, se precisar, hotkey em `core/keys.py`.
