from pathlib import Path

from osu_fy.core.ports import Player, Source
from osu_fy.core.settings import load_settings, save_settings


def find_lazer_folder(source: Source, player: Player, app_data: Path) -> Path:
    """The Session step that finds the lazer folder (US-01) and remembers it."""
    settings = load_settings(app_data)
    remembered = settings.get("lazer_folder")
    if isinstance(remembered, str):
        if source.is_lazer_folder(Path(remembered)):
            player.show_reading_lazer_folder(Path(remembered))
            return Path(remembered)
        player.show_no_lazer_data(Path(remembered))

    folder = source.find_lazer_folder()
    if folder is None or not player.confirm_lazer_folder(folder):
        folder = player.ask_lazer_folder()
        while not source.is_lazer_folder(folder):
            player.show_no_lazer_data(folder)
            folder = player.ask_lazer_folder()

    settings["lazer_folder"] = str(folder)
    save_settings(app_data, settings)
    player.show_reading_lazer_folder(folder)
    return folder
