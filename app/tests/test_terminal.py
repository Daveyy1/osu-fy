from collections.abc import Iterator
from pathlib import Path

import pytest
import readchar
from rich.console import Console

from osu_fy.core.ports import PlayerQuit
from osu_fy.ui.terminal import TerminalPlayer


def press(monkeypatch: pytest.MonkeyPatch, *keys: str) -> Iterator[str]:
    remaining = iter(keys)
    monkeypatch.setattr(readchar, "readkey", lambda: next(remaining))
    return remaining


def test_greeting_reaches_the_screen() -> None:
    console = Console(record=True, width=80)

    TerminalPlayer(console).greet()

    assert console.export_text() == (
        "osu-fy — your osu! Songs, on Spotify\nPress q to quit.\n"
    )


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_q_quits_and_other_keys_are_ignored(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    remaining = press(monkeypatch, "x", readchar.key.ENTER, quit_key, "never read")

    TerminalPlayer(Console()).wait_for_quit()

    assert list(remaining) == ["never read"]


@pytest.mark.parametrize(
    ("key", "accepted"),
    [(readchar.key.ENTER, True), ("y", True), ("Y", True), ("n", False), ("N", False)],
)
def test_US_01_1_enter_or_y_accepts_n_declines(
    monkeypatch: pytest.MonkeyPatch, key: str, accepted: bool
) -> None:
    remaining = press(monkeypatch, "x", " ", key, "never read")
    console = Console(record=True, width=80)

    answer = TerminalPlayer(console).confirm_lazer_folder(Path(r"C:\Users\A\osu"))

    assert answer is accepted
    assert list(remaining) == ["never read"]
    assert console.export_text() == (
        "C:\\Users\\A\\osu\nUse this lazer folder? [Y/n] \n"
    )


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_US_01_3_q_quits_the_y_n_prompt(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    press(monkeypatch, quit_key)

    with pytest.raises(PlayerQuit):
        TerminalPlayer(Console()).confirm_lazer_folder(Path("osu"))


def type_line(monkeypatch: pytest.MonkeyPatch, console: Console, line: str) -> None:
    monkeypatch.setattr(console, "input", lambda prompt="": line)


@pytest.mark.parametrize(
    "typed", [r"D:\osu-data", r'"D:\osu-data"', r"  'D:\osu-data'  "]
)
def test_US_01_3_path_prompt_strips_quotes(
    monkeypatch: pytest.MonkeyPatch, typed: str
) -> None:
    console = Console()
    type_line(monkeypatch, console, typed)

    assert TerminalPlayer(console).ask_lazer_folder() == Path(r"D:\osu-data")


def test_US_01_3_a_relative_path_is_made_absolute(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    console = Console()
    type_line(monkeypatch, console, "osu")

    assert TerminalPlayer(console).ask_lazer_folder() == tmp_path / "osu"


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_US_01_3_q_quits_the_path_prompt(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    console = Console()
    type_line(monkeypatch, console, quit_key)

    with pytest.raises(PlayerQuit):
        TerminalPlayer(console).ask_lazer_folder()


def test_US_01_3_and_01_4_messages_show_the_path_as_typed() -> None:
    console = Console(record=True, width=80)
    player = TerminalPlayer(console)

    player.show_no_lazer_data(Path(r"D:\[old] osu"))
    player.show_reading_lazer_folder(Path(r"D:\[bold]osu"))

    assert console.export_text() == (
        "No lazer data found in D:\\[old] osu\nReading lazer folder D:\\[bold]osu\n"
    )


def test_long_paths_are_not_broken_into_lines() -> None:
    console = Console(record=True, width=20)
    path = Path("C:/" + "long-folder-name/" * 3)

    TerminalPlayer(console).show_reading_lazer_folder(path)

    assert console.export_text() == f"Reading lazer folder {path}\n"
