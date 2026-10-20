from collections.abc import Callable

from osu_fy.core.ports import LoginIncomplete, Playlist, Track

INCOMPLETE = LoginIncomplete()


class FakeStreaming:
    """log_in answers from a script: a display name, or INCOMPLETE after the browser opened.

    library holds the playlists in the Player's Spotify library, by id; contents
    the Track ids in each Playlist, by id, in order; searches the answer to each
    search, by (artist, title).
    """

    def __init__(self, *logins: str | LoginIncomplete) -> None:
        self.logins = list(logins)
        self.client_ids: list[str] = []
        self.library: dict[str, Playlist] = {}
        self.created: list[str] = []
        self.contents: dict[str, list[str]] = {}
        self.searches: dict[tuple[str, str], list[Track]] = {}
        self.searched: list[tuple[str, str]] = []

    def log_in(self, client_id: str, keep_waiting: Callable[[str | None], bool]) -> str:
        self.client_ids.append(client_id)
        assert self.logins, "osu-fy logged in more often than the script answers"
        login = self.logins.pop(0)
        if isinstance(login, LoginIncomplete):
            # the browser opened; then the Player stopped or Spotify refused
            keep_waiting(None)
            raise login
        return login

    def create_playlist(self, name: str) -> Playlist:
        self.created.append(name)
        playlist_id = f"created-{len(self.created)}"
        playlist = Playlist(
            playlist_id, name, f"https://open.spotify.com/playlist/{playlist_id}"
        )
        self.library[playlist_id] = playlist
        self.contents[playlist_id] = []
        return playlist

    def find_playlist(self, playlist_id: str) -> Playlist | None:
        return self.library.get(playlist_id)

    def find_tracks(self, artist: str, title: str) -> list[Track]:
        self.searched.append((artist, title))
        # loud, so a test never passes on a search it did not expect
        assert (artist, title) in self.searches, f"no answer for {artist} – {title}"
        return self.searches[(artist, title)]

    def tracks_in_playlist(self, playlist: Playlist) -> set[str]:
        return set(self.contents[playlist.id])

    def append_tracks(self, playlist: Playlist, tracks: list[str]) -> None:
        # append only: nothing else changes a Playlist (N1)
        self.contents[playlist.id] += tracks
