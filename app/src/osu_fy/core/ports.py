"""The ports the core needs. Adapters and the UI implement them (ADR-005)."""

from pathlib import Path
from typing import Protocol


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


class Source(Protocol):
    """Where the Songs come from: osu!lazer for now."""

    def find_lazer_folder(self) -> Path | None: ...

    def is_lazer_folder(self, path: Path) -> bool: ...
