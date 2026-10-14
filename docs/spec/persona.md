# Persona — the Player

*Written once, early. Its main job is to surface the non-negotiables so they propagate
into every acceptance criterion. You will rarely re-read it — that's fine.*

## Who
- **Role:** a Player: someone who plays osu! (lazer) and wants its music on
  Spotify. First the owner, then friends.
- **Context:** Windows PC with osu!lazer installed; a Spotify account (the
  owner has Premium); a terminal.
- **Technical level:** comfortable in a terminal. The owner writes Python
  and reviews every line. Friends can install `uv`, register a Spotify
  developer app and paste a Client ID when a guide tells them how.
- **Background:** knows osu! well: Beatmapsets, TV Size cuts, Nightcore
  maps, romanised and original-script metadata.
- **Usage pattern:** occasional: after downloading a batch of new maps,
  perhaps monthly. Each Session must explain itself; nothing may depend on
  remembering how osu-fy worked last time.
- **Preferences & values:** a clean, simple interface; control over what
  goes into the Playlist (a wrong Track is worse than a missing one);
  transparency about what was not found; never wondering whether the app
  has frozen.

## Goals
- Hear the Songs they know from osu! on Spotify, without searching for each
  one by hand.
- Keep the Playlist growing as they install new maps, without duplicates and
  without redoing work.
- (Owner) a codebase clean enough to extend to other Sources and Streaming
  services, built in small reviewed steps.

## Non-negotiables (these become acceptance criteria)

- **N1 — Append only.** osu-fy never removes, replaces or reorders a Track in
  any playlist. After a Session, every Track that was in the Playlist before
  is still there, in the same order, and new Tracks come after them. The
  Streaming service port has no operation that removes or reorders.
- **N2 — The osu! install is read only.** osu-fy never creates, changes or
  deletes a file in the lazer folder (or later the stable folder): every
  file there has the same size and modification time before and after a
  Session, and no file is created.
- **N3 — Secrets stay secret.** Spotify access and refresh tokens never
  appear in terminal output, in any file osu-fy writes other than its token
  file in the app-data folder, or in the repository. osu-fy never writes a
  file into the folder it was started from.
- **N4 — Nothing leaves except to osu! and the Streaming service.** The only
  hosts osu-fy contacts in version one are `accounts.spotify.com` and
  `api.spotify.com`. No telemetry, no other lookup service.
- **N5 — Never twice.** A Track appears at most once in the Playlist, across
  Sessions, when several Songs or Beatmapsets lead to it, and when the
  Player added it by hand. The Playlist on Spotify is the truth for this,
  not osu-fy's memory.

## Out of scope / explicitly NOT wanted
- Adding Doubtful matches the Player has not seen: "add all" only after the
  full list was shown.
- Silent waiting: any wait longer than a moment shows what osu-fy waits for
  and for how long.
- Python tracebacks shown to the Player for expected failures (no network,
  rate limit, login refused).
- Shipping anyone's Spotify Client ID in the repository.
- Probing Spotify's rate limit to find "the fastest rate".
