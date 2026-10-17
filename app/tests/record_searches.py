"""Records Spotify's answers for the sample Songs into tests/recordings/ (git-ignored).

Run from the repository root: `uv run --directory app python tests/record_searches.py`.
It uses your osu-fy login and Client ID in %APPDATA%\\osu-fy, makes the same
searches a Session makes, and keeps only the Track fields of the port. Spotify's
terms do not allow committing the result (Q1 of #9).
"""

import json
import os
from dataclasses import asdict
from pathlib import Path

from rich.console import Console

from osu_fy.adapters.lazer import LazerSource
from osu_fy.adapters.spotify import Spotify
from osu_fy.core.matching import match_songs
from osu_fy.core.ports import Track
from osu_fy.core.songs import read_songs
from osu_fy.core.spotify_login import connect_to_spotify
from osu_fy.ui.terminal import TerminalPlayer

HERE = Path(__file__).parent
RECORDINGS = HERE / "recordings" / "searches.json"


class RecordingSpotify(Spotify):
    def __init__(self, app_data: Path) -> None:
        super().__init__(app_data)
        self.answers: list[dict[str, object]] = []

    def find_tracks(self, artist: str, title: str) -> list[Track]:
        tracks = super().find_tracks(artist, title)
        self.answers.append(
            {"artist": artist, "title": title, "tracks": [asdict(t) for t in tracks]}
        )
        return tracks


def main() -> None:
    app_data = Path(os.environ["APPDATA"]) / "osu-fy"
    player = TerminalPlayer(Console())
    spotify = RecordingSpotify(app_data)
    songs = read_songs(LazerSource(app_data), player, HERE / "sample-lazer")
    connect_to_spotify(spotify, player, app_data)
    match_songs(songs, spotify, player)
    RECORDINGS.parent.mkdir(exist_ok=True)
    RECORDINGS.write_text(
        json.dumps(spotify.answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Recorded {len(spotify.answers)} searches in {RECORDINGS}")


if __name__ == "__main__":
    main()
