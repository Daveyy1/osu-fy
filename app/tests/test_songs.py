import pytest

from osu_fy.core.songs import Beatmapset, song_key


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
