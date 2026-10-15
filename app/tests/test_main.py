from pathlib import Path

import pytest
import readchar

from osu_fy.__main__ import main
from osu_fy.core.ports import StreamingServiceUnavailable


@pytest.fixture(autouse=True)
def roaming(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temporary %APPDATA% with lazer's default folder, never the real one."""
    (tmp_path / "osu" / "files").mkdir(parents=True)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    return tmp_path


def test_osu_fy_greets_and_quits_on_q(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(readchar, "readkey", lambda: "q")

    main()  # q at "Use this lazer folder? [Y/n]" returns without a traceback

    assert "osu-fy — your osu! Songs, on Spotify" in capsys.readouterr().out


def test_ctrl_c_quits_without_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    def ctrl_c() -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(readchar, "readkey", ctrl_c)

    main()  # returns instead of raising, so Python prints no traceback


def test_US_01_4_unreadable_settings_stop_with_a_message(
    roaming: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    settings = roaming / "osu-fy" / "settings.json"
    settings.parent.mkdir()
    settings.write_text("{not json", encoding="utf-8")

    main()

    out = capsys.readouterr().out
    assert f"Cannot read {settings}: " in out.replace("\n", "")
    assert "Fix or delete it." in out


def test_US_03_8_a_stop_shows_its_message_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unreachable(*args: object) -> None:
        raise StreamingServiceUnavailable(
            "Can't reach Spotify. Everything found so far is kept; try again later."
        )

    monkeypatch.setattr("osu_fy.__main__.run_session", unreachable)

    main()  # returns instead of raising

    assert capsys.readouterr().out == (
        "Can't reach Spotify. Everything found so far is kept; try again later.\n"
    )
