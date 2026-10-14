from collections.abc import Iterator

import pytest
import readchar
from rich.console import Console

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
