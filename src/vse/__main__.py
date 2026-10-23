"""CLI entry: ``python -m vse`` or ``poetry run vse``."""

from vse.engine import VirtualStreamEngine


def main() -> None:
    VirtualStreamEngine().run()


if __name__ == "__main__":
    main()
