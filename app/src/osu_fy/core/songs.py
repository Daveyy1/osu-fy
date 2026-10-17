"""Beatmapsets and the Songs they make (US-02)."""

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # ports.py imports Beatmapset from here
    from osu_fy.core.ports import Player, Source


@dataclass(frozen=True)
class Beatmapset:
    online_id: int | None
    artist: str
    artist_original: str
    title: str
    title_original: str


@dataclass(frozen=True)
class Song:
    key: tuple[str, str]
    beatmapsets: tuple[Beatmapset, ...]


def normal(text: str) -> str:
    """Case, full width and extra spaces ignored (US-02.3)."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


CUT_MARKERS = tuple(
    normal(marker)
    for marker in (
        "(TV Size)",
        "(TV Size Ver.)",
        "(Cut Ver.)",
        "(Short Ver.)",
        "～TVサイズ～",
        "~TV Size~",
    )
)


def normal_title(text: str) -> str:
    """A title as compared: normal, cut markers removed (US-02.3)."""
    title = normal(text)
    for marker in CUT_MARKERS:
        title = title.replace(marker, " ")
    return normal(title)


def song_key(beatmapset: Beatmapset) -> tuple[str, str]:
    """Artist and title as compared: romanised first (Q1 of #6), cut markers removed."""
    return (
        normal(beatmapset.artist or beatmapset.artist_original),
        normal_title(beatmapset.title or beatmapset.title_original),
    )


def read_songs(source: "Source", player: "Player", folder: Path) -> list[Song]:
    """The Session step that turns the lazer folder's Beatmapsets into Songs (US-02)."""
    beatmapsets = source.read_beatmapsets(folder, player.show_files_read)
    songs: dict[tuple[str, str], list[Beatmapset]] = {}
    for beatmapset in beatmapsets:
        songs.setdefault(song_key(beatmapset), []).append(beatmapset)
    player.show_songs_found(len(songs), len(beatmapsets))
    return [Song(key, tuple(sets)) for key, sets in songs.items()]
