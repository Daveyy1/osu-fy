import re
from pathlib import Path

from osu_fy.core.ports import LoginIncomplete, Player, StreamingService
from osu_fy.core.settings import load_settings, save_settings

CLIENT_ID = re.compile(r"[0-9a-f]{32}")


def connect_to_spotify(streaming: StreamingService, player: Player, app_data: Path) -> None:
    """The Session step that logs in to Spotify (US-03), asking for the Client ID once."""
    client_id = load_settings(app_data).get("spotify_client_id")
    if not isinstance(client_id, str):
        player.show_spotify_setup_guide()
        client_id = _ask_client_id(player, app_data)

    while True:
        pressed: str | None = None
        waiting = False

        def keep_waiting(login_url: str | None) -> bool:
            nonlocal pressed, waiting
            if not waiting:
                player.show_waiting_for_login(login_url)
                waiting = True
            pressed = player.key_pressed_while_waiting()
            return pressed is None

        try:
            player.show_logged_in(streaming.log_in(client_id, keep_waiting))
            return
        except LoginIncomplete:
            player.show_login_incomplete()
        if (pressed or player.ask_login_retry()) == "c":  # a key pressed while waiting is the answer
            client_id = _ask_client_id(player, app_data)


def _ask_client_id(player: Player, app_data: Path) -> str:
    client_id = player.ask_client_id().lower()  # Spotify's Client IDs are lower case
    while not CLIENT_ID.fullmatch(client_id):
        player.show_not_a_client_id()
        client_id = player.ask_client_id().lower()
    settings = load_settings(app_data)
    settings["spotify_client_id"] = client_id
    save_settings(app_data, settings)  # saved before the login, so it outlives a failed one
    return client_id
