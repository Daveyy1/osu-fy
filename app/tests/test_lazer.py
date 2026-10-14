from pathlib import Path

from osu_fy.adapters.lazer import LazerSource
from osu_fy.core.songs import Beatmapset


def lazer_folder(path: Path) -> Path:
    (path / "files").mkdir(parents=True)
    return path


def test_US_01_1_finds_the_default_folder(tmp_path: Path) -> None:
    default = lazer_folder(tmp_path / "osu")

    assert LazerSource(tmp_path).find_lazer_folder() == default


def test_US_01_3_finds_nothing_without_a_default_folder(tmp_path: Path) -> None:
    (tmp_path / "osu").mkdir()  # lazer installed, but no files yet

    assert LazerSource(tmp_path).find_lazer_folder() is None


def test_US_01_2_storage_ini_lines_are_read_like_lazer_does(tmp_path: Path) -> None:
    lazer_folder(tmp_path / "osu")
    elsewhere = lazer_folder(tmp_path / "a=b ünïcode")
    (tmp_path / "osu" / "storage.ini").write_text(
        f"﻿# a comment\n\nno equals sign\nFullPath={elsewhere}  \n",
        encoding="utf-8",
    )

    assert LazerSource(tmp_path).find_lazer_folder() == elsewhere


def test_US_01_2_falls_back_to_the_default_when_full_path_is_empty_or_has_no_files(
    tmp_path: Path,
) -> None:
    default = lazer_folder(tmp_path / "osu")
    ini = tmp_path / "osu" / "storage.ini"
    source = LazerSource(tmp_path)

    ini.write_text("FullPath = \n", encoding="utf-8")
    assert source.find_lazer_folder() == default

    (tmp_path / "empty").mkdir()
    ini.write_text(f"FullPath = {tmp_path / 'empty'}\n", encoding="utf-8")
    assert source.find_lazer_folder() == default


def test_full_path_key_is_case_sensitive_like_lazer(tmp_path: Path) -> None:
    default = lazer_folder(tmp_path / "osu")
    lazer_folder(tmp_path / "elsewhere")
    (tmp_path / "osu" / "storage.ini").write_text(
        f"fullpath = {tmp_path / 'elsewhere'}\n", encoding="utf-8"
    )

    assert LazerSource(tmp_path).find_lazer_folder() == default


def test_is_lazer_folder_means_it_has_files(tmp_path: Path) -> None:
    source = LazerSource(tmp_path)

    assert source.is_lazer_folder(lazer_folder(tmp_path / "x"))
    assert not source.is_lazer_folder(tmp_path)
    assert not source.is_lazer_folder(tmp_path / "missing")


SAMPLE = Path(__file__).parent / "sample-lazer"


def osu_file(folder: Path, name: str, metadata: str, prefix: bytes = b"") -> None:
    path = folder / "files" / name[0] / name[:2] / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"osu file format v14\r\n\r\n[General]\r\nMode: 0\r\n\r\n[Metadata]\r\n{metadata}"
    path.write_bytes(prefix + text.encode() + b"\r\n[Difficulty]\r\nTitle:not this\r\n")


def read(folder: Path) -> list[Beatmapset]:
    return LazerSource(folder).read_beatmapsets(folder, lambda done, total: None)


def test_US_02_2_difficulties_of_one_beatmapset_count_once() -> None:
    walk_this_way = [b for b in read(SAMPLE) if b.online_id == 914242]

    assert walk_this_way == [
        Beatmapset(914242, "Kano", "鹿乃", "Walk This Way!", "Walk This Way!")
    ]


def test_US_02_2_difficulties_without_a_set_id(tmp_path: Path) -> None:
    for name, set_id in [("a1", ""), ("a2", "BeatmapSetID:-1\n"), ("a3", "")]:
        osu_file(tmp_path, name, f"Artist:A\nTitle:T\n{set_id}")
    osu_file(tmp_path, "b1", "Artist:A\nTitle:T\nTitleUnicode:other\n")

    assert sorted(read(tmp_path), key=lambda b: b.title_original) == [
        Beatmapset(None, "A", "", "T", ""),
        Beatmapset(None, "A", "", "T", "other"),
    ]


def test_US_02_4_skips_files_that_are_not_osu_files(tmp_path: Path) -> None:
    others = {
        "c1": b"ID3\x04\x00 an mp3",
        "c2": b"\x89PNG\r\n\x1a\n",
        "c3": b"[General]\r\nName: a skin\r\n",
        "c4": b"",
        "c5": b"\xff\xfe" + "osu file format v14".encode("utf-16-le"),
    }
    for name, content in others.items():
        (tmp_path / "files" / "c" / name).mkdir(parents=True)
        (tmp_path / "files" / "c" / name / name).write_bytes(content)
    osu_file(tmp_path, "d1", "Title:no artist\n")
    osu_file(tmp_path, "d2", "Artist:no title\n")
    osu_file(tmp_path, "e1", "Artist:A\nTitle:T\nBeatmapSetID:7\n", prefix=b"\xef\xbb\xbf")

    assert read(tmp_path) == [Beatmapset(7, "A", "", "T", "")]


def test_a_beatmapset_id_that_is_not_a_number_is_no_id(tmp_path: Path) -> None:
    osu_file(tmp_path, "f1", "Artist:A\nTitle:T\nBeatmapSetID:²\n")

    assert read(tmp_path) == [Beatmapset(None, "A", "", "T", "")]
