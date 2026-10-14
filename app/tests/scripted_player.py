from pathlib import Path

from osu_fy.core.ports import PlayerQuit


class ScriptedPlayer:
    """Answers from a list ("q" quits, like the terminal) and records what it was shown."""

    def __init__(self, *answers: bool | str) -> None:
        self.answers = list(answers)
        self.shown: list[str] = []
        self.files_read: list[tuple[int, int]] = []

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

    def _next(self) -> bool | str:
        assert self.answers, "osu-fy asked more than the script answers"
        answer = self.answers.pop(0)
        if answer == "q":
            raise PlayerQuit
        return answer
