import msvcrt
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


def test_US_02_5_progress_bar_reaches_the_screen() -> None:
    console = Console(record=True, width=80)
    player = TerminalPlayer(console)

    for done in range(1, 1235):
        player.show_files_read(done, 1234)

    screen = console.export_text()
    assert "Reading lazer folder" in screen
    assert screen.rstrip().endswith("1,234/1,234 files")


def test_US_02_1_songs_found_reaches_the_screen() -> None:
    console = Console(record=True, width=80)

    TerminalPlayer(console).show_songs_found(8, 9)

    assert console.export_text() == "Found 8 Songs in 9 Beatmapsets\n"


def test_US_03_1_the_setup_guide_names_every_step_and_the_friend_option() -> None:
    console = Console(record=True, width=200)

    TerminalPlayer(console).show_spotify_setup_guide()

    screen = console.export_text()
    assert "https://developer.spotify.com/dashboard" in screen
    assert "Web API" in screen
    assert "http://127.0.0.1:8765/callback" in screen
    assert "exactly" in screen
    assert "Client ID" in screen
    friend_lines = [line for line in screen.splitlines() if "friend" in line]
    assert len(friend_lines) == 1


@pytest.mark.parametrize(
    "typed",
    [
        "0123456789abcdef0123456789abcdef",
        "  0123456789abcdef0123456789abcdef  ",
        '"0123456789abcdef0123456789abcdef"',
    ],
)
def test_US_03_2_client_id_prompt_strips_spaces_and_quotes(
    monkeypatch: pytest.MonkeyPatch, typed: str
) -> None:
    console = Console()
    type_line(monkeypatch, console, typed)

    assert TerminalPlayer(console).ask_client_id() == "0123456789abcdef0123456789abcdef"


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_US_03_2_q_quits_the_client_id_prompt(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    console = Console()
    type_line(monkeypatch, console, quit_key)

    with pytest.raises(PlayerQuit):
        TerminalPlayer(console).ask_client_id()


def test_US_03_2_and_03_3_messages_reach_the_screen() -> None:
    console = Console(record=True, width=80)
    player = TerminalPlayer(console)

    player.show_not_a_client_id()
    player.show_logged_in("[b]Kanon")

    assert console.export_text() == (
        "That does not look like a Client ID\nLogged in to Spotify as [b]Kanon\n"
    )


WAIT_LINE = (
    "Waiting for the login in your browser… press t to try again, "
    "c for another Client ID, q to quit\n"
)


def test_US_03_4_the_wait_line_reaches_the_screen() -> None:
    console = Console(record=True, width=200)

    TerminalPlayer(console).show_waiting_for_login(None)

    assert console.export_text() == WAIT_LINE


def test_US_03_4_the_login_link_is_shown_when_no_browser_opened() -> None:
    console = Console(record=True, width=40)
    url = "https://accounts.spotify.com/authorize?client_id=0123&state=x"

    TerminalPlayer(console).show_waiting_for_login(url)

    assert console.export_text() == f"Open this link to log in: {url}\n" + WAIT_LINE


def keys_waiting(monkeypatch: pytest.MonkeyPatch, *keys: str) -> None:
    """Stands in for the Windows console: keys pressed since the last look."""
    pending = list(keys)
    monkeypatch.setattr(msvcrt, "kbhit", lambda: bool(pending))
    monkeypatch.setattr(msvcrt, "getwch", lambda: pending.pop(0))


def test_US_03_4_no_key_pressed_keeps_waiting(monkeypatch: pytest.MonkeyPatch) -> None:
    keys_waiting(monkeypatch)

    assert TerminalPlayer(Console()).key_pressed_while_waiting() is None


@pytest.mark.parametrize(
    ("keys", "answer"),
    [
        (("x", "t"), "t"),
        (("T",), "t"),
        (("c",), "c"),
        (("C",), "c"),
        (("x", readchar.key.ENTER), None),
    ],
)
def test_US_03_4_t_or_c_pressed_while_waiting_is_the_answer(
    monkeypatch: pytest.MonkeyPatch, keys: tuple[str, ...], answer: str | None
) -> None:
    keys_waiting(monkeypatch, *keys)

    assert TerminalPlayer(Console()).key_pressed_while_waiting() == answer


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_US_03_4_q_pressed_while_waiting_quits(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    keys_waiting(monkeypatch, quit_key)

    with pytest.raises(PlayerQuit):
        TerminalPlayer(Console()).key_pressed_while_waiting()


def test_ctrl_c_pressed_while_waiting_stops_like_everywhere_else(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    keys_waiting(monkeypatch, "\x03")

    with pytest.raises(KeyboardInterrupt):
        TerminalPlayer(Console()).key_pressed_while_waiting()


@pytest.mark.parametrize(
    ("key", "answer"), [("t", "t"), ("T", "t"), ("c", "c"), ("C", "c")]
)
def test_US_03_4_retry_offer_takes_t_or_c(
    monkeypatch: pytest.MonkeyPatch, key: str, answer: str
) -> None:
    remaining = press(monkeypatch, "x", readchar.key.ENTER, key, "never read")
    console = Console(record=True, width=80)
    player = TerminalPlayer(console)

    player.show_login_incomplete()
    assert player.ask_login_retry() == answer

    assert list(remaining) == ["never read"]
    assert console.export_text() == (
        "The login did not complete.\n"
        "Try again [t], enter another Client ID [c] or quit [q] \n"
    )


@pytest.mark.parametrize("quit_key", ["q", "Q"])
def test_US_03_4_q_quits_the_retry_offer(
    monkeypatch: pytest.MonkeyPatch, quit_key: str
) -> None:
    press(monkeypatch, quit_key)

    with pytest.raises(PlayerQuit):
        TerminalPlayer(Console()).ask_login_retry()
