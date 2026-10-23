# Virtual Stream Engine (VSE)

Webcam → gestos → filtros/ações → câmera virtual (Teams, Zoom, Discord).

Documentação técnica, requisitos e **guia de manutenção:** [docs/spec.md](docs/spec.md) (em especial [§8 Guia de manutenção](docs/spec.md#8-guia-de-manutenção)).

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

Sensibilidade dos gestos: `config/settings.py` (`gesture_stable_frames`, `min_hand_span_ratio`, `eye_touch_radius_factor`). Detalhes em [spec §2.3](docs/spec.md#23-gestos-contrato-principal).

## Desenvolvimento

| Precisa de… | Onde |
|-------------|------|
| Saber **qual arquivo editar** | [spec.md §8](docs/spec.md#8-guia-de-manutenção) |
| Requisitos, contratos, aceite | [spec.md](docs/spec.md) |
| Validar tipos | `poetry run pyright .` |
