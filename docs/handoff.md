# Hand-off note

*The assistant keeps no memory between sessions: only what is written down.
Update this note at the end of every session that leaves work open. Keep it
short. It says where to continue, not what was done: the issues and pull
requests are the record of that.*

## Resume here (the exact next step)
1. The spec, ADR-004 to ADR-007 and the toolchain (PRs #1 to #3) are on
   `main`, and so are the walking skeleton (#4, PR #18), US-01, find the
   lazer folder (#5, PR #20), US-02, read Songs from lazer (#6, PR #22),
   and US-03, connect to Spotify (#7, PR #24): the `StreamingService` port,
   the Spotify adapter (PKCE, tokens in `%APPDATA%\osu-fy\spotify-token.json`)
   and the login step after reading the Songs; and US-04, name and create
   the Playlist (#8, PR #26): a private Playlist, its id in `settings.json`,
   found by that id in later Sessions; and US-05a, search Spotify at a
   safe pace (#9, PR #28): `find_tracks`, every request at least 1 s
   apart, a 429 stops with "Spotify asks us to wait <time>", and the first
   rule (exact artist and title, either script, is Certain); and US-05b,
   matching rules and the quality set (#10, PR #30): cut markers, other
   scripts, versions and covers per US-05, a fuzzy score that is at least
   80 for a Doubtful match (`DOUBTFUL`), and the quality set in the git-ignored `app/tests/recordings/`.
   PR #24 also built US-10.3 and
   US-10.4 for the login only; #15 builds the rest of US-10. #15 also
   builds the refresh at every start that US-03.5 asks for since PR #25:
   the code still refreshes only an expired token. #15 also handles a 403
   or other 4xx from creating or finding the Playlist, which still raises
   a traceback, and a 429 on the token refresh, which opens the browser
   instead of the wait message. Nothing found is kept between Sessions
   yet (US-09). Issues #11 to #16 hold the
   rest of version one, one per ticket, with GitHub's native "blocked by"
   links; `docs/spec/roadmap.md` maps them.
2. Next: in a work session (`claude --settings .claude/work-settings.json`),
   `/plan 11` (add Certain matches, US-06), following the roadmap. Then
   the owner sets `plan-approved`, and `/build`.
3. What PR #30 left for later issues:
   - On the owner's library, 52 Doubtful matches go to the Review (#12).
     Some are other versions or releases the old tool took as matched.
     `RADWIMPS – Zen Zen Zense (movie ver.)` gets `Zenzenzense - English
     Version` as a Doubtful match, so the Review offers a wrong version
     there; `Linked Horizon – Shinzou o Sasageyo! [TV Size]` stays
     Unmatched (Spotify's search misses the other romanisation).
   - The Doubtful threshold of 80 has no margin: `Ke$ha → Kesha –
     Backstabber` and `Vickeblanka → VK Blanka – Black Rover` score
     exactly 80. A rule change that moves either needs the quality set
     run again.
   - The quality set and the sample replay run only where
     `tests/recordings/` exists (the owner's machine), not in CI, and the
     recordings go stale as Spotify's catalogue moves.
   - Of the 104 Certain matches in the owner's real Session, only the 90
     in the quality set are known to be right. #11 adds them to the
     Playlist, so its check in the running app should look at the rest.

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
