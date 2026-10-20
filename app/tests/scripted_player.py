from pathlib import Path

from osu_fy.core.ports import PlayerQuit, Playlist


class ScriptedPlayer:
    """Answers from a list ("q" quits, like the terminal) and records what it was shown."""

    def __init__(self, *answers: bool | str | None) -> None:
        self.answers = list(answers)
        self.shown: list[str] = []
        self.files_read: list[tuple[int, int]] = []
        self.songs_searched: list[tuple[int, int]] = []

    def greet(self) -> None:
        self.shown.append("greet")

    def wait_for_quit(self) -> None:
        self.shown.append("wait_for_quit")

    def confirm_lazer_folder(self, path: Path) -> bool:
        self.shown.append(f"Use this lazer folder? {path}")
        answer = self._next()
        assert isinstance(answer, bool)
        return answer

    def ask_lazer_folder(self) -> Path:
        self.shown.append("Path to the lazer folder?")
        answer = self._next()
        assert isinstance(answer, str)
        return Path(answer)

    def show_no_lazer_data(self, path: Path) -> None:
        self.shown.append(f"No lazer data found in {path}")

    def show_reading_lazer_folder(self, path: Path) -> None:
        self.shown.append(f"Reading lazer folder {path}")

    def show_files_read(self, done: int, total: int) -> None:
        self.files_read.append((done, total))

    def show_songs_found(self, songs: int, beatmapsets: int) -> None:
        self.shown.append(f"Found {songs} Songs in {beatmapsets} Beatmapsets")

    def show_spotify_setup_guide(self) -> None:
        self.shown.append("Spotify setup guide")

    def ask_client_id(self) -> str:
        self.shown.append("Client ID?")
        answer = self._next()
        assert isinstance(answer, str)
        return answer

    def show_not_a_client_id(self) -> None:
        self.shown.append("That does not look like a Client ID")

    def show_waiting_for_login(self, login_url: str | None) -> None:
        self.shown.append(f"Waiting for the login in your browser {login_url}")

    def key_pressed_while_waiting(self) -> str | None:
        answer = self._next()
        assert answer is None or answer in ("t", "c")
        return answer

    def show_login_incomplete(self) -> None:
        self.shown.append("The login did not complete.")

    def ask_login_retry(self) -> str:
        self.shown.append("Try again [t], enter another Client ID [c] or quit [q]")
        answer = self._next()
        assert answer in ("t", "c")
        return answer

    def show_logged_in(self, name: str) -> None:
        self.shown.append(f"Logged in to Spotify as {name}")

    def ask_playlist_name(self, default: str) -> str:
        self.shown.append(f"Name for your Playlist [{default}]:")
        answer = self._next()  # None stands for Enter
        assert answer is None or isinstance(answer, str)
        return default if answer is None else answer

    def show_playlist_created(self, playlist: Playlist) -> None:
        self.shown.append(f"Created your Playlist {playlist.name} {playlist.link}")

    def show_playlist_in_use(self, playlist: Playlist) -> None:
        self.shown.append(f"Adding to your Playlist {playlist.name} {playlist.link}")

    def show_playlist_gone(self) -> None:
        self.shown.append("Your Playlist is no longer in your Spotify library.")

    def show_songs_searched(self, done: int, total: int) -> None:
        self.songs_searched.append((done, total))

    def show_match_summary(self, certain: int, doubtful: int, unmatched: int) -> None:
        self.shown.append(
            f"{certain} Certain matches, {doubtful} Doubtful matches, "
            f"{unmatched} Unmatched Songs"
        )

    def show_tracks_added(self, added: int, already: int, playlist: Playlist) -> None:
        already_there = f" ({already} were already in the Playlist)" if already else ""
        self.shown.append(f"Added {added} Tracks to {playlist.name}{already_there}")

    def _next(self) -> bool | str | None:
        assert self.answers, "osu-fy asked more than the script answers"
        answer = self.answers.pop(0)
        if answer == "q":
            raise PlayerQuit
        return answer
