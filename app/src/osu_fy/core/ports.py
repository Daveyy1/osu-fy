"""The ports the core needs. Adapters and the UI implement them (ADR-005)."""

from typing import Protocol


class Player(Protocol):
    """Everything osu-fy shows the Player or asks them. The core never prints."""

    def greet(self) -> None: ...

    def wait_for_quit(self) -> None: ...
