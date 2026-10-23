"""Ponto de entrada do VSE."""

from core.engine import VirtualStreamEngine


def main() -> None:
    VirtualStreamEngine().run()


if __name__ == "__main__":
    main()
