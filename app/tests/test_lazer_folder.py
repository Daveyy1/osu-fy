import json
import shutil
from pathlib import Path

import pytest
from scripted_player import ScriptedPlayer

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.lazer_folder import find_lazer_folder
from osu_fy.core.ports import PlayerQuit
from osu_fy.core.settings import SettingsUnreadable


@pytest.fixture
def roaming(tmp_path: Path) -> Path:
    """A stand-in for %APPDATA%."""
    return tmp_path / "Roaming"


def lazer_folder(path: Path) -> Path:
    (path / "files" / "a" / "ab").mkdir(parents=True)
    (path / "files" / "a" / "ab" / "abc123").write_text("osu file format v14\n")
    return path


def run(roaming: Path, player: ScriptedPlayer) -> Path:
    return find_lazer_folder(LazerSource(roaming), player, roaming / "osu-fy")


def remembered(roaming: Path) -> object:
    settings = json.loads((roaming / "osu-fy" / "settings.json").read_text("utf-8"))
    assert isinstance(settings, dict)
    return settings["lazer_folder"]


def test_US_01_1_offers_the_default_folder_and_remembers_it(roaming: Path) -> None:
    default = lazer_folder(roaming / "osu")
    player = ScriptedPlayer(True)

    assert run(roaming, player) == default

    assert player.shown == [
        f"Use this lazer folder? {default}",
        f"Reading lazer folder {default}",
    ]
    assert remembered(roaming) == str(default)


def test_US_01_2_offers_the_folder_storage_ini_names(
    roaming: Path, tmp_path: Path
) -> None:
    lazer_folder(roaming / "osu")
    elsewhere = lazer_folder(tmp_path / "osu-data")
    (roaming / "osu" / "storage.ini").write_text(
        f"FullPath = {elsewhere}\n", encoding="utf-8"
    )
    player = ScriptedPlayer(True)

    assert run(roaming, player) == elsewhere
    assert player.shown[0] == f"Use this lazer folder? {elsewhere}"


def test_US_01_3_asks_for_a_path_when_nothing_is_found(
    roaming: Path, tmp_path: Path
) -> None:
    typed = lazer_folder(tmp_path / "Jürgen's osu")
    player = ScriptedPlayer(str(typed))

    assert run(roaming, player) == typed
    assert player.shown == [
        "Path to the lazer folder?",
        f"Reading lazer folder {typed}",
    ]
    assert remembered(roaming) == str(typed)


def test_US_01_3_asks_for_a_path_when_the_player_says_n(
    roaming: Path, tmp_path: Path
) -> None:
    lazer_folder(roaming / "osu")
    typed = lazer_folder(tmp_path / "other")
    player = ScriptedPlayer(False, str(typed))

    assert run(roaming, player) == typed
    assert remembered(roaming) == str(typed)


def test_US_01_3_says_no_lazer_data_found_and_asks_again(
    roaming: Path, tmp_path: Path
) -> None:
    wrong = tmp_path / "wrong"
    wrong.mkdir()
    right = lazer_folder(tmp_path / "right")
    player = ScriptedPlayer(str(wrong), str(right))

    assert run(roaming, player) == right
    assert player.shown == [
        "Path to the lazer folder?",
        f"No lazer data found in {wrong}",
        "Path to the lazer folder?",
        f"Reading lazer folder {right}",
    ]


def test_US_01_3_q_quits(roaming: Path) -> None:
    player = ScriptedPlayer("q")

    with pytest.raises(PlayerQuit):
        run(roaming, player)

    assert not (roaming / "osu-fy" / "settings.json").exists()


def test_US_01_4_uses_the_remembered_folder_without_asking(roaming: Path) -> None:
    default = lazer_folder(roaming / "osu")
    run(roaming, ScriptedPlayer(True))
    later = ScriptedPlayer()  # answers nothing: any question fails the test

    assert run(roaming, later) == default
    assert later.shown == [f"Reading lazer folder {default}"]


@pytest.mark.parametrize("content", ["{not json", "[]"])
def test_US_01_4_unreadable_settings_stop_with_a_message(
    roaming: Path, content: str
) -> None:
    lazer_folder(roaming / "osu")
    settings = roaming / "osu-fy" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(content, encoding="utf-8")

    with pytest.raises(SettingsUnreadable) as stop:
        run(roaming, ScriptedPlayer())

    assert str(stop.value).startswith(f"Cannot read {settings}: ")
    assert str(stop.value).endswith(". Fix or delete it.")
    assert settings.read_text(encoding="utf-8") == content


def test_US_01_5_remembered_folder_without_files_asks_again(
    roaming: Path, tmp_path: Path
) -> None:
    default = lazer_folder(roaming / "osu")
    gone = lazer_folder(tmp_path / "old")
    run(roaming, ScriptedPlayer(False, str(gone)))
    shutil.rmtree(gone / "files")
    player = ScriptedPlayer(True)

    assert run(roaming, player) == default
    assert player.shown == [
        f"No lazer data found in {gone}",
        f"Use this lazer folder? {default}",
        f"Reading lazer folder {default}",
    ]
    assert remembered(roaming) == str(default)


def listing(folder: Path) -> list[tuple[str, int, int]]:
    return sorted(
        (str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in folder.rglob("*")
    )


def test_N2_the_lazer_folder_is_unchanged(roaming: Path, tmp_path: Path) -> None:
    lazer_folder(roaming / "osu")
    elsewhere = lazer_folder(tmp_path / "osu-data")
    (roaming / "osu" / "storage.ini").write_text(
        f"FullPath = {elsewhere}\n", encoding="utf-8"
    )
    before = listing(roaming / "osu"), listing(elsewhere)

    run(roaming, ScriptedPlayer(True))
    run(roaming, ScriptedPlayer())

    assert (listing(roaming / "osu"), listing(elsewhere)) == before


def test_N3_nothing_is_written_to_the_working_folder(
    roaming: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lazer_folder(roaming / "osu")
    working = tmp_path / "working"
    working.mkdir()
    monkeypatch.chdir(working)

    run(roaming, ScriptedPlayer(True))

    assert list(working.iterdir()) == []
    assert [p.name for p in (roaming / "osu-fy").iterdir()] == ["settings.json"]
