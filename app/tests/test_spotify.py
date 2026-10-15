import json
import logging
import socket
import threading
from collections.abc import Callable
from itertools import chain, repeat
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

import pytest
import requests

from osu_fy.adapters.spotify import Spotify
from osu_fy.core.ports import LoginIncomplete, StreamingServiceUnavailable

CLIENT_ID = "0123456789abcdef0123456789abcdef"  # made up
ACCESS = "fake-access-token-7f3a9c"
REFRESH = "fake-refresh-token-91c2e4"
NEW_ACCESS = "fake-access-token-refreshed-55d1"
SCOPES = {"playlist-read-private", "playlist-modify-private", "playlist-modify-public"}
TOKEN_URL = "https://accounts.spotify.com/api/token"
ME_URL = "https://api.spotify.com/v1/me/"  # spotipy adds the slash


def keep_waiting(login_url: str | None) -> bool:
    return True


class FakeSpotifySession(requests.Session):
    """Answers the token and /v1/me calls like Spotify, and records every request."""

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self.me: dict[str, Any] = {"display_name": "Kanon", "id": "kanon-id"}
        self.refresh_refused = False
        self.unreachable = False

    def request(  # spotipy passes everything but method and url by keyword
        self, method: str | bytes, url: str | bytes, *args: Any, **kwargs: Any
    ) -> requests.Response:
        assert isinstance(method, str) and isinstance(url, str) and not args
        data = kwargs.get("data") or {}
        self.requests.append((method, url, dict(data)))
        if self.unreachable:
            raise requests.ConnectionError("no network")
        if url == TOKEN_URL and data.get("grant_type") == "authorization_code":
            return answer(url, 200, token(ACCESS))
        if url == TOKEN_URL and data.get("grant_type") == "refresh_token":
            if self.refresh_refused:
                return answer(url, 400, {"error": "invalid_grant"})
            return answer(url, 200, token(NEW_ACCESS))
        if url == ME_URL:
            return answer(url, 200, self.me)
        raise AssertionError(f"unexpected request {method} {url}")


def token(access: str, expires_in: int = 3600) -> dict[str, Any]:
    return {
        "access_token": access,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "refresh_token": REFRESH,
        "scope": " ".join(sorted(SCOPES)),
    }


def answer(url: str, status: int, body: dict[str, Any]) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = url
    response._content = json.dumps(body).encode()
    return response


class Browser:
    """Stands in for webbrowser.open: answers on the loopback callback like Spotify would."""

    def __init__(self) -> None:
        self.urls: list[str] = []
        self.answer = "agree"
        self.opens = True

    def open(self, url: str) -> bool:
        self.urls.append(url)
        state = parse_qs(urlparse(url).query)["state"][0]
        query = {
            "agree": f"code=fake-code&state={state}",
            "refuse": f"error=access_denied&state={state}",
            "forged state": "code=fake-code&state=forged",
            "close the tab": None,
        }[self.answer]
        if query is not None:
            callback = f"http://127.0.0.1:8765/callback?{query}"
            threading.Thread(target=lambda: urlopen(callback).read(), daemon=True).start()
        return self.opens


@pytest.fixture
def browser(monkeypatch: pytest.MonkeyPatch) -> Browser:
    fake = Browser()
    monkeypatch.setattr("webbrowser.open", fake.open)
    return fake


@pytest.fixture
def no_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(url: str) -> bool:
        raise AssertionError("the browser opened")

    monkeypatch.setattr("webbrowser.open", fail)


@pytest.fixture
def session() -> FakeSpotifySession:
    return FakeSpotifySession()


def spotify(
    app_data: Path,
    session: FakeSpotifySession,
    clock: Callable[[], float] | None = None,
) -> Spotify:
    return Spotify(app_data, session=session, **({"clock": clock} if clock else {}))


def save_token(app_data: Path, access: str, expires_at: int) -> None:
    app_data.mkdir(parents=True, exist_ok=True)
    saved = token(access) | {"expires_at": expires_at}
    (app_data / "spotify-token.json").write_text(json.dumps(saved), encoding="utf-8")


def saved_token(app_data: Path) -> dict[str, Any]:
    loaded = json.loads((app_data / "spotify-token.json").read_text("utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_US_03_3_opens_spotify_login_and_returns_the_display_name(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    name = spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)

    assert name == "Kanon"
    [url] = browser.urls
    assert url.startswith("https://accounts.spotify.com/authorize?")
    params = {key: values[0] for key, values in parse_qs(urlparse(url).query).items()}
    assert params["client_id"] == CLIENT_ID
    assert params["redirect_uri"] == "http://127.0.0.1:8765/callback"
    assert set(params["scope"].split()) == SCOPES
    assert params["code_challenge_method"] == "S256"
    assert len(params["state"]) >= 16
    exchange = [data for _, url, data in session.requests if url == TOKEN_URL]
    assert exchange[0]["code"] == "fake-code"
    assert exchange[0]["code_verifier"]
    assert saved_token(tmp_path)["access_token"] == ACCESS


def test_US_03_3_an_empty_display_name_shows_the_spotify_user_id(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    session.me = {"display_name": None, "id": "kanon-id"}

    assert spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting) == "kanon-id"


def test_US_03_4_the_login_url_reaches_the_player_only_when_no_browser_opened(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    shown: list[str | None] = []

    def record(login_url: str | None) -> bool:
        shown.append(login_url)
        return True

    spotify(tmp_path / "a", session).log_in(CLIENT_ID, record)
    assert shown and set(shown) == {None}

    shown.clear()
    browser.opens = False
    spotify(tmp_path / "b", session).log_in(CLIENT_ID, record)
    assert shown and set(shown) == {browser.urls[-1]}


@pytest.mark.parametrize("answer", ["refuse", "forged state"])
def test_US_03_4_a_refused_or_forged_answer_does_not_complete_the_login(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession, answer: str
) -> None:
    browser.answer = answer

    with pytest.raises(LoginIncomplete):
        spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)

    assert not (tmp_path / "spotify-token.json").exists()


def test_US_03_4_a_key_pressed_while_waiting_stops_the_wait_and_frees_the_port(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    browser.answer = "close the tab"

    with pytest.raises(LoginIncomplete):
        spotify(tmp_path, session).log_in(CLIENT_ID, lambda login_url: False)

    with socket.socket() as again:
        again.bind(("127.0.0.1", 8765))  # fails if osu-fy still listens


def test_US_03_4_a_closed_tab_gives_up_after_3_minutes(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    browser.answer = "close the tab"
    clock = chain([1000.0], repeat(1000.0 + 180)).__next__  # 3 minutes pass at once

    with pytest.raises(LoginIncomplete):
        spotify(tmp_path, session, clock).log_in(CLIENT_ID, keep_waiting)


def test_US_03_4_the_wait_lasts_until_3_minutes_have_passed(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    browser.answer = "close the tab"
    clock = chain([1000.0], repeat(1000.0 + 179.9)).__next__
    calls: list[str | None] = []

    def twice(login_url: str | None) -> bool:
        calls.append(login_url)
        return len(calls) < 2

    with pytest.raises(LoginIncomplete):
        spotify(tmp_path, session, clock).log_in(CLIENT_ID, twice)

    assert len(calls) == 2  # still waiting at 179.9 s: it asked the Player again


def test_US_03_5_a_saved_login_opens_no_browser(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    save_token(tmp_path, ACCESS, expires_at=2**40)

    assert spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting) == "Kanon"
    assert [url for _, url, _ in session.requests] == [ME_URL]


def test_US_10_3_an_expired_login_is_refreshed_without_a_browser(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    save_token(tmp_path, ACCESS, expires_at=0)

    assert spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting) == "Kanon"
    assert saved_token(tmp_path)["access_token"] == NEW_ACCESS


def test_US_10_4_a_refused_refresh_opens_the_browser_to_log_in_again(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    save_token(tmp_path, ACCESS, expires_at=0)
    session.refresh_refused = True

    assert spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting) == "Kanon"
    assert len(browser.urls) == 1


def test_an_unreadable_token_file_means_logging_in_again(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    (tmp_path / "spotify-token.json").write_text("{not json", encoding="utf-8")

    assert spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting) == "Kanon"
    assert saved_token(tmp_path)["access_token"] == ACCESS


def test_US_03_6_tokens_are_kept_only_in_the_token_file(
    tmp_path: Path,
    browser: Browser,
    session: FakeSpotifySession,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    started_from = tmp_path / "started-from"
    started_from.mkdir()
    monkeypatch.chdir(started_from)
    caplog.set_level(logging.DEBUG)
    app_data = tmp_path / "Roaming" / "osu-fy"
    save_token(app_data, ACCESS, expires_at=0)
    session.refresh_refused = True  # refresh attempt, then a browser login: every token path

    spotify(app_data, session).log_in(CLIENT_ID, keep_waiting)

    assert list(started_from.iterdir()) == []  # no .cache, nothing at all
    assert [path.name for path in app_data.iterdir()] == ["spotify-token.json"]
    out, err = capsys.readouterr()
    for secret in (ACCESS, REFRESH):
        assert secret not in out
        assert secret not in err
        assert secret not in caplog.text


def test_US_03_7_contacts_only_accounts_and_api_spotify_com(
    tmp_path: Path, browser: Browser, session: FakeSpotifySession
) -> None:
    save_token(tmp_path, ACCESS, expires_at=0)
    session.refresh_refused = True  # refresh, browser login, token exchange, /v1/me

    spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)

    hosts = {urlparse(url).hostname for _, url, _ in session.requests}
    hosts |= {urlparse(url).hostname for url in browser.urls}
    assert hosts == {"accounts.spotify.com", "api.spotify.com"}


def test_US_03_8_spotify_unreachable_stops_with_a_clear_message(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    save_token(tmp_path, ACCESS, expires_at=0)
    session.unreachable = True

    with pytest.raises(StreamingServiceUnavailable) as stop:
        spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)

    assert str(stop.value) == (
        "Can't reach Spotify. Everything found so far is kept; try again later."
    )


def test_US_03_8_port_8765_in_use_stops_with_a_clear_message(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    with socket.socket() as other:
        other.bind(("127.0.0.1", 8765))
        other.listen()

        with pytest.raises(StreamingServiceUnavailable) as stop:
            spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)

    assert str(stop.value) == "Port 8765 is in use; is osu-fy already running?"
