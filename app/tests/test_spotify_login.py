import json
from pathlib import Path

import pytest
from fake_streaming import INCOMPLETE, FakeStreaming
from scripted_player import ScriptedPlayer

from osu_fy.core.ports import PlayerQuit, StreamingService
from osu_fy.core.spotify_login import connect_to_spotify

# made up: the repository ships no Client ID
CLIENT_ID = "0123456789abcdef0123456789abcdef"
OTHER_ID = "fedcba9876543210fedcba9876543210"
WAITING = "Waiting for the login in your browser None"
RETRY = "Try again [t], enter another Client ID [c] or quit [q]"


def settings(app_data: Path) -> dict[str, object]:
    loaded = json.loads((app_data / "settings.json").read_text("utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def save(app_data: Path, **values: str) -> None:
    app_data.mkdir(parents=True, exist_ok=True)
    (app_data / "settings.json").write_text(json.dumps(values), encoding="utf-8")


def test_US_03_1_fresh_start_shows_the_guide_then_asks_for_the_client_id(
    tmp_path: Path,
) -> None:
    player = ScriptedPlayer(CLIENT_ID)

    connect_to_spotify(FakeStreaming("Kanon"), player, tmp_path)

    assert player.shown[:2] == ["Spotify setup guide", "Client ID?"]


@pytest.mark.parametrize(
    "pasted",
    [
        "abc",
        CLIENT_ID[:31],
        CLIENT_ID + "0",
        CLIENT_ID[:31] + "g",
        "https://developer.spotify.com/dashboard",
    ],
)
def test_US_03_2_not_32_hexadecimal_characters_asks_again(
    tmp_path: Path, pasted: str
) -> None:
    player = ScriptedPlayer(pasted, CLIENT_ID)
    streaming = FakeStreaming("Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert player.shown[1:4] == [
        "Client ID?",
        "That does not look like a Client ID",
        "Client ID?",
    ]
    assert streaming.client_ids == [CLIENT_ID]


def test_US_03_2_upper_case_client_id_is_accepted_and_saved_in_lower_case(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming("Kanon")

    connect_to_spotify(streaming, ScriptedPlayer(CLIENT_ID.upper()), tmp_path)

    assert streaming.client_ids == [CLIENT_ID]
    assert settings(tmp_path)["spotify_client_id"] == CLIENT_ID


def test_US_03_2_the_client_id_is_saved_next_to_the_lazer_folder(
    tmp_path: Path,
) -> None:
    save(tmp_path, lazer_folder=r"C:\osu")

    connect_to_spotify(FakeStreaming("Kanon"), ScriptedPlayer(CLIENT_ID), tmp_path)

    assert settings(tmp_path) == {
        "lazer_folder": r"C:\osu",
        "spotify_client_id": CLIENT_ID,
    }


def test_US_03_3_a_valid_client_id_logs_in_and_shows_the_display_name(
    tmp_path: Path,
) -> None:
    player = ScriptedPlayer(CLIENT_ID)
    streaming = FakeStreaming("Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert streaming.client_ids == [CLIENT_ID]
    assert player.shown[-1] == "Logged in to Spotify as Kanon"


def test_US_03_4_a_refused_login_offers_to_try_again(tmp_path: Path) -> None:
    save(tmp_path, spotify_client_id=CLIENT_ID)
    player = ScriptedPlayer(None, "t")  # no key while waiting; then t
    streaming = FakeStreaming(INCOMPLETE, "Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert player.shown == [
        WAITING,
        "The login did not complete.",
        RETRY,
        "Logged in to Spotify as Kanon",
    ]
    assert streaming.client_ids == [CLIENT_ID, CLIENT_ID]


def test_US_03_4_t_pressed_while_waiting_tries_again_without_asking(
    tmp_path: Path,
) -> None:
    save(tmp_path, spotify_client_id=CLIENT_ID)
    player = ScriptedPlayer("t")
    streaming = FakeStreaming(INCOMPLETE, "Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert player.shown == [
        WAITING,
        "The login did not complete.",
        "Logged in to Spotify as Kanon",
    ]
    assert streaming.client_ids == [CLIENT_ID, CLIENT_ID]


@pytest.mark.parametrize(
    "answers", [("c",), (None, "c")], ids=["while waiting", "after"]
)
def test_US_03_4_c_asks_for_another_client_id_and_saves_it(
    tmp_path: Path, answers: tuple[str | None, ...]
) -> None:
    save(tmp_path, spotify_client_id=CLIENT_ID)
    player = ScriptedPlayer(*answers, "abc", OTHER_ID)
    streaming = FakeStreaming(INCOMPLETE, "Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert player.shown[-4:] == [
        "Client ID?",
        "That does not look like a Client ID",
        "Client ID?",
        "Logged in to Spotify as Kanon",
    ]
    assert streaming.client_ids == [CLIENT_ID, OTHER_ID]
    assert settings(tmp_path)["spotify_client_id"] == OTHER_ID


@pytest.mark.parametrize(
    "answers", [("q",), (None, "q")], ids=["while waiting", "after"]
)
def test_US_03_4_q_quits_and_the_client_id_stays_saved(
    tmp_path: Path, answers: tuple[str | None, ...]
) -> None:
    player = ScriptedPlayer(CLIENT_ID, *answers)

    with pytest.raises(PlayerQuit):
        connect_to_spotify(FakeStreaming(INCOMPLETE), player, tmp_path)

    assert settings(tmp_path)["spotify_client_id"] == CLIENT_ID


def test_US_03_5_a_saved_client_id_logs_in_without_the_guide_or_a_question(
    tmp_path: Path,
) -> None:
    save(tmp_path, spotify_client_id=CLIENT_ID)
    player = ScriptedPlayer()
    streaming = FakeStreaming("Kanon")

    connect_to_spotify(streaming, player, tmp_path)

    assert player.shown == ["Logged in to Spotify as Kanon"]
    assert streaming.client_ids == [CLIENT_ID]


def test_N1_the_streaming_service_port_cannot_remove_or_reorder() -> None:
    operations = [name for name in vars(StreamingService) if not name.startswith("_")]

    assert operations  # the check below must not pass on an empty port
    for forbidden in ("remove", "delete", "replace", "reorder", "move", "clear"):
        assert not [name for name in operations if forbidden in name]
