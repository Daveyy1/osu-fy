"""The `osu-fy` command: wires the adapters and the UI into the core (ADR-005)."""

import os
from pathlib import Path

from rich.console import Console

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.ports import PlayerQuit
from osu_fy.core.session import run_session
from osu_fy.core.settings import SettingsUnreadable
from osu_fy.ui.terminal import TerminalPlayer


def main() -> None:
    console = Console()
    roaming = Path(os.environ["APPDATA"])  # Windows only for now (roadmap)
    try:
        run_session(TerminalPlayer(console), LazerSource(roaming), roaming / "osu-fy")
    except SettingsUnreadable as error:
        console.print(str(error), markup=False, soft_wrap=True)
    except (KeyboardInterrupt, PlayerQuit):
        pass  # Ctrl+C or q quits quietly: no traceback for the Player (persona)


if __name__ == "__main__":
    main()
