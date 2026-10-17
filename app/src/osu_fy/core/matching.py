"""Matching Songs to Tracks (US-05): the rules of the feature spec, "Matching rules"."""

import re
from collections.abc import Iterator
from dataclasses import dataclass

from rapidfuzz.fuzz import ratio, token_sort_ratio

from osu_fy.core.ports import Player, StreamingService, Track
from osu_fy.core.songs import CUT_MARKER, Song, normal, normal_title

# the lowest score of artist and title for a Doubtful match: the highest value that
# keeps every quality-set Song at least Doubtful, measured 2026-10-17 (Q9 of #10)
DOUBTFUL = 80
# ` x ` only with spaces around it, so a name like "Xion" is never split (Q6 of #10)
CREDIT = re.compile(r" (?:feat\.?|ft\.?|&|x|\+) |, ", re.IGNORECASE)
FEAT = re.compile(
    r" ?(?:[(\[（] ?(?:feat\.?|ft\.?) [^)\]）]*[)\]）]| (?:feat\.?|ft\.) .*$)",
    re.IGNORECASE,
)
SAME_RECORDING = re.compile(
    r" - (?:(?:\d{4} )?remaster(?:ed)?(?: \d{4})?|original mix)$"
)
NOT_A_SONG = re.compile(r"instrumental|\binst\b|off vocal|karaoke|カラオケ")
VERSION = re.compile(r"(?: ?\([^)]*\))+$")  # every trailing version marker


@dataclass(frozen=True)
class Match:
    song: Song
    track: Track
    certain: bool


def match_songs(
    songs: list[Song], streaming: StreamingService, player: Player
) -> tuple[list[Match], list[Song]]:
    """The Session step that searches Spotify for every Song: the Matches and the Unmatched Songs."""
    matches: list[Match] = []
    unmatched: list[Song] = []
    for done, song in enumerate(songs, start=1):
        match = _best_match(song, streaming)
        if match is None:
            unmatched.append(song)
        else:
            matches.append(match)
        player.show_songs_searched(done, len(songs))
    certain = sum(match.certain for match in matches)
    player.show_match_summary(certain, len(matches) - certain, len(unmatched))
    return matches, unmatched


def _best_match(song: Song, streaming: StreamingService) -> Match | None:
    """The first Certain match, else the Doubtful one with the highest score."""
    best: tuple[float, Track] | None = None
    for artist, title in _searches(song):
        for track in streaming.find_tracks(artist, title):
            score = _score(song, track)
            if score is True:
                return Match(song, track, certain=True)
            if score and (best is None or score > best[0]):
                best = (score, track)
    return None if best is None else Match(song, best[1], certain=False)


def _searches(song: Song) -> Iterator[tuple[str, str]]:
    """Romanised, original script, then the base title of a remix or Nightcore Song."""
    first = song.beatmapsets[0]
    romanised = _query(
        first.artist or first.artist_original, first.title or first.title_original
    )
    original = _query(
        first.artist_original or first.artist, first.title_original or first.title
    )
    searches = [romanised, original]
    if (base := VERSION.sub("", romanised[1])) != romanised[1]:
        searches.append((romanised[0], base))
    yield from dict.fromkeys(searches)  # an ordered set: never the same search twice


def _query(artist: str, title: str) -> tuple[str, str]:
    """Cut markers and feat. credits left out, so Spotify's filters find the Track (#10)."""
    title = " ".join(FEAT.sub(" ", CUT_MARKER.sub(" ", title)).split())
    return " ".join(FEAT.sub(" ", artist).split()), title


def _score(song: Song, track: Track) -> bool | float:
    """True for a Certain match, a score for a Doubtful one, False for neither."""
    titles = {_title(t) for b in song.beatmapsets for t in (b.title, b.title_original)}
    titles -= {""}
    track_title = _title(track.title, track_side=True)
    if NOT_A_SONG.search(track_title) and not any(NOT_A_SONG.search(t) for t in titles):
        return False  # never offer an instrumental or karaoke version (Q8 of #10)
    names = {
        n
        for b in song.beatmapsets
        for a in (b.artist, b.artist_original)
        for n in _names(a)
    }
    artists = {normal(artist) for artist in track.artists} - {""}
    same_artist = not names.isdisjoint(artists)
    if same_artist and track_title in titles:
        return True
    if same_artist and _base(track_title) in {_base(t) for t in titles}:
        # another version, or the original of a remix (US-05.4, US-05.5); a tie goes to
        # the plain title, then to no extra artists: Poison, not Poison - Radio Edit
        return 100.0 - (track_title != _base(track_title)) - (not artists <= names) / 2
    if not names or not artists or not titles:
        return False
    # token_sort for names in either order (Suzuki Konomi), ratio for PornoGraffitti
    artist_score = max(
        max(ratio(n, a), token_sort_ratio(n, a)) for n in names for a in artists
    )
    bases = titles | {_base(t) for t in titles}
    title_score = max(
        ratio(t, x) for t in bases for x in (track_title, _base(track_title))
    )
    score = min(artist_score, title_score)
    return score if score >= DOUBTFUL else False


def _names(artist: str) -> set[str]:
    """The whole artist and its first credit: `Meg & Dia` is one band, `Razihel & …` is not."""
    return {normal(FEAT.sub(" ", artist)), CREDIT.split(normal(artist))[0]} - {""}


def _title(text: str, track_side: bool = False) -> str:
    """A title as compared: cut markers and credits out, `- X Mix` read as `(X Mix)`."""
    title = normal_title(FEAT.sub(" ", normal(text)))
    if track_side:
        title = SAME_RECORDING.sub("", title)
    return normal(re.sub(r" - (.+)$", r" (\1)", title))


def _base(title: str) -> str:
    return VERSION.sub("", title)
