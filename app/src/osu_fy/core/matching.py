"""Matching Songs to Tracks (US-05): the first, simple rule; #10 adds the rest."""

from dataclasses import dataclass

from osu_fy.core.ports import Player, StreamingService, Track
from osu_fy.core.songs import Song, normal, normal_title


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
        track = _certain_track(song, streaming)
        if track is None:
            unmatched.append(song)
        else:
            matches.append(Match(song, track, certain=True))
        player.show_songs_searched(done, len(songs))
    certain = sum(match.certain for match in matches)
    player.show_match_summary(certain, len(matches) - certain, len(unmatched))
    return matches, unmatched


def _certain_track(song: Song, streaming: StreamingService) -> Track | None:
    """Romanised first, then the original script if it differs (Q2 of #9)."""
    first = song.beatmapsets[0]
    searches = dict.fromkeys(  # an ordered set: no second search for the same names
        [
            (
                first.artist or first.artist_original,
                first.title or first.title_original,
            ),
            (
                first.artist_original or first.artist,
                first.title_original or first.title,
            ),
        ]
    )
    for artist, title in searches:
        for track in streaming.find_tracks(artist, title):
            if _is_certain(song, track):
                return track
    return None


def _is_certain(song: Song, track: Track) -> bool:
    """One of the Track's artists and its title equal the Song's, in either script (Q3 of #9)."""
    artists = {normal(b.artist) for b in song.beatmapsets}
    artists |= {normal(b.artist_original) for b in song.beatmapsets}
    titles = {normal_title(b.title) for b in song.beatmapsets}
    titles |= {normal_title(b.title_original) for b in song.beatmapsets}
    return normal(track.title) in titles - {""} and not artists.isdisjoint(
        {normal(artist) for artist in track.artists} - {""}
    )
