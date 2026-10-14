from osu_fy.core.session import run_session


class ScriptedPlayer:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def greet(self) -> None:
        self.calls.append("greet")

    def wait_for_quit(self) -> None:
        self.calls.append("wait_for_quit")


def test_session_greets_the_player_then_waits_for_them_to_quit() -> None:
    player = ScriptedPlayer()

    run_session(player)

    assert player.calls == ["greet", "wait_for_quit"]
