"""Records Spotify's answers for the sample Songs, and the quality set, into tests/recordings/.

Run from the repository root:
  uv run --directory app python tests/record_searches.py [EXPORT_FOLDER]

It uses your osu-fy login, Client ID and lazer folder in %APPDATA%\\osu-fy, makes
the searches a Session makes, and keeps only the Track fields of the port. With
EXPORT_FOLDER (the old tool's CSV exports plus confirmed.csv), it also writes the
quality set: the Beatmapsets of those CSVs that are still installed (US-05.12).
Git ignores tests/recordings/: Spotify's terms do not allow committing it (Q1 of #9).
"""

import csv
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from rich.console import Console

from osu_fy.adapters.lazer import LazerSource
from osu_fy.adapters.spotify import Spotify
from osu_fy.core.matching import match_songs
from osu_fy.core.ports import Track
from osu_fy.core.settings import load_settings
from osu_fy.core.songs import Beatmapset, read_songs
from osu_fy.core.spotify_login import connect_to_spotify
from osu_fy.ui.terminal import TerminalPlayer

HERE = Path(__file__).parent
RECORDINGS = HERE / "recordings" / "searches.json"
QUALITY_SET = HERE / "recordings" / "quality_set.json"
EXPORTS = {  # file in EXPORT_FOLDER: kind of quality-set entry
    "local_lazer_songs_spotify_matches.csv": "old match",
    "confirmed.csv": "confirmed",
    "local_lazer_songs_spotify_unmatched.csv": "old unmatched",
}


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


def quality_set(export: Path, library: list[Beatmapset]) -> list[dict[str, object]]:
    """One entry per CSV row whose Beatmapset is installed: both scripts and the Track."""
    installed = {b.online_id: b for b in library if b.online_id is not None}
    entries: list[dict[str, object]] = []
    for name, kind in EXPORTS.items():
        with open(export / name, encoding="utf-8") as rows:
            for row in csv.DictReader(rows):
                url = row["osu_beatmapset_url"]
                beatmapset = installed.get(int(url.rsplit("/", 1)[1])) if url else None
                if beatmapset is None:
                    continue  # deleted since the old run, or no Beatmapset id
                entry = asdict(beatmapset) | {"kind": kind}
                if kind != "old unmatched":
                    entry |= {
                        "track_id": row["spotify_uri"].rsplit(":", 1)[1],
                        "track_title": row["spotify_title"],
                        "track_artists": row["spotify_artist"].split(", "),
                    }
                entries.append(entry)
    return entries


def main() -> None:
    app_data = Path(os.environ["APPDATA"]) / "osu-fy"
    player = TerminalPlayer(Console())
    spotify = RecordingSpotify(app_data)
    source = LazerSource(app_data.parent)
    songs = read_songs(source, player, HERE / "sample-lazer")
    if len(sys.argv) > 1:
        folder = Path(load_settings(app_data)["lazer_folder"])
        library = read_songs(source, player, folder)
        entries = quality_set(
            Path(sys.argv[1]), [b for s in library for b in s.beatmapsets]
        )
        ids = {entry["online_id"] for entry in entries}
        songs += [s for s in library if any(b.online_id in ids for b in s.beatmapsets)]
        QUALITY_SET.parent.mkdir(exist_ok=True)
        QUALITY_SET.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Quality set: {len(entries)} entries in {QUALITY_SET}")
    connect_to_spotify(spotify, player, app_data)
    match_songs(list({s.key: s for s in songs}.values()), spotify, player)
    RECORDINGS.parent.mkdir(exist_ok=True)
    RECORDINGS.write_text(
        json.dumps(spotify.answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Recorded {len(spotify.answers)} searches in {RECORDINGS}")


if __name__ == "__main__":
    main()
