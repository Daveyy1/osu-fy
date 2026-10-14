"""The ports the core needs. Adapters and the UI implement them (ADR-005)."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from osu_fy.core.songs import Beatmapset


class PlayerQuit(Exception):
    """The Player pressed q at a prompt: the Session ends."""


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


class Source(Protocol):
    """Where the Songs come from: osu!lazer for now."""

    def find_lazer_folder(self) -> Path | None: ...

    def is_lazer_folder(self, path: Path) -> bool: ...

    def read_beatmapsets(
        self, folder: Path, progress: Callable[[int, int], None]
    ) -> list[Beatmapset]:
        """Calls progress(done, total) after each file it reads."""
        ...
