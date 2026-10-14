from pathlib import Path

from osu_fy.adapters.lazer import LazerSource


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
