from pathlib import Path

from osu_fy.core.lazer_folder import find_lazer_folder
from osu_fy.core.matching import match_songs
from osu_fy.core.playlist import add_certain_matches, ensure_playlist
from osu_fy.core.ports import Player, Source, StreamingService
from osu_fy.core.songs import read_songs
from osu_fy.core.spotify_login import connect_to_spotify


def run_session(
    player: Player, source: Source, streaming: StreamingService, app_data: Path
) -> None:
    """One Session, from starting osu-fy to quitting."""
    player.greet()
    songs = read_songs(source, player, find_lazer_folder(source, player, app_data))
    connect_to_spotify(streaming, player, app_data)
    playlist = ensure_playlist(streaming, player, app_data)
    matches, _ = match_songs(songs, streaming, player)
    add_certain_matches(matches, streaming, player, playlist)
