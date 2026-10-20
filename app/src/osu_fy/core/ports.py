"""The ports the core needs. Adapters and the UI implement them (ADR-005)."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from osu_fy.core.songs import Beatmapset


class PlayerQuit(Exception):
    """The Player pressed q at a prompt: the Session ends."""


class LoginIncomplete(Exception):
    """The browser login was refused, abandoned or stopped by the Player (US-03.4)."""


class StreamingServiceUnavailable(Exception):
    """The Session stops and shows this message, without a traceback (US-03.8)."""


@dataclass(frozen=True)
class Playlist:
    id: str
    name: str
    link: str


@dataclass(frozen=True)
class Track:
    id: str
    title: str
    artists: tuple[str, ...]
    album: str
    length_ms: int


class Player(Protocol):
    """Everything osu-fy shows the Player or asks them. The core never prints."""

    def greet(self) -> None: ...

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

    def ask_playlist_name(self, default: str) -> str:
        """The typed name, or default on Enter; raises PlayerQuit on q."""
        ...

    def show_playlist_created(self, playlist: Playlist) -> None: ...

    def show_playlist_in_use(self, playlist: Playlist) -> None: ...

    def show_playlist_gone(self) -> None: ...

    def show_songs_searched(self, done: int, total: int) -> None: ...

    def show_match_summary(
        self, certain: int, doubtful: int, unmatched: int
    ) -> None: ...

    def show_tracks_added(self, added: int, already: int, playlist: Playlist) -> None:
        """already counts the distinct Tracks that were in the Playlist before."""
        ...


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

    def create_playlist(self, name: str) -> Playlist:
        """A new private Playlist on the Player's account."""
        ...

    def find_playlist(self, playlist_id: str) -> Playlist | None:
        """The Playlist with this id in the Player's library, with its current name."""
        ...

    def find_tracks(self, artist: str, title: str) -> list[Track]:
        """At most 10 candidate Tracks for one search."""
        ...

    def tracks_in_playlist(self, playlist: Playlist) -> set[str]:
        """The ids of every Track in the Playlist, whoever added it, read from the service."""
        ...

    def append_tracks(self, playlist: Playlist, tracks: list[str]) -> None:
        """Appends the Tracks with these ids at the end of the Playlist, in this order."""
        ...
