from collections.abc import Callable

from osu_fy.core.ports import LoginIncomplete

INCOMPLETE = LoginIncomplete()


class FakeStreaming:
    """log_in answers from a script: a display name, or INCOMPLETE after the browser opened."""

    def __init__(self, *logins: str | LoginIncomplete) -> None:
        self.logins = list(logins)
        self.client_ids: list[str] = []

    def log_in(self, client_id: str, keep_waiting: Callable[[str | None], bool]) -> str:
        self.client_ids.append(client_id)
        assert self.logins, "osu-fy logged in more often than the script answers"
        login = self.logins.pop(0)
        if isinstance(login, LoginIncomplete):
            keep_waiting(None)  # the browser opened; then the Player stopped or Spotify refused
            raise login
        return login
