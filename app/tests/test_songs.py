import shutil
from pathlib import Path

import pytest
from scripted_player import ScriptedPlayer

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.songs import Beatmapset, read_songs, song_key

SAMPLE = Path(__file__).parent / "sample-lazer"


@pytest.fixture
def sample(tmp_path: Path) -> Path:
    """A copy of the sample lazer folder, so a failing N2 test harms no other test."""
    return shutil.copytree(SAMPLE, tmp_path / "sample-lazer")


def read(folder: Path, player: ScriptedPlayer) -> list[list[Beatmapset]]:
    songs = read_songs(LazerSource(folder.parent), player, folder)
    return [list(song.beatmapsets) for song in songs]


def test_US_02_1_sample_folder_has_8_songs_in_9_beatmapsets(sample: Path) -> None:
    player = ScriptedPlayer()

    songs = read(sample, player)

    assert player.shown == ["Found 8 Songs in 9 Beatmapsets"]
    walk_this_way = [s for s in songs if s[0].title.startswith("Walk This Way!")]
    assert sorted(b.online_id or 0 for b in walk_this_way[0]) == [914242, 1127002]


def test_US_02_1_an_empty_lazer_folder_has_no_songs(tmp_path: Path) -> None:
    (tmp_path / "files").mkdir()
    player = ScriptedPlayer()

    assert read(tmp_path, player) == []
    assert player.shown == ["Found 0 Songs in 0 Beatmapsets"]


def test_US_02_5_progress_counts_every_file_read(sample: Path) -> None:
    player = ScriptedPlayer()

    read(sample, player)

    assert player.files_read == [(done, 10) for done in range(1, 11)]


def listing(folder: Path) -> list[tuple[str, int, int]]:
    return sorted(
        (str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in folder.rglob("*")
    )


def test_US_02_6_the_sample_folder_is_unchanged(sample: Path) -> None:
    before = listing(sample)

    read(sample, ScriptedPlayer())

    assert listing(sample) == before


def beatmapset(artist: str, title: str, artist_original: str = "") -> Beatmapset:
    return Beatmapset(None, artist, artist_original, title, "")


@pytest.mark.parametrize(
    "title",
    [
        "Hana ni Natte (TV Size)",
        "Hana ni Natte (TV Size Ver.)",
        "Hana ni Natte (TV size ver.)",
        "Hana ni Natte (Cut Ver.)",
        "Hana ni Natte (Short Ver.)",
        "Hana ni Natte ～TVサイズ～",
        "Hana ni Natte  ~TV Size~",
        "Hana ni Natte ～TV Size～",
        "ＨＡＮＡ  ni   natte",
        "hana ni natte",
    ],
)
def test_US_02_3_song_key_ignores_case_width_spaces_and_cut_markers(title: str) -> None:
    original = beatmapset("Ryokuoushoku Shakai", "Hana ni Natte")

    assert song_key(beatmapset(" ｒyokuoushoku  shakai", title)) == song_key(original)


@pytest.mark.parametrize(
    "title",
    [
        "Rockefeller Street (Nightcore Mix)",
        "Rockefeller Street (DotEXE Remix)",
        "Rockefeller Street (Extended Mix)",
    ],
)
def test_US_02_3_version_markers_make_another_song(title: str) -> None:
    original = beatmapset("Getter Jaani", "Rockefeller Street")

    assert song_key(beatmapset("Getter Jaani", title)) != song_key(original)


def test_US_02_3_another_artist_makes_another_song() -> None:
    assert song_key(beatmapset("Kano", "Greetings")) != song_key(
        beatmapset("VINXIS", "Greetings")
    )


def test_US_02_3_the_original_script_counts_only_when_the_romanised_is_empty() -> None:
    romanised = Beatmapset(None, "Kano", "鹿乃", "Walk This Way!", "Walk This Way!")
    other_original = Beatmapset(None, "Kano", "かの", "Walk This Way!", "")
    only_original = Beatmapset(None, "", "鹿乃", "", "Walk This Way!")

    assert song_key(romanised) == song_key(other_original)
    assert song_key(only_original) != song_key(romanised)
    assert song_key(only_original) == song_key(
        Beatmapset(None, "", "鹿乃", "", "WALK this way! (TV Size)")
    )


@pytest.mark.parametrize(
    "title",
    [
        "Hana ni Natte [TV Size]",
        "Hana ni Natte (TV edit)",
        "Hana ni Natte（TV edit.）",
        "Hana ni Natte -TV MIX-",
        "Hana ni Natte -TV SIZE-",
        "Hana ni Natte - TV Size",
        "Hana ni Natte (anime size)",
    ],
)
def test_US_02_3_every_form_of_cut_marker_is_ignored(title: str) -> None:
    original = beatmapset("Ryokuoushoku Shakai", "Hana ni Natte")

    assert song_key(beatmapset("Ryokuoushoku Shakai", title)) == song_key(original)


@pytest.mark.parametrize(
    "title",
    [
        "Zen Zen Zense (movie ver.)",
        "Zen Zen Zense (Game Ver.)",
        "Zen Zen Zense (TV Size & ED Ver.)",
    ],
)
def test_US_02_3_other_recordings_stay_other_songs(title: str) -> None:
    assert song_key(beatmapset("RADWIMPS", title)) != song_key(
        beatmapset("RADWIMPS", "Zen Zen Zense")
    )
