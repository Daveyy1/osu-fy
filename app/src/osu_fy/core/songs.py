"""Beatmapsets and the Songs they make (US-02)."""

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Beatmapset:
    online_id: int | None
    artist: str
    artist_original: str
    title: str
    title_original: str


def _normal(text: str) -> str:
    """Case, full width and extra spaces ignored (US-02.3)."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


CUT_MARKERS = tuple(
    _normal(marker)
    for marker in (
        "(TV Size)",
        "(TV Size Ver.)",
        "(Cut Ver.)",
        "(Short Ver.)",
        "～TVサイズ～",
        "~TV Size~",
    )
)


def song_key(beatmapset: Beatmapset) -> tuple[str, str]:
    """Artist and title as compared: romanised first (Q1 of #6), cut markers removed."""
    title = _normal(beatmapset.title or beatmapset.title_original)
    for marker in CUT_MARKERS:
        title = title.replace(marker, " ")
    return _normal(beatmapset.artist or beatmapset.artist_original), _normal(title)
