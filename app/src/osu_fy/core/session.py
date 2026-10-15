from pathlib import Path

from osu_fy.core.lazer_folder import find_lazer_folder
from osu_fy.core.ports import Player, Source, StreamingService
from osu_fy.core.songs import read_songs
from osu_fy.core.spotify_login import connect_to_spotify


def run_session(
    player: Player, source: Source, streaming: StreamingService, app_data: Path
) -> None:
    """One Session, from starting osu-fy to quitting."""
    player.greet()
    read_songs(source, player, find_lazer_folder(source, player, app_data))
    connect_to_spotify(streaming, player, app_data)
    player.wait_for_quit()  # until US-04 creates the Playlist
