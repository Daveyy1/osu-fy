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
        # markup=False: a folder name like "[old]" must print as it is
        self._console.print(str(path), markup=False)
        self._console.print("Use this lazer folder? [Y/n] ", end="", markup=False)
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
        self._console.print(f"No lazer data found in {path}", markup=False)

    def show_reading_lazer_folder(self, path: Path) -> None:
        self._console.print(f"Reading lazer folder {path}", markup=False)
