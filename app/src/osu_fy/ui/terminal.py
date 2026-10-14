"""The Player port in a terminal: rich for output, readchar for key presses."""

import readchar
from rich.console import Console


class TerminalPlayer:
    def __init__(self, console: Console) -> None:
        self._console = console

    def greet(self) -> None:
        self._console.print("osu-fy — your osu! Songs, on Spotify")
        self._console.print("Press q to quit.")

    def wait_for_quit(self) -> None:
        while readchar.readkey().lower() != "q":
            pass
