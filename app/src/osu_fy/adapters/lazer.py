"""The Source port for osu!lazer on Windows. Only ever reads (N2)."""

import codecs
from collections.abc import Callable
from pathlib import Path

from osu_fy.core.songs import Beatmapset

OSU_FILE = b"osu file format v"


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

    def read_beatmapsets(
        self, folder: Path, progress: Callable[[int, int], None]
    ) -> list[Beatmapset]:
        """Every Beatmapset in lazer's file store, found by content (ADR-006)."""
        files = [path for path in (folder / "files").rglob("*") if path.is_file()]
        beatmapsets: dict[object, Beatmapset] = {}
        for done, path in enumerate(files, 1):
            beatmapset = _read_osu_file(path)
            if beatmapset is not None:
                # Q3 of #6: without a set id, equal metadata is one Beatmapset
                key = beatmapset if beatmapset.online_id is None else beatmapset.online_id
                beatmapsets.setdefault(key, beatmapset)
            progress(done, len(files))
        return list(beatmapsets.values())

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


def _read_osu_file(path: Path) -> Beatmapset | None:
    """The Metadata section of a .osu file; None for any other file (US-02.4)."""
    metadata: dict[str, str] = {}
    try:
        with open(path, "rb") as file:
            if not file.read(32).removeprefix(codecs.BOM_UTF8).startswith(OSU_FILE):
                return None
            in_metadata = False
            for raw in file:
                line = raw.decode("utf-8", errors="replace").strip()
                if line.startswith("["):
                    if in_metadata:
                        break
                    in_metadata = line == "[Metadata]"
                elif in_metadata:
                    key, sep, value = line.partition(":")
                    if sep:
                        metadata[key.strip()] = value.strip()
    except OSError:  # vanished or locked, e.g. while lazer runs
        return None
    get = metadata.get
    if not (get("Artist") or get("ArtistUnicode")) or not (
        get("Title") or get("TitleUnicode")
    ):
        return None
    set_id = get("BeatmapSetID", "")
    online_id = int(set_id) if set_id.isdecimal() and int(set_id) > 0 else None
    return Beatmapset(
        online_id,
        get("Artist", ""),
        get("ArtistUnicode", ""),
        get("Title", ""),
        get("TitleUnicode", ""),
    )
