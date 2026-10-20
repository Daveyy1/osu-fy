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
from osu_fy.core.ports import (
    LoginIncomplete,
    Playlist,
    StreamingServiceUnavailable,
    Track,
)

CLIENT_ID = "0123456789abcdef0123456789abcdef"  # made up
ACCESS = "fake-access-token-7f3a9c"
REFRESH = "fake-refresh-token-91c2e4"
NEW_ACCESS = "fake-access-token-refreshed-55d1"
SCOPES = {"playlist-read-private", "playlist-modify-private", "playlist-modify-public"}
TOKEN_URL = "https://accounts.spotify.com/api/token"
ME_URL = "https://api.spotify.com/v1/me/"  # spotipy adds the slash
PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"
SEARCH_URL = "https://api.spotify.com/v1/search"
ITEMS_URL = "https://api.spotify.com/v1/playlists/mine/items"
MINE = Playlist("mine", "osu!fy", "https://open.spotify.com/playlist/mine")


def keep_waiting(login_url: str | None) -> bool:
    return True


class FakeSpotifySession(requests.Session):
    """Answers the token, /v1/me, /v1/me/playlists and playlist-items calls like Spotify.

    Records every request with what it sent: form data, a JSON body or the query;
    a JSON list body as {"body": [...]} with the query.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[tuple[str, str, dict[str, Any]]] = []
        self.me: dict[str, Any] = {"display_name": "Kanon", "id": "kanon-id"}
        self.library: list[dict[str, Any]] = []  # the Player's playlists, in order
        self.items: list[dict[str, Any]] = []  # the items of the playlist "mine"
        self.refresh_refused = False
        self.unreachable = False
        self.found: list[dict[str, Any] | None] = []  # what a search finds
        self.retry_after: str | None = None  # set: every API request gets a 429

    def request(  # spotipy passes everything but method and url by keyword
        self, method: str | bytes, url: str | bytes, *args: Any, **kwargs: Any
    ) -> requests.Response:
        assert isinstance(method, str) and isinstance(url, str) and not args
        data = kwargs.get("data") or {}
        if isinstance(data, str):
            data = json.loads(data)  # spotipy sends API bodies as JSON text
        query = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        params = kwargs.get("params") or {}
        # requests leaves out None, as spotipy relies on
        query |= {k: str(v) for k, v in params.items() if v is not None}
        url = url.split("?")[0]
        if isinstance(data, list):  # spotipy posts the URIs to add as a bare list
            self.requests.append((method, url, {"body": data} | query))
        else:
            self.requests.append((method, url, dict(data) or query))
        if self.unreachable:
            raise requests.ConnectionError("no network")
        if url == TOKEN_URL and data.get("grant_type") == "authorization_code":
            return answer(url, 200, token(ACCESS))
        if url == TOKEN_URL and data.get("grant_type") == "refresh_token":
            if self.refresh_refused:
                return answer(url, 400, {"error": "invalid_grant"})
            return answer(url, 200, token(NEW_ACCESS))
        if self.retry_after is not None and "api.spotify.com" in url:
            headers = {"Retry-After": self.retry_after} if self.retry_after else {}
            return answer(url, 429, {"error": {"status": 429}}, headers)
        if url == ME_URL:
            return answer(url, 200, self.me)
        if method == "POST" and url == ITEMS_URL:
            return answer(url, 201, {"snapshot_id": "made-up"})
        if method == "GET" and url == ITEMS_URL:
            offset, limit = int(query.get("offset", 0)), int(query["limit"])
            more = offset + limit < len(self.items)
            return answer(
                url,
                200,
                {
                    "items": self.items[offset : offset + limit],
                    "next": f"{url}?offset={offset + limit}&limit={limit}"
                    if more
                    else None,
                },
            )
        if method == "GET" and url == SEARCH_URL:
            return answer(url, 200, {"tracks": {"items": self.found}})
        if method == "POST" and url == PLAYLISTS_URL:
            created = spotify_playlist("new-id", data["name"])
            self.library.insert(0, created)
            return answer(url, 201, created)
        if method == "GET" and url == PLAYLISTS_URL:
            offset, limit = int(query.get("offset", 0)), int(query["limit"])
            more = offset + limit < len(self.library)
            return answer(
                url,
                200,
                {
                    "items": self.library[offset : offset + limit],
                    "next": f"{url}?offset={offset + limit}&limit={limit}"
                    if more
                    else None,
                },
            )
        raise AssertionError(f"unexpected request {method} {url}")


def spotify_playlist(playlist_id: str, name: str) -> dict[str, Any]:
    """A playlist as Spotify describes it, trimmed to the fields osu-fy reads."""
    return {
        "id": playlist_id,
        "name": name,
        "external_urls": {
            "spotify": f"https://open.spotify.com/playlist/{playlist_id}"
        },
    }


def token(access: str, expires_in: int = 3600) -> dict[str, Any]:
    return {
        "access_token": access,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "refresh_token": REFRESH,
        "scope": " ".join(sorted(SCOPES)),
    }


def answer(
    url: str, status: int, body: dict[str, Any], headers: dict[str, str] | None = None
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = url
    response.headers.update(headers or {})
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
            threading.Thread(
                target=lambda: urlopen(callback).read(), daemon=True
            ).start()
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


def no_sleep(seconds: float) -> None:
    pass  # no test waits in real time


def spotify(
    app_data: Path,
    session: FakeSpotifySession,
    clock: Callable[[], float] | None = None,
    sleep: Callable[[float], None] = no_sleep,
) -> Spotify:
    return Spotify(
        app_data, session=session, sleep=sleep, **({"clock": clock} if clock else {})
    )


def save_token(app_data: Path, access: str, expires_at: int) -> None:
    app_data.mkdir(parents=True, exist_ok=True)
    saved = token(access) | {"expires_at": expires_at}
    (app_data / "spotify-token.json").write_text(json.dumps(saved), encoding="utf-8")


def logged_in(
    app_data: Path, session: FakeSpotifySession, adapter: Spotify | None = None
) -> Spotify:
    save_token(app_data, ACCESS, expires_at=2**40)
    adapter = adapter or spotify(app_data, session)
    adapter.log_in(CLIENT_ID, keep_waiting)
    session.requests.clear()
    return adapter


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
    # a refresh attempt, then a browser login: every path a token takes
    session.refresh_refused = True

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


def test_US_04_1_creates_a_private_playlist_with_the_name_and_returns_its_link(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    playlist = logged_in(tmp_path, session).create_playlist("osu!fy")

    assert playlist == Playlist(
        "new-id", "osu!fy", "https://open.spotify.com/playlist/new-id"
    )
    [(method, url, body)] = session.requests
    assert (method, url) == ("POST", PLAYLISTS_URL)
    assert body["name"] == "osu!fy"
    assert body["public"] is False  # spotipy's default is public
    assert body["description"] == "Songs from osu!, added by osu-fy"


def test_US_04_2_finds_the_playlist_by_id_on_a_later_page_with_its_current_name(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    session.library = [spotify_playlist(f"other-{n}", "osu!fy") for n in range(50)]
    session.library.append(spotify_playlist("mine", "Renamed"))

    found = logged_in(tmp_path, session).find_playlist("mine")

    assert found == Playlist(
        "mine", "Renamed", "https://open.spotify.com/playlist/mine"
    )
    assert session.requests == [
        ("GET", PLAYLISTS_URL, {"limit": "50", "offset": "0"}),
        ("GET", PLAYLISTS_URL, {"limit": "50", "offset": "50"}),
    ]


def test_US_04_4_a_playlist_in_no_page_of_the_library_is_not_found(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    session.library = [spotify_playlist(f"other-{n}", "x") for n in range(3)]

    assert logged_in(tmp_path, session).find_playlist("gone") is None


def test_US_03_7_the_playlist_calls_contact_only_api_spotify_com(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    adapter = logged_in(tmp_path, session)

    adapter.find_playlist(adapter.create_playlist("osu!fy").id)

    assert {urlparse(url).hostname for _, url, _ in session.requests} == {
        "api.spotify.com"
    }


@pytest.mark.parametrize("call", ["create", "find"])
def test_spotify_unreachable_at_the_playlist_stops_with_the_clear_message(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession, call: str
) -> None:
    adapter = logged_in(tmp_path, session)
    session.unreachable = True

    with pytest.raises(StreamingServiceUnavailable) as stop:
        if call == "create":
            adapter.create_playlist("osu!fy")
        else:
            adapter.find_playlist("mine")

    assert str(stop.value) == (
        "Can't reach Spotify. Everything found so far is kept; try again later."
    )


def spotify_track(title: str, *artists: str) -> dict[str, Any]:
    """A Track as Spotify describes it, trimmed to the fields osu-fy reads; made-up id."""
    return {
        "id": f"made-up-{title}",
        "name": title,
        "artists": [{"name": artist} for artist in artists],
        "album": {"name": "Album"},
        "duration_ms": 200_000,
    }


def test_US_05_3_find_tracks_searches_by_track_and_artist_and_reads_the_tracks(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    # Spotify sends null for an item it cannot show
    session.found = [spotify_track("ケロ⑨destiny", "Silver Forest"), None]

    tracks = logged_in(tmp_path, session).find_tracks("Silver Forest", "ケロ⑨destiny")

    assert tracks == [
        Track(
            "made-up-ケロ⑨destiny", "ケロ⑨destiny", ("Silver Forest",), "Album", 200_000
        )
    ]
    [(method, url, query)] = session.requests
    assert (method, url) == ("GET", SEARCH_URL)
    assert query == {
        "q": 'track:"ケロ⑨destiny" artist:"Silver Forest"',
        "type": "track",
        "limit": "10",
        "offset": "0",
    }


def test_double_quotes_in_a_title_are_dropped_from_the_search(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    logged_in(tmp_path, session).find_tracks("Ado", 'Usseewa "Remix"')

    [(_, _, query)] = session.requests
    assert query["q"] == 'track:"Usseewa Remix" artist:"Ado"'


def test_US_03_7_the_search_contacts_only_api_spotify_com(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    logged_in(tmp_path, session).find_tracks("Kano", "Walk This Way!")

    assert {urlparse(url).hostname for _, url, _ in session.requests} == {
        "api.spotify.com"
    }


def playlist_item(track_id: str | None) -> dict[str, Any]:
    """A playlist item as Spotify sends it since February 2026 (checked on #11)."""
    return {"item": {"id": track_id}}


def test_US_06_2_reads_every_track_in_the_playlist_page_by_page(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    session.items = [playlist_item(f"track{n}") for n in range(149)]
    session.items.insert(7, playlist_item(None))  # a local file has no id

    found = logged_in(tmp_path, session).tracks_in_playlist(MINE)

    assert found == {f"track{n}" for n in range(149)}
    [(_, first_url, first), (_, second_url, second)] = session.requests
    assert first_url == second_url == ITEMS_URL
    assert first["fields"] == "items(item(id)),next"  # `track` is empty since 2026
    assert (first["limit"], first["offset"]) == ("100", "0")
    assert second["offset"] == "100"


def test_US_06_5_more_than_100_tracks_go_out_in_requests_of_at_most_100(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    tracks = [f"track{n}" for n in range(148)]

    logged_in(tmp_path, session).append_tracks(MINE, tracks)

    uris = [f"spotify:track:{track}" for track in tracks]
    # no position anywhere: Spotify then appends at the end (US-06.4)
    assert session.requests == [
        ("POST", ITEMS_URL, {"body": uris[:100]}),
        ("POST", ITEMS_URL, {"body": uris[100:]}),
    ]


def test_nothing_to_append_sends_no_request(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    logged_in(tmp_path, session).append_tracks(MINE, [])

    assert session.requests == []


def test_US_03_7_the_playlist_items_calls_contact_only_api_spotify_com(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    adapter = logged_in(tmp_path, session)

    adapter.tracks_in_playlist(MINE)
    adapter.append_tracks(MINE, ["track1"])

    assert {urlparse(url).hostname for _, url, _ in session.requests} == {
        "api.spotify.com"
    }


@pytest.mark.parametrize("call", ["read", "append"])
def test_spotify_unreachable_while_adding_stops_with_the_clear_message(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession, call: str
) -> None:
    adapter = logged_in(tmp_path, session)
    session.unreachable = True

    with pytest.raises(StreamingServiceUnavailable) as stop:
        if call == "read":
            adapter.tracks_in_playlist(MINE)
        else:
            adapter.append_tracks(MINE, ["track1"])

    assert str(stop.value) == (
        "Can't reach Spotify. Everything found so far is kept; try again later."
    )


class FakeTime:
    """A clock that moves only when osu-fy sleeps; notes when each request went out."""

    def __init__(self, session: FakeSpotifySession) -> None:
        self.now = 1000.0
        self.sent: list[float] = []
        original = session.request

        def timed(*args: Any, **kwargs: Any) -> requests.Response:
            self.sent.append(self.now)
            return original(*args, **kwargs)

        session.request = timed  # type: ignore[method-assign]

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        assert seconds > 0
        self.now += seconds


def test_US_05_9_at_least_1_second_between_requests_and_at_most_30_in_30_seconds(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    time = FakeTime(session)
    save_token(tmp_path, ACCESS, expires_at=0)  # the refresh is paced too (Q4 of #9)
    adapter = spotify(tmp_path, session, time.clock, time.sleep)
    adapter.log_in(CLIENT_ID, keep_waiting)
    adapter.create_playlist("osu!fy")
    for n in range(40):
        adapter.find_tracks("Kano", f"Song {n}")

    assert len(time.sent) == 43  # refresh, /v1/me, the Playlist, 40 searches
    assert all(b - a >= 1 for a, b in zip(time.sent, time.sent[1:], strict=False))
    assert max(sum(s <= t < s + 30 for t in time.sent) for s in time.sent) <= 30


def test_US_05_9_no_wait_when_a_second_has_passed_already(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession
) -> None:
    time = FakeTime(session)
    adapter = spotify(tmp_path, session, time.clock, time.sleep)
    logged_in(tmp_path, session, adapter)
    time.now += 5  # the Player took 5 s to answer a question

    adapter.find_tracks("Kano", "Walk This Way!")

    assert time.sent[-1] - time.sent[-2] == 5


@pytest.mark.parametrize(
    ("retry_after", "shown"),
    [
        ("30", "Spotify asks us to wait 30 s"),
        ("120", "Spotify asks us to wait 120 s"),
        ("121", "Spotify asks us to wait 3 min"),
        ("720", "Spotify asks us to wait 12 min"),
        ("18180", "Spotify asks us to wait 5 h 3 min"),
        ("18001", "Spotify asks us to wait 5 h 1 min"),
        ("", "Spotify asks us to wait."),
    ],
)
def test_US_05_11_too_many_requests_stops_without_waiting(
    tmp_path: Path,
    no_browser: None,
    session: FakeSpotifySession,
    retry_after: str,
    shown: str,
) -> None:
    adapter = logged_in(tmp_path, session)
    session.retry_after = retry_after

    with pytest.raises(StreamingServiceUnavailable) as stop:
        adapter.find_tracks("Kano", "Walk This Way!")

    assert str(stop.value) == shown
    assert len(session.requests) == 1  # no hidden retry


@pytest.mark.parametrize("call", ["log in", "create", "find"])
def test_US_05_11_too_many_requests_stops_every_call(
    tmp_path: Path, no_browser: None, session: FakeSpotifySession, call: str
) -> None:
    if call == "log in":
        save_token(tmp_path, ACCESS, expires_at=2**40)
        session.retry_after = "30"
        with pytest.raises(StreamingServiceUnavailable) as stop:
            spotify(tmp_path, session).log_in(CLIENT_ID, keep_waiting)
    else:
        adapter = logged_in(tmp_path, session)
        session.retry_after = "30"
        with pytest.raises(StreamingServiceUnavailable) as stop:
            if call == "create":
                adapter.create_playlist("osu!fy")
            else:
                adapter.find_playlist("mine")

    assert str(stop.value) == "Spotify asks us to wait 30 s"
