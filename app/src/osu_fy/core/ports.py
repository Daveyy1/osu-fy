"""The ports the core needs. Adapters and the UI implement them (ADR-005)."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from osu_fy.core.songs import Beatmapset


class PlayerQuit(Exception):
    """The Player pressed q at a prompt: the Session ends."""


class LoginIncomplete(Exception):
    """The browser login was refused, abandoned or stopped by the Player (US-03.4)."""


class StreamingServiceUnavailable(Exception):
    """The Session stops and shows this message, without a traceback (US-03.8)."""


class Player(Protocol):
    """Everything osu-fy shows the Player or asks them. The core never prints."""

    def greet(self) -> None: ...

    def wait_for_quit(self) -> None: ...

    def confirm_lazer_folder(self, path: Path) -> bool: ...

    def ask_lazer_folder(self) -> Path: ...

    def show_no_lazer_data(self, path: Path) -> None: ...

    def show_reading_lazer_folder(self, path: Path) -> None: ...

    def show_files_read(self, done: int, total: int) -> None: ...

    def show_songs_found(self, songs: int, beatmapsets: int) -> None: ...

    def show_spotify_setup_guide(self) -> None: ...

    def ask_client_id(self) -> str: ...

    def show_not_a_client_id(self) -> None: ...

    def show_waiting_for_login(self, login_url: str | None) -> None:
        """login_url is set only when no browser could be opened."""
        ...

    def key_pressed_while_waiting(self) -> str | None:
        """t or c if pressed since the last call, else None; raises PlayerQuit on q."""
        ...

    def show_login_incomplete(self) -> None: ...

    def ask_login_retry(self) -> str:
        """t or c; raises PlayerQuit on q."""
        ...

    def show_logged_in(self, name: str) -> None: ...


class Source(Protocol):
    """Where the Songs come from: osu!lazer for now."""

    def find_lazer_folder(self) -> Path | None: ...

    def is_lazer_folder(self, path: Path) -> bool: ...

    def read_beatmapsets(
        self, folder: Path, progress: Callable[[int, int], None]
    ) -> list[Beatmapset]:
        """Calls progress(done, total) after each file it reads."""
        ...


class StreamingService(Protocol):
    """Where the Playlist lives: Spotify for now. No operation removes or reorders (N1)."""

    def log_in(self, client_id: str, keep_waiting: Callable[[str | None], bool]) -> str:
        """The Player's display name; opens the browser only without a usable login.

        While waiting for the browser, calls keep_waiting(login_url) about once a
        second and raises LoginIncomplete when it returns False, on a refusal, or
        after 3 minutes (US-03.4).
        """
        ...
