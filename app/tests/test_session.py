from pathlib import Path

from scripted_player import ScriptedPlayer

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.session import run_session


def test_session_greets_finds_the_lazer_folder_reads_songs_then_waits_for_quit(
    tmp_path: Path,
) -> None:
    (tmp_path / "osu" / "files").mkdir(parents=True)
    player = ScriptedPlayer(True)

    run_session(player, LazerSource(tmp_path), tmp_path / "osu-fy")

    assert player.shown == [
        "greet",
        f"Use this lazer folder? {tmp_path / 'osu'}",
        f"Reading lazer folder {tmp_path / 'osu'}",
        "Found 0 Songs in 0 Beatmapsets",
        "wait_for_quit",
    ]
