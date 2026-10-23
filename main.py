"""Ponto de entrada do VSE."""

from core.engine import VirtualStreamEngine


def main() -> None:
    """CLI: inicia o Virtual Stream Engine."""
    VirtualStreamEngine().run()


if __name__ == "__main__":
    main()
