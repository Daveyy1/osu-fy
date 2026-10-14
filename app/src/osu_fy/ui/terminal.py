"""The Player port in a terminal: rich for output, readchar for key presses."""

from pathlib import Path

import readchar
from rich.console import Console

from osu_fy.core.ports import PlayerQuit

YES = (readchar.key.ENTER, "y", "Y")
NO = ("n", "N")
QUIT = ("q", "Q")


class TerminalPlayer:
    def __init__(self, console: Console) -> None:
        self._console = console

    def greet(self) -> None:
        self._console.print("osu-fy — your osu! Songs, on Spotify")
        self._console.print("Press q to quit.")

    def wait_for_quit(self) -> None:
        while readchar.readkey().lower() != "q":
            pass

    def confirm_lazer_folder(self, path: Path) -> bool:
        self._say(str(path))
        self._say("Use this lazer folder? [Y/n] ", end="")
        while (key := readchar.readkey()) not in YES + NO + QUIT:
            pass
        self._console.print()
        if key in QUIT:
            raise PlayerQuit
        return key in YES

    def ask_lazer_folder(self) -> Path:
        typed = self._console.input("Path to the lazer folder: ")
        typed = typed.strip().strip("\"'")  # Explorer's "Copy as path" adds quotes
        if typed in QUIT:
            raise PlayerQuit
        return Path(typed).absolute()

    def show_no_lazer_data(self, path: Path) -> None:
        self._say(f"No lazer data found in {path}")

    def show_reading_lazer_folder(self, path: Path) -> None:
        self._say(f"Reading lazer folder {path}")

    def _say(self, text: str, end: str = "\n") -> None:
        # A path prints as it is: "[old]" is no markup, and the terminal wraps it
        self._console.print(text, end=end, markup=False, soft_wrap=True)
