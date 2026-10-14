# Hand-off note

*The assistant keeps no memory between sessions: only what is written down.
Update this note at the end of every session that leaves work open. Keep it
short. It says where to continue, not what was done: the issues and pull
requests are the record of that.*

## Resume here (the exact next step)
1. The spec, ADR-004 to ADR-007 and the toolchain (PRs #1 to #3) are on
   `main`. Issues #4 to #16 hold version one, one per ticket, with GitHub's
   native "blocked by" links; `docs/spec/roadmap.md` maps them.
2. Next: in a work session (`claude --settings .claude/work-settings.json`),
   `/plan 4` (walking skeleton). Then the owner answers and sets
   `plan-approved`, and `/build`.

## Settled in the interview (rounds 1 to 7), now written into `docs/spec/`
- **What it is:** osu-fy turns the Songs a Player knows from osu! into a
  playlist on their Streaming service. Spotify first, others later.
- **Who it is for:** the owner first, and friends who can handle a terminal
  and their own API keys.
- **Why a rewrite:** the first tool was rough and unoptimised and its CLI was
  ugly. Wanted: a clean, simple interface and room for other services.
- **Form:** a guided terminal app first, logic separate from the interface;
  a web app or GUI later.
- **Sources:** installed Beatmapsets (osu! stable and lazer) and the lists
  tied to the osu! account.
- **Uncertain matches:** only certain matches go into the playlist; the
  Player gets the doubtful and the unmatched Songs to look at.
- **Later Sessions:** the same playlist is appended to. osu-fy never removes.
- **Other services:** Apple Music and YouTube Music were named as ideas, not
  commitments. Whether their APIs allow it is unchecked.
- **The old tool (`OsuSongParser`):** nothing is carried over unless the
  owner says so. Exception: its lazer reader (walk `files/`, parse every
  file as `.osu`, keep those with metadata; no realm) worked reliably and
  fast; the owner wants it looked at. Private repo `Daveyy1/OsuSongParser`.
  Its last lazer run: 292 Songs, 154 matched, 6 to review, 132 unmatched;
  many unmatched are on Spotify (Japanese titles, `(TV Size)`, Nightcore).
  "Unoptimised" meant unclean code, not rate limits.
- **Version one (round 3):** one Source end to end: the lazer install, to a
  Spotify Playlist. Stable and the account lists go on the roadmap.
- **Review (rounds 3, 4):** Doubtful matches are decided inside osu-fy.
  osu-fy first lists them all; the Player then adds them all at once or goes
  through them one by one, and can add the remaining ones in one go at any
  point. Unanswered ones wait for the next Session; answers are remembered.
- **Memory (round 4):** kept in the Player's app-data folder. Only Songs new
  since the last Session are searched; a menu option searches the Unmatched
  Songs again. A "no" in the Review stays a no.
- **Duplicates (round 4):** osu-fy reads the Playlist from Spotify on every
  Session and treats it as the truth.
- **Song identity (round 4):** a TV Size or other cut and a different script
  are the same Song (Certain match). An extended mix is Doubtful. For a
  remix or Nightcore map, look for that exact version first; falling back
  to the original is Doubtful, never certain.
- **Deleted maps in lazer (round 4):** accepted as a known limitation,
  because no reliable way exists without a realm reader (checked
  2026-10-14). Lazer removes the files of deleted or replaced Beatmapsets
  and old versions of edited difficulties only when it next starts, so
  osu-fy may find Songs the Player deleted since then.
- **Friends (round 4):** first-Session setup guides the Player to register their
  own Spotify app and paste its Client ID (PKCE, no secret). The repo ships
  no Client ID. The owner has Premium.
- **Stack (rounds 4, 5):** Python 3.13, uv, pytest, ruff, a type checker, a
  small terminal UI library, spotipy 2.26 or newer (it follows Spotify's
  February 2026 endpoints) with its token cache replaced so tokens live in
  the app-data folder, never in the working directory. Spotify sits behind
  one port. Needs an ADR.
- **First Session (round 5):** Certain matches are added as soon as the search
  ends, before the Review, with their count shown.
- **Lazer folder (round 5):** default `%APPDATA%\osu`, follow `storage.ini`
  if the Player moved it, show the path to confirm, ask only if nothing is
  found, remember the answer.
- **Unmatched Songs (round 5):** listed in the terminal and written to a
  file in the app-data folder with the osu! link and a Spotify search link
  per Song; osu-fy prints the path.
- **Failures (round 5):** expired login refreshes silently, else the browser
  opens again; Spotify unreachable stops with a clear message and the next
  Session continues. Rate limits: the old project once got a day-long block, so
  pacing matters. Old pacing: at most 30 requests per sliding 30 s and at
  least 1 s between requests.
- **Pacing (round 6):** keep the old pacing (about 1 request a second) and
  make fewer requests: one search per Song, never again in later Sessions, stop at
  the first Certain match, add in batches of 100. spotipy's silent 429 retry
  is off: a short wait (up to about 2 minutes) shows a countdown and
  continues; a longer one stops, keeps the progress and says until when.
  The search shows a progress bar counting the Songs done, so the app never
  looks frozen. About 10 minutes for a first Session of 300 Songs is fine.
- **Platform (round 6):** Windows first; folder lookups written so macOS and
  Linux are one small issue each later.
- **Install (round 6):** `uv tool install git+https://github.com/Daveyy1/osu-fy`,
  explained in the README. A `.exe` goes on the roadmap.
- **Licence (round 6):** MIT; dependencies must have compatible licences.
- **Non-goals (round 6), all confirmed:** never removes or reorders Tracks
  or changes the osu! install; no GUI or web app, no other Streaming service,
  no account lists, stable or collections in version one; no downloading or
  playing of music; no several Players or Playlists per Windows account; no
  telemetry, no server of its own; English only.
- **Players (round 5):** one Player and one Playlist per Windows user
  account in version one.
- **Playlist (round 3):** the Player names it in the first Session; private by
  default.
- **Non-negotiables (round 3), all confirmed:** never delete or reorder in
  a Playlist; only read the osu! install; keys and tokens never printed,
  logged or committed; nothing about the Player goes anywhere but osu! and
  the Streaming service; a Track is never added twice, also across Sessions.
- **Facts checked 2026-10-14:** Spotify development mode allows 5 users per
  app and the app owner needs Premium; search returns at most 10 results;
  new endpoints `POST /me/playlists` and `/playlists/{id}/items`; PKCE with
  a `http://127.0.0.1` redirect. osu! account lists need only an app token
  and no collections endpoint exists. No Python reader for lazer's realm.

- **Matching quality (round 7):** measured on a fixed set: the old run's
  154 matched Songs must keep the same Track; the five Song-identity cases
  are rule tests; about 10 old Unmatched Songs that are on Spotify, with a
  Track the assistant proposes and the owner confirms y/n. Tests run on
  recorded Spotify answers. Success: no wrong Certain match on the set, all
  154 kept, fewer Unmatched Songs than 132 on the same library. Assumed: no
  wrong Track known in the old Playlist (owner did not name any).

## ADRs from the interview
Written as ADR-004 (stack), ADR-005 (structure checks), ADR-006 (lazer file
store) and ADR-007 (own Spotify app per Player), all `proposed` until the
owner merges PR #1.

## Open decisions
See `open_threads.md`.

## Watch out
- `Daveyy1/OsuSongParser` (private) has spotipy's `.cache` committed, with
  a Spotify access and refresh token. Told the owner on 2026-10-14; revoking
  the app's access and removing the file is their call.
- `/plan`, `/build`, `/address-review`, `/grill-me`, `/grill-with-docs`,
  `/to-spec` and `/to-tickets` only run when typed.
- Only the owner sets an ADR to `accepted`. On 2026-10-14 the index said
  `accepted` while the ADR files still said `proposed`; keep both in step.
