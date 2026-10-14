from osu_fy.core.ports import Player


def run_session(player: Player) -> None:
    """One Session, from starting osu-fy to quitting."""
    player.greet()
    player.wait_for_quit()
