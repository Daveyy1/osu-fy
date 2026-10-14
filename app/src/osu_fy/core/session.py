from pathlib import Path

from osu_fy.core.lazer_folder import find_lazer_folder
from osu_fy.core.ports import Player, Source
from osu_fy.core.songs import read_songs


def run_session(player: Player, source: Source, app_data: Path) -> None:
    """One Session, from starting osu-fy to quitting."""
    player.greet()
    read_songs(source, player, find_lazer_folder(source, player, app_data))
    player.wait_for_quit()  # until US-03 connects to Spotify
