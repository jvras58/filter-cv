"""``poetry run vse`` / ``python -m vse`` entry point."""

from core.engine import VirtualStreamEngine


def main() -> None:
    VirtualStreamEngine().run()


if __name__ == "__main__":
    main()
