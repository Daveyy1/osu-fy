import json
from pathlib import Path

import pytest
from fake_streaming import FakeStreaming
from scripted_player import ScriptedPlayer

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.matching import match_songs
from osu_fy.core.ports import Track
from osu_fy.core.songs import (
    Beatmapset,
    Song,
    normal,
    normal_title,
    read_songs,
    song_key,
)

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
            track("Walk This Way!", "Aerosmith"),  # a cover (US-05.6)
            track("Walk This Way! - Radio Edit", "Kano"),  # another version: Doubtful
        ],
        ("鹿乃", "Walk This Way!"): [],
    }

    matches, _ = match_songs([song(WALK)], streaming, ScriptedPlayer())

    assert [(m.track.title, m.certain) for m in matches] == [
        ("Walk This Way! - Radio Edit", False)
    ]


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


RECORDINGS = Path(__file__).parent / "recordings" / "searches.json"


@pytest.mark.skipif(
    not RECORDINGS.exists(),
    reason="no local recordings (Q1 of #9): run tests/record_searches.py",
)
def test_US_05_2_to_US_05_7_on_spotifys_recorded_answers_for_the_sample_songs(
    tmp_path: Path,
) -> None:
    streaming = FakeStreaming()
    for answer in json.loads(RECORDINGS.read_text("utf-8")):
        tracks = [
            Track(**(t | {"artists": tuple(t["artists"])})) for t in answer["tracks"]
        ]
        streaming.searches[(answer["artist"], answer["title"])] = tracks
    sample = Path(__file__).parent / "sample-lazer"
    songs = read_songs(LazerSource(tmp_path), ScriptedPlayer(), sample)

    matches, unmatched = match_songs(songs, streaming, ScriptedPlayer())

    certain = {m.song.key for m in matches if m.certain}
    assert ("silver forest", "kero (9) destiny") in certain
    assert ("nightmare", "the world") in certain  # US-05.2
    assert ("vinxis", "greetings") in certain  # US-05.4: only an extended mix
    assert ("various artist", "jump training #1") in {song.key for song in unmatched}
    # the five Song-identity cases on real answers: never a wrong Certain match
    doubtful_at_most = {
        ("getter jaani", "rockefeller street (nightcore mix)"),  # US-05.5
        ("meg & dia", "monster (dotexe remix)"),  # US-05.5
        ("kano", "walk this way!"),  # US-05.6: covers only
    }
    assert certain.isdisjoint(doubtful_at_most)


HANA = Beatmapset(
    2083205,
    "Ryokuoushoku Shakai",
    "緑黄色社会",
    "Hana ni Natte (TV Size)",
    "花になって (TV Size)",
)
WORLD = Beatmapset(
    438535, "NIGHTMARE", "ナイトメア", "the WORLD  ~TV Size~", "the WORLD ～TVサイズ～"
)
GREETINGS = Beatmapset(288974, "VINXIS", "VINXIS", "Greetings", "Greetings")
SILHOUETTE = Beatmapset(399358, "KANA-BOON", "KANA-BOON", "Silhouette", "シルエット")
ROCKEFELLER = Beatmapset(
    942866,
    "Getter Jaani",
    "Getter Jaani",
    "Rockefeller Street (Nightcore Mix)",
    "Rockefeller Street (Nightcore Mix)",
)
MONSTER = Beatmapset(
    157896, "Meg & Dia", "Meg & Dia", "Monster (DotEXE Remix)", "Monster (DotEXE Remix)"
)


def matched(
    beatmapset: Beatmapset, searches: dict[tuple[str, str], list[Track]]
) -> list[tuple[str, bool]]:
    """The Match for one Song as (Track title, certain), or [] when it is Unmatched."""
    streaming = FakeStreaming()
    streaming.searches = searches
    matches, _ = match_songs([song(beatmapset)], streaming, ScriptedPlayer())
    return [(m.track.title, m.certain) for m in matches]


def test_US_05_1_a_cut_marker_does_not_matter_and_stays_out_of_the_search() -> None:
    assert matched(
        HANA,
        {
            ("Ryokuoushoku Shakai", "Hana ni Natte"): [],
            ("緑黄色社会", "花になって"): [track("花になって", "Ryokuoushoku Shakai")],
        },
    ) == [("花になって", True)]


@pytest.mark.parametrize(
    "title",
    ["Hana ni Natte - TV Size", "Hana ni Natte -TV SIZE-", "Hana ni Natte (TV Size)"],
)
def test_US_05_1_spotifys_cut_suffixes_do_not_matter(title: str) -> None:
    searches = {
        ("Ryokuoushoku Shakai", "Hana ni Natte"): [track(title, "Ryokuoushoku Shakai")]
    }

    assert matched(HANA, searches) == [(title, True)]


@pytest.mark.parametrize(
    "title",
    ["Greetings - Remastered", "Greetings - 2011 Remaster", "Greetings - Original Mix"],
)
def test_US_05_1_remaster_and_original_mix_are_the_same_recording(title: str) -> None:
    assert matched(GREETINGS, {("VINXIS", "Greetings"): [track(title, "VINXIS")]}) == [
        (title, True)
    ]


def test_US_05_2_artist_or_title_in_either_script_counts() -> None:
    assert matched(
        WORLD, {("NIGHTMARE", "the WORLD"): [track("the WORLD", "NIGHTMARE")]}
    ) == [("the WORLD", True)]
    assert matched(
        SILHOUETTE, {("KANA-BOON", "Silhouette"): [track("シルエット", "KANA-BOON")]}
    ) == [("シルエット", True)]


def test_US_05_4_an_extended_mix_is_certain() -> None:
    searches = {("VINXIS", "Greetings"): [track("Greetings - Extended Mix", "VINXIS")]}

    assert matched(GREETINGS, searches) == [("Greetings - Extended Mix", True)]


def test_US_05_4_an_extended_mix_song_still_matches_its_own_version() -> None:
    extended = Beatmapset(1, "VINXIS", "VINXIS", "Greetings (Extended Mix)", "")
    exact = track("Greetings - Extended Mix", "VINXIS")
    original = track("Greetings", "VINXIS")

    assert matched(extended, {("VINXIS", "Greetings (Extended Mix)"): [exact]}) == [
        ("Greetings - Extended Mix", True)
    ]
    only_original = {
        ("VINXIS", "Greetings (Extended Mix)"): [],
        ("VINXIS", "Greetings"): [original],
    }
    assert matched(extended, only_original) == [("Greetings", False)]


@pytest.mark.parametrize(
    ("beatmapset", "exact", "base"),
    [
        (ROCKEFELLER, "Rockefeller Street - Nightcore Mix", "Rockefeller Street"),
        (MONSTER, "Monster - DotEXE Remix", "Monster"),
    ],
)
def test_US_05_5_the_exact_version_is_certain(
    beatmapset: Beatmapset, exact: str, base: str
) -> None:
    searches = {
        (beatmapset.artist, beatmapset.title): [track(exact, beatmapset.artist)]
    }

    assert matched(beatmapset, searches) == [(exact, True)]


@pytest.mark.parametrize(
    ("beatmapset", "base"),
    [(ROCKEFELLER, "Rockefeller Street"), (MONSTER, "Monster")],
)
def test_US_05_5_only_the_original_is_doubtful_never_certain(
    beatmapset: Beatmapset, base: str
) -> None:
    searches = {
        (beatmapset.artist, beatmapset.title): [],
        (beatmapset.artist, base): [track(base, beatmapset.artist)],  # the third search
    }

    assert matched(beatmapset, searches) == [(base, False)]


def test_US_05_6_a_cover_by_another_artist_is_never_certain() -> None:
    searches = {
        ("KANA-BOON", "Silhouette"): [track("シルエット", "KANA-BOON Tribute")],
        ("KANA-BOON", "シルエット"): [track("Silhouette", "Silhouette Covers")],
    }

    assert all(not certain for _, certain in matched(SILHOUETTE, searches))


@pytest.mark.parametrize(
    ("beatmapset", "query", "found"),
    [
        (
            Beatmapset(
                None,
                "Razihel & Virtual Riot",
                "Razihel & Virtual Riot",
                "Highscore",
                "Highscore",
            ),
            ("Razihel & Virtual Riot", "Highscore"),
            track("Highscore", "Razihel", "Virtual Riot"),
        ),
        (
            Beatmapset(
                None,
                "Pegboard Nerds",
                "Pegboard Nerds",
                "Gunslinga (feat. MC Mota)",
                "Gunslinga (feat. MC Mota)",
            ),
            ("Pegboard Nerds", "Gunslinga"),
            track("Gunslinga", "Pegboard Nerds", "MC Mota"),
        ),
        (
            Beatmapset(
                None,
                "MIMI feat. Hatsune Miku",
                "MIMI feat. 初音ミク",
                "Ai no Sukima",
                "哀の隙間",
            ),
            ("MIMI", "Ai no Sukima"),
            track("哀の隙間", "MIMI", "初音ミク"),
        ),
        (
            Beatmapset(
                None,
                "Station Earth",
                "Station Earth",
                "Cold Green Eyes ft. Roos Denayer",
                "Cold Green Eyes ft. Roos Denayer",
            ),
            ("Station Earth", "Cold Green Eyes"),
            track("Cold Green Eyes - Original Mix", "Station Earth", "Roos Denayer"),
        ),
    ],
)
def test_credits_split_across_the_tracks_artists_are_certain(
    beatmapset: Beatmapset, query: tuple[str, str], found: Track
) -> None:
    assert matched(beatmapset, {query: [found]}) == [(found.title, True)]


@pytest.mark.parametrize(
    "title",
    [
        "Greetings (Instrumental)",
        "Greetings - inst",
        "Greetings (Off Vocal)",
        "Greetings カラオケ",
    ],
)
def test_instrumental_and_karaoke_tracks_are_never_a_match(title: str) -> None:
    assert matched(GREETINGS, {("VINXIS", "Greetings"): [track(title, "VINXIS")]}) == []


def test_a_close_artist_and_title_is_doubtful_by_score() -> None:
    zense = Beatmapset(
        513590,
        "RADWIMPS",
        "RADWIMPS",
        "Zen Zen Zense (movie ver.)",
        "前前前世 (movie ver.)",
    )
    searches = {
        ("RADWIMPS", "Zen Zen Zense (movie ver.)"): [
            track("Zenzenzense - movie ver.", "RADWIMPS")
        ],
        ("RADWIMPS", "前前前世 (movie ver.)"): [],
        ("RADWIMPS", "Zen Zen Zense"): [],
    }

    assert matched(zense, searches) == [("Zenzenzense - movie ver.", False)]


def test_nothing_close_is_an_unmatched_song() -> None:
    searches = {
        ("VINXIS", "Greetings"): [track("Completely Different", "Someone Else")]
    }

    assert matched(GREETINGS, searches) == []


def test_a_swapped_name_order_is_doubtful() -> None:
    redo = Beatmapset(437055, "Suzuki Konomi", "鈴木このみ", "Redo", "Redo")
    searches = {
        ("Suzuki Konomi", "Redo"): [track("Redo", "Konomi Suzuki")],
        ("鈴木このみ", "Redo"): [],
    }

    assert matched(redo, searches) == [("Redo", False)]


def test_US_05_5_the_base_title_drops_every_version_marker() -> None:
    sorry = Beatmapset(
        2449469,
        "Demi Lovato",
        "Demi Lovato",
        "Sorry Not Sorry (Rock Ver.) (Nightcore & Cut Ver.)",
        "Sorry Not Sorry (Rock Ver.) (Nightcore & Cut Ver.)",
    )
    searches = {
        ("Demi Lovato", sorry.title): [],
        ("Demi Lovato", "Sorry Not Sorry"): [track("Sorry Not Sorry", "Demi Lovato")],
    }

    assert matched(sorry, searches) == [("Sorry Not Sorry", False)]


def test_a_close_artist_with_the_base_title_is_doubtful() -> None:
    backstabber = Beatmapset(
        1217044,
        "Ke$ha",
        "Ke$ha",
        "Backstabber (Sped Up & Cut Ver.)",
        "Backstabber (Sped Up & Cut Ver.)",
    )
    searches = {
        ("Ke$ha", backstabber.title): [],
        ("Ke$ha", "Backstabber"): [track("Backstabber", "Kesha")],
    }

    assert matched(backstabber, searches) == [("Backstabber", False)]


def test_US_05_5_the_original_without_extra_artists_wins_a_tie() -> None:
    poison = Beatmapset(
        2281428,
        "Groove Coverage",
        "Groove Coverage",
        "Poison (Nightcore & Cut Ver.)",
        "Poison (Nightcore & Cut Ver.)",
    )
    searches = {
        ("Groove Coverage", poison.title): [],
        ("Groove Coverage", "Poison"): [
            track("Poison", "AXMO", "Groove Coverage"),
            track("Poison", "Groove Coverage"),
        ],
    }
    streaming = FakeStreaming()
    streaming.searches = searches

    matches, _ = match_songs([song(poison)], streaming, ScriptedPlayer())

    assert [(m.track.artists, m.certain) for m in matches] == [
        (("Groove Coverage",), False)
    ]


def test_a_spelling_variant_of_the_artist_is_doubtful() -> None:
    day = Beatmapset(
        459293, "Porno Graffitti", "ポルノグラフィティ", "THE DAY", "THE DAY"
    )
    searches = {
        ("Porno Graffitti", "THE DAY"): [track("THE DAY", "PornoGraffitti")],
        ("ポルノグラフィティ", "THE DAY"): [],
    }

    assert matched(day, searches) == [("THE DAY", False)]


def test_US_05_5_the_plain_original_wins_over_another_version_of_it() -> None:
    poison = Beatmapset(
        2281428,
        "Groove Coverage",
        "Groove Coverage",
        "Poison (Nightcore & Cut Ver.)",
        "Poison (Nightcore & Cut Ver.)",
    )
    searches = {
        ("Groove Coverage", poison.title): [],
        ("Groove Coverage", "Poison"): [
            track("Poison - Radio Edit", "Groove Coverage"),
            track("Poison", "Groove Coverage"),
        ],
    }

    assert matched(poison, searches) == [("Poison", False)]


QUALITY_SET = Path(__file__).parent / "recordings" / "quality_set.json"
# old matches and confirmed Songs no rule reaches, approved in the pull request (Q10 of #10)
EXCEPTIONS = {
    2077229: "the same recording as the old Track (ISRC JPPO02302806), titled 唱",
    1085435: "the same recording as the old Track (ISRC JPTF01914601), titled レーゾンデートル",
    999645: "the same recording as the old Track (ISRC JPPO01902850), titled インフェルノ",
    513590: "Spotify's filter search never returns Zenzenzense - movie ver. (other romanisation)",
    593620: "Spotify's filter search never returns Shinzo wo Sasageyo ! (other romanisation)",
}


def recorded() -> FakeStreaming:
    streaming = FakeStreaming()
    for answer in json.loads(RECORDINGS.read_text("utf-8")):
        tracks = [
            Track(**(t | {"artists": tuple(t["artists"])})) for t in answer["tracks"]
        ]
        streaming.searches[(answer["artist"], answer["title"])] = tracks
    return streaming


def same_track(track: Track, entry: dict[str, object]) -> bool:
    """The same id, or another release with the same title and artists (Q4 of #10)."""
    artists = entry["track_artists"]
    assert isinstance(artists, list)
    return track.id == entry["track_id"] or (
        normal_title(track.title) == normal_title(str(entry["track_title"]))
        and {normal(a) for a in track.artists} == {normal(str(a)) for a in artists}
    )


@pytest.mark.skipif(
    not QUALITY_SET.exists(),
    reason="no local quality set (Q1 of #9): run tests/record_searches.py <export folder>",
)
def test_US_05_12_the_quality_set() -> None:
    streaming = recorded()
    fields = ("online_id", "artist", "artist_original", "title", "title_original")
    wrong: list[object] = []
    lost: list[object] = []
    unmatched_old: set[tuple[str, str]] = set()
    old: set[tuple[str, str]] = set()
    for entry in json.loads(QUALITY_SET.read_text("utf-8")):
        beatmapset = Beatmapset(*(entry[f] for f in fields))
        matches, _ = match_songs([song(beatmapset)], streaming, ScriptedPlayer())
        match = matches[0] if matches else None
        if entry["kind"] == "old unmatched":
            old.add(song_key(beatmapset))
            if match is None:
                unmatched_old.add(song_key(beatmapset))
        elif entry["online_id"] in EXCEPTIONS:
            continue
        elif match is None or not same_track(match.track, entry):
            (wrong if match and match.certain else lost).append(entry["title"])

    print(
        f"Unmatched among the old Unmatched Songs: {len(unmatched_old)} of {len(old)}"
    )
    assert wrong == []  # no wrong Certain match
    assert lost == []  # every old match and confirmed Song keeps its Track
    assert len(unmatched_old) < len(old)
