import json
from pathlib import Path

import pytest
from fake_streaming import FakeStreaming
from scripted_player import ScriptedPlayer

from osu_fy.core.playlist import ensure_playlist
from osu_fy.core.ports import PlayerQuit, Playlist

NAME_QUESTION = "Name for your Playlist [osu!fy]:"
ENTER = None  # what the scripted Player answers for Enter at the name question


def settings(app_data: Path) -> dict[str, object]:
    loaded = json.loads((app_data / "settings.json").read_text("utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def save(app_data: Path, **values: str) -> None:
    app_data.mkdir(parents=True, exist_ok=True)
    (app_data / "settings.json").write_text(json.dumps(values), encoding="utf-8")


def test_US_04_1_fresh_start_enter_creates_the_playlist_osu_fy(tmp_path: Path) -> None:
    player = ScriptedPlayer(ENTER)
    streaming = FakeStreaming()

    playlist = ensure_playlist(streaming, player, tmp_path)

    assert streaming.created == ["osu!fy"]
    assert playlist == streaming.library[playlist.id]
    assert player.shown == [
        NAME_QUESTION,
        f"Created your Playlist osu!fy {playlist.link}",
    ]
    assert settings(tmp_path)["spotify_playlist_id"] == playlist.id


def test_US_04_1_a_typed_name_is_the_playlist_name(tmp_path: Path) -> None:
    streaming = FakeStreaming()

    playlist = ensure_playlist(streaming, ScriptedPlayer("My osu! Songs"), tmp_path)

    assert streaming.created == ["My osu! Songs"]
    assert playlist.name == "My osu! Songs"


def test_US_04_1_the_id_is_saved_before_anything_else_can_stop_osu_fy(
    tmp_path: Path,
) -> None:
    class QuitsAfterCreating(ScriptedPlayer):
        def show_playlist_created(self, playlist: Playlist) -> None:
            raise PlayerQuit

    streaming = FakeStreaming()

    with pytest.raises(PlayerQuit):
        ensure_playlist(streaming, QuitsAfterCreating(ENTER), tmp_path)

    [created] = streaming.library
    assert settings(tmp_path)["spotify_playlist_id"] == created


def test_US_04_1_saving_the_id_keeps_the_other_settings(tmp_path: Path) -> None:
    save(tmp_path, lazer_folder=r"C:\osu", spotify_client_id="0123456789abcdef" * 2)

    playlist = ensure_playlist(FakeStreaming(), ScriptedPlayer(ENTER), tmp_path)

    assert settings(tmp_path) == {
        "lazer_folder": r"C:\osu",
        "spotify_client_id": "0123456789abcdef" * 2,
        "spotify_playlist_id": playlist.id,
    }


def test_US_04_1_q_at_the_name_question_quits_and_creates_nothing(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming()

    with pytest.raises(PlayerQuit):
        ensure_playlist(streaming, ScriptedPlayer("q"), tmp_path)

    assert streaming.created == []
    assert not (tmp_path / "settings.json").exists()


def test_US_04_2_a_saved_playlist_is_used_by_its_id_even_when_renamed(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming()
    renamed = Playlist("pl-1", "Renamed", "https://open.spotify.com/playlist/pl-1")
    streaming.library = {"pl-1": renamed}
    save(tmp_path, spotify_playlist_id="pl-1")
    player = ScriptedPlayer()  # no answers: any question fails the test

    assert ensure_playlist(streaming, player, tmp_path) == renamed

    assert streaming.created == []
    assert player.shown == [
        "Adding to your Playlist Renamed https://open.spotify.com/playlist/pl-1"
    ]


def test_US_04_3_a_playlist_called_osu_fy_that_osu_fy_did_not_create_is_left_alone(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming()
    own = Playlist("players-own", "osu!fy", "https://open.spotify.com/playlist/x")
    streaming.library = {"players-own": own}

    playlist = ensure_playlist(streaming, ScriptedPlayer(ENTER), tmp_path)

    assert playlist.id != "players-own"
    assert streaming.created == ["osu!fy"]
    assert streaming.library["players-own"] == own
    assert settings(tmp_path)["spotify_playlist_id"] == playlist.id


def test_US_04_4_a_playlist_gone_from_the_library_is_replaced_by_a_new_one(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming()  # pl-gone is in no library: deleted in Spotify
    save(tmp_path, spotify_playlist_id="pl-gone")
    player = ScriptedPlayer("osu! again")

    playlist = ensure_playlist(streaming, player, tmp_path)

    assert streaming.created == ["osu! again"]
    assert player.shown == [
        "Your Playlist is no longer in your Spotify library.",
        NAME_QUESTION,
        f"Created your Playlist osu! again {playlist.link}",
    ]
    assert settings(tmp_path)["spotify_playlist_id"] == playlist.id
