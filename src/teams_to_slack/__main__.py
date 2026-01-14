"""CLI wrapper to reuse migrate.py entrypoint."""

from pathlib import Path
import sys


def main() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    from migrate import main as run_main

    run_main()


if __name__ == "__main__":
    main()
