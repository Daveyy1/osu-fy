from pathlib import Path

from osu_fy.core.matching import Match
from osu_fy.core.ports import Player, Playlist, StreamingService
from osu_fy.core.settings import load_settings, save_settings

DEFAULT_NAME = "osu!fy"


def ensure_playlist(
    streaming: StreamingService, player: Player, app_data: Path
) -> Playlist:
    """The Session step that creates the Playlist once, then finds it by its id (US-04)."""
    playlist_id = load_settings(app_data).get("spotify_playlist_id")
    if isinstance(playlist_id, str):
        # by id, never by name: a playlist the Player named osu!fy stays untouched (US-04.3)
        playlist = streaming.find_playlist(playlist_id)
        if playlist is not None:
            player.show_playlist_in_use(playlist)
            return playlist
        player.show_playlist_gone()  # deleted in Spotify, or another account (US-04.4)

    playlist = streaming.create_playlist(player.ask_playlist_name(DEFAULT_NAME))
    settings = load_settings(app_data)
    settings["spotify_playlist_id"] = playlist.id
    # saved at once, so a stop now does not create a second Playlist next time
    save_settings(app_data, settings)
    player.show_playlist_created(playlist)
    return playlist


def add_certain_matches(
    matches: list[Match], streaming: StreamingService, player: Player, playlist: Playlist
) -> None:
    """The Session step that appends the Certain matches' Tracks the Playlist lacks (US-06)."""
    # each Track once, in Song order (US-06.3)
    certain = dict.fromkeys(match.track.id for match in matches if match.certain)
    # read from the service every time, never from osu-fy's memory (N5)
    already = streaming.tracks_in_playlist(playlist)
    new = [track for track in certain if track not in already]
    streaming.append_tracks(playlist, new)
    player.show_tracks_added(len(new), len(certain) - len(new), playlist)
