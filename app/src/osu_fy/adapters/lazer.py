"""The Source port for osu!lazer on Windows. Only ever reads (N2)."""

from pathlib import Path


class LazerSource:
    def __init__(self, app_data_root: Path) -> None:
        self._default = app_data_root / "osu"

    def find_lazer_folder(self) -> Path | None:
        """The folder lazer uses: storage.ini's FullPath if usable, else the default."""
        moved = self._full_path()
        if moved is not None and self.is_lazer_folder(moved):
            return moved
        return self._default if self.is_lazer_folder(self._default) else None

    def is_lazer_folder(self, path: Path) -> bool:
        return (path / "files").is_dir()

    def _full_path(self) -> Path | None:
        # Parsed like osu-framework's IniConfigManager: split at the first "=",
        # trim both sides, exact key; lazer ignores an empty FullPath.
        try:
            with open(self._default / "storage.ini", encoding="utf-8-sig") as ini:
                lines = ini.read().splitlines()
        except OSError:
            return None
        for line in lines:
            key, sep, value = line.partition("=")
            if sep and not line.startswith("#") and key.strip() == "FullPath":
                return Path(value.strip()) if value.strip() else None
        return None
