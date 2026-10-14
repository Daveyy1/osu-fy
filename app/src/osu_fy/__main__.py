"""The `osu-fy` command: wires the adapters and the UI into the core (ADR-005)."""

from rich.console import Console

from osu_fy.core.session import run_session
from osu_fy.ui.terminal import TerminalPlayer


def main() -> None:
    try:
        run_session(TerminalPlayer(Console()))
    except KeyboardInterrupt:
        pass  # Ctrl+C quits quietly: no traceback for the Player (persona)


if __name__ == "__main__":
    main()
