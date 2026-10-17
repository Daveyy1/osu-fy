from fake_streaming import FakeStreaming
from scripted_player import ScriptedPlayer

from osu_fy.core.matching import match_songs
from osu_fy.core.ports import Track
from osu_fy.core.songs import Beatmapset, Song, song_key

KERO = Beatmapset(
    1670776, "Silver Forest", "Silver Forest", "Kero (9) destiny", "ケロ⑨destiny"
)


def song(*beatmapsets: Beatmapset) -> Song:
    return Song(song_key(beatmapsets[0]), beatmapsets)


def track(title: str, *artists: str) -> Track:
    """A hand-written Track: names from the osu! metadata, a made-up id (Q1 of #9)."""
    return Track(f"made-up-{title}", title, artists, "Album", 200_000)


def test_US_05_3_exact_artist_and_title_is_a_certain_match() -> None:
    kero = track("ケロ⑨destiny", "Silver Forest")
    streaming = FakeStreaming()
    streaming.searches = {
        ("Silver Forest", "Kero (9) destiny"): [],
        ("Silver Forest", "ケロ⑨destiny"): [kero],
    }

    matches, unmatched = match_songs([song(KERO)], streaming, ScriptedPlayer())

    assert [(m.track, m.certain) for m in matches] == [(kero, True)]
    assert unmatched == []


WALK = Beatmapset(914242, "Kano", "鹿乃", "Walk This Way!", "Walk This Way!")
JUMP = Beatmapset(
    825086, "Various Artist", "Various Artist", "Jump Training #1", "Jump Training #1"
)


def test_US_05_3_case_full_width_and_spaces_do_not_matter() -> None:
    walk = track("ＷＡＬＫ  this way!", "kano")
    streaming = FakeStreaming()
    streaming.searches = {("Kano", "Walk This Way!"): [walk]}

    matches, _ = match_songs([song(WALK)], streaming, ScriptedPlayer())

    assert [(m.track, m.certain) for m in matches] == [(walk, True)]


def test_US_05_3_the_first_certain_match_ends_the_search() -> None:
    walk = track("Walk This Way!", "鹿乃")
    streaming = FakeStreaming()
    streaming.searches = {("Kano", "Walk This Way!"): [walk]}

    match_songs([song(WALK)], streaming, ScriptedPlayer())

    assert streaming.searched == [("Kano", "Walk This Way!")]  # not 鹿乃 as well


def test_US_05_7_nothing_found_is_an_unmatched_song() -> None:
    streaming = FakeStreaming()
    streaming.searches = {("Various Artist", "Jump Training #1"): []}

    matches, unmatched = match_songs([song(JUMP)], streaming, ScriptedPlayer())

    assert matches == []
    assert unmatched == [song(JUMP)]


def test_US_05_7_another_artist_or_another_title_is_never_certain() -> None:
    streaming = FakeStreaming()
    streaming.searches = {
        ("Kano", "Walk This Way!"): [
            track("Walk This Way!", "Aerosmith"),  # a cover, US-05.6 in #10
            track("Walk This Way! - Extended Mix", "Kano"),  # Doubtful in #10
        ],
        ("鹿乃", "Walk This Way!"): [],
    }

    matches, unmatched = match_songs([song(WALK)], streaming, ScriptedPlayer())

    assert matches == []
    assert unmatched == [song(WALK)]


def test_US_05_8_progress_counts_the_songs_searched() -> None:
    streaming = FakeStreaming()
    streaming.searches = {
        ("Kano", "Walk This Way!"): [track("Walk This Way!", "Kano")],
        ("Various Artist", "Jump Training #1"): [],
    }
    player = ScriptedPlayer()

    match_songs([song(WALK), song(JUMP)], streaming, player)

    assert player.songs_searched == [(1, 2), (2, 2)]


def test_US_05_10_the_summary_counts_certain_doubtful_and_unmatched() -> None:
    streaming = FakeStreaming()
    streaming.searches = {
        ("Kano", "Walk This Way!"): [track("Walk This Way!", "Kano")],
        ("Silver Forest", "Kero (9) destiny"): [],
        ("Silver Forest", "ケロ⑨destiny"): [track("ケロ⑨destiny", "Silver Forest")],
        ("Various Artist", "Jump Training #1"): [],
    }
    player = ScriptedPlayer()

    match_songs([song(WALK), song(KERO), song(JUMP)], streaming, player)

    assert player.shown == ["2 Certain matches, 0 Doubtful matches, 1 Unmatched Songs"]
