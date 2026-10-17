"""The Streaming service port on Spotify, through spotipy (ADR-004, ADR-007)."""

import json
import logging
import secrets
import time
import webbrowser
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import requests
import spotipy
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOauthError, SpotifyPKCE, start_local_http_server

from osu_fy.core.ports import LoginIncomplete, Playlist, StreamingServiceUnavailable

PORT = 8765
REDIRECT_URI = f"http://127.0.0.1:{PORT}/callback"
# playlist-modify-public only so appending still works if the Player makes the Playlist public
SCOPES = "playlist-read-private playlist-modify-private playlist-modify-public"
LOGIN_TIMEOUT = 180  # seconds (US-03.4)
REQUEST_TIMEOUT = 10  # seconds (api_contracts)
CANT_REACH = "Can't reach Spotify. Everything found so far is kept; try again later."
PORT_IN_USE = f"Port {PORT} is in use; is osu-fy already running?"
DESCRIPTION = "Songs from osu!, added by osu-fy"

# spotipy logs the Authorization header and token requests at DEBUG (N3); a level,
# unlike `disabled`, also holds for its child loggers spotipy.client and spotipy.oauth2
logging.getLogger("spotipy").setLevel(logging.CRITICAL + 1)


class TokenFile(CacheHandler):  # type: ignore[misc]  # spotipy has no type hints
    """spotipy's token cache, kept only in osu-fy's app-data folder, never in .cache (N3)."""

    def __init__(self, app_data: Path) -> None:
        self._app_data = app_data

    def get_cached_token(self) -> dict[str, Any] | None:
        try:
            token = json.loads(
                (self._app_data / "spotify-token.json").read_text("utf-8")
            )
        except (OSError, ValueError):
            return None  # no token, or an unreadable one: the Player logs in again
        return token if isinstance(token, dict) else None

    def save_token_to_cache(self, token_info: dict[str, Any]) -> None:
        self._app_data.mkdir(parents=True, exist_ok=True)
        temporary = self._app_data / "spotify-token.json.tmp"
        temporary.write_text(json.dumps(token_info), encoding="utf-8")
        temporary.replace(self._app_data / "spotify-token.json")


class Spotify:
    def __init__(
        self,
        app_data: Path,
        session: requests.Session | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._tokens = TokenFile(app_data)
        # a plain Session never retries, so spotipy never sleeps silently on a 429 (ADR-004)
        self._session = session or requests.Session()
        self._clock = clock
        self._client: spotipy.Spotify | None = None

    def log_in(self, client_id: str, keep_waiting: Callable[[str | None], bool]) -> str:
        auth = SpotifyPKCE(
            client_id=client_id,
            redirect_uri=REDIRECT_URI,
            scope=SCOPES,
            cache_handler=self._tokens,
            open_browser=False,
            requests_timeout=REQUEST_TIMEOUT,
            requests_session=self._session,
        )
        with _reachable():
            if not self._has_usable_login(auth):
                self._log_in_in_browser(auth, keep_waiting)
            self._client = spotipy.Spotify(
                auth_manager=auth,
                requests_session=self._session,
                requests_timeout=REQUEST_TIMEOUT,
            )
            me = self._client.current_user()
        return str(me["display_name"] or me["id"])

    def create_playlist(self, name: str) -> Playlist:
        with _reachable():
            created = self._logged_in().current_user_playlist_create(
                name,
                public=False,  # spotipy's default is public
                description=DESCRIPTION,
            )
        return _playlist(created)

    def find_playlist(self, playlist_id: str) -> Playlist | None:
        client = self._logged_in()
        with _reachable():
            page = client.current_user_playlists(limit=50)
            while page is not None:
                for item in page["items"]:
                    if item and item["id"] == playlist_id:
                        return _playlist(item)
                page = client.next(page)  # None after the last page
        return None

    def _logged_in(self) -> spotipy.Spotify:
        assert self._client is not None, "log_in comes first in every Session"
        return self._client

    def _has_usable_login(self, auth: SpotifyPKCE) -> bool:
        try:  # validate_token refreshes an expired token (US-10.3)
            return auth.validate_token(self._tokens.get_cached_token()) is not None
        except SpotifyOauthError:
            return False  # refresh refused, e.g. the Player removed osu-fy's access (US-10.4)

    def _log_in_in_browser(
        self, auth: SpotifyPKCE, keep_waiting: Callable[[str | None], bool]
    ) -> None:
        # spotipy's own wait has no timeout and no state check, so osu-fy waits itself (Q2)
        try:
            server = start_local_http_server(PORT)
        except OSError as error:
            raise StreamingServiceUnavailable(PORT_IN_USE) from error
        server.timeout = 1  # handle_request returns after a second without a request
        try:
            state = secrets.token_urlsafe(16)
            url = auth.get_authorize_url(state)
            login_url = None if webbrowser.open(url) else url
            deadline = self._clock() + LOGIN_TIMEOUT
            while keep_waiting(login_url) and self._clock() < deadline:
                server.handle_request()
                if server.error is not None:
                    raise LoginIncomplete  # the Player refused access
                if server.auth_code is not None:
                    if server.state != state:
                        raise LoginIncomplete  # not the answer to our request
                    try:
                        auth.get_access_token(server.auth_code, check_cache=False)
                    except SpotifyOauthError as error:
                        raise LoginIncomplete from error
                    return
            raise LoginIncomplete
        finally:
            server.server_close()


@contextmanager
def _reachable() -> Iterator[None]:
    """No network, a timeout or a 5xx stops the Session with CANT_REACH (US-03.8)."""
    try:
        yield
    except (requests.ConnectionError, requests.Timeout) as error:
        raise StreamingServiceUnavailable(CANT_REACH) from error
    except spotipy.SpotifyException as error:
        if error.http_status >= 500:
            raise StreamingServiceUnavailable(CANT_REACH) from error
        raise


def _playlist(item: dict[str, Any]) -> Playlist:
    return Playlist(item["id"], item["name"], item["external_urls"]["spotify"])
