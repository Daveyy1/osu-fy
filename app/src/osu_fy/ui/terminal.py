"""The Player port in a terminal: rich for output, readchar for key presses."""

import msvcrt
from pathlib import Path

import readchar
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn

from osu_fy.core.ports import PlayerQuit

YES = (readchar.key.ENTER, "y", "Y")
NO = ("n", "N")
QUIT = ("q", "Q")


class TerminalPlayer:
    def __init__(self, console: Console) -> None:
        self._console = console
        self._progress: Progress | None = None

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

    def show_files_read(self, done: int, total: int) -> None:
        if self._progress is None:
            self._progress = Progress(
                TextColumn("Reading lazer folder"),
                BarColumn(),
                TextColumn("{task.completed:,.0f}/{task.total:,.0f} files"),
                console=self._console,
            )
            self._progress.add_task("", total=total)
            self._progress.start()
        self._progress.update(self._progress.task_ids[0], completed=done)
        if done == total:
            self._progress.stop()
            self._progress = None

    def show_songs_found(self, songs: int, beatmapsets: int) -> None:
        self._say(f"Found {songs} Songs in {beatmapsets} Beatmapsets")

    def show_spotify_setup_guide(self) -> None:
        self._say(
            "osu-fy talks to Spotify through a Spotify app of your own. Set it up once:"
        )
        self._say("  1. Open https://developer.spotify.com/dashboard and log in.")
        self._say("  2. Create an app and tick Web API as the API it uses.")
        self._say("  3. Add this redirect URI, exactly: http://127.0.0.1:8765/callback")
        self._say("  4. Save, then copy the app's Client ID.")
        self._say(
            "Or ask a friend to add you to their Spotify app and use its Client ID."
        )

    def ask_client_id(self) -> str:
        typed = self._console.input("Client ID: ").strip().strip("\"'")
        if typed in QUIT:
            raise PlayerQuit
        return typed

    def show_not_a_client_id(self) -> None:
        self._say("That does not look like a Client ID")

    def show_waiting_for_login(self, login_url: str | None) -> None:
        if login_url is not None:
            self._say(f"Open this link to log in: {login_url}")
        self._say(
            "Waiting for the login in your browser… press t to try again, "
            "c for another Client ID, q to quit"
        )

    def key_pressed_while_waiting(self) -> str | None:
        # shortcut: msvcrt is Windows only and readchar cannot check without waiting;
        # macOS and Linux need a select()-based check when they are added (roadmap)
        while msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == "\x03":
                raise KeyboardInterrupt  # Ctrl+C, as readchar does at the other prompts
            if key in QUIT:
                raise PlayerQuit
            if key.lower() in ("t", "c"):
                return key.lower()
        return None

    def show_login_incomplete(self) -> None:
        self._say("The login did not complete.")

    def ask_login_retry(self) -> str:
        self._say("Try again [t], enter another Client ID [c] or quit [q] ", end="")
        while (key := readchar.readkey()) not in ("t", "T", "c", "C") + QUIT:
            pass
        self._console.print()
        if key in QUIT:
            raise PlayerQuit
        return key.lower()

    def show_logged_in(self, name: str) -> None:
        self._say(f"Logged in to Spotify as {name}")

    def _say(self, text: str, end: str = "\n") -> None:
        # A path prints as it is: "[old]" is no markup, and the terminal wraps it
        self._console.print(text, end=end, markup=False, soft_wrap=True)
