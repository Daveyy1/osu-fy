import pytest
import readchar

from osu_fy.__main__ import main


def test_osu_fy_greets_and_quits_on_q(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(readchar, "readkey", lambda: "q")

    main()

    assert "osu-fy — your osu! Songs, on Spotify" in capsys.readouterr().out


def test_ctrl_c_quits_without_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    def ctrl_c() -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(readchar, "readkey", ctrl_c)

    main()  # returns instead of raising, so Python prints no traceback
