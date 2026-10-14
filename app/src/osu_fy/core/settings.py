"""osu-fy's settings.json in the app-data folder: read whole, written whole and atomically."""

import json
from pathlib import Path
from typing import Any


class SettingsUnreadable(Exception):
    """settings.json exists but is not a JSON object; never overwrite it (US-01.4)."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"Cannot read {path}: {reason}. Fix or delete it.")


def load_settings(app_data: Path) -> dict[str, Any]:
    path = app_data / "settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as error:
        raise SettingsUnreadable(path, str(error)) from error
    if not isinstance(settings, dict):
        raise SettingsUnreadable(path, "not a JSON object")
    return settings


def save_settings(app_data: Path, settings: dict[str, Any]) -> None:
    app_data.mkdir(parents=True, exist_ok=True)
    temporary = app_data / "settings.json.tmp"
    temporary.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    temporary.replace(app_data / "settings.json")  # a crash never leaves half a file
