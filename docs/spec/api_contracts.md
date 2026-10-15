# API contracts

*One section per external API the app talks to. Each API
sits behind a **port** (the interface the app calls) and is reached through an
**adapter** (the code that calls the real service). Claude builds from this
file, so name the exact operations and data it needs.*

## Spotify Web API

- **Purpose in the app:** find the Track for each Song, create the Playlist,
  read what is in it, and append Tracks to it.
- **Access today:** available. Each Player registers their own app in
  development mode (ADR-007); the owner has Premium. Facts checked
  2026-10-14.
- **Docs:** <https://developer.spotify.com/documentation/web-api>;
  February 2026 changes:
  <https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide>
- **Auth:** Authorization Code with PKCE, no client secret.
  - The Player's Client ID is entered in the guided setup and stored in
    osu-fy's settings in the app-data folder (`%APPDATA%\osu-fy`), not in
    an environment variable: a Player should not have to edit files.
  - Redirect URI: `http://127.0.0.1:8765/callback`. The Player registers
    exactly this in their app. `localhost` is not accepted by Spotify;
    plain `http` is allowed only for loopback addresses.
  - Scopes: `playlist-read-private`, `playlist-modify-private`,
    `playlist-modify-public`. The last one is needed only if the Player
    makes the Playlist public later; without it, appending would fail.
  - Tokens are kept by a custom spotipy cache handler in osu-fy's token
    file in the app-data folder; never spotipy's default `.cache` (N3).
    Tokens never appear in output, logs or the repository.
- **Port (what the app needs, in domain terms):** the Streaming service
  port has exactly these operations. It has no operation that removes or
  reorders (N1).
  - `log_in(client_id, keep_waiting) → Player name`: completes the login,
    opening the browser only when no usable token is stored. While it
    waits for the browser it calls `keep_waiting(login_url)` about once a
    second (`login_url` is set only when no browser could be opened) and
    gives up when that returns false or after 3 minutes.
  - `find_tracks(artist, title) → list[Track]`: at most 10 candidate
    Tracks for one query; each Track has id, title, artists, album and
    length.
  - `create_playlist(name) → Playlist`: creates a private Playlist on the
    Player's account and returns its id, name and link.
  - `tracks_in_playlist(playlist) → set[Track id]`: every Track already in
    the Playlist, whoever added it.
  - `append_tracks(playlist, tracks)`: appends at the end, at most 100
    per request.
- **Calls behind it:**
  - `GET /v1/search?type=track&limit=10&q=track:"<title>" artist:"<artist>"`.
    `limit` is at most 10 since February 2026. Whether the `track:` and
    `artist:` filters behave as before was not confirmed; the first
    matching issue checks it against the real API.
  - `POST /v1/me/playlists` with `{"name", "public": false, "description"}`.
    `POST /v1/users/{id}/playlists` no longer exists for new apps.
  - `GET /v1/playlists/{id}/items?limit=100&offset=…&fields=items(track(id)),next`.
  - `POST /v1/playlists/{id}/items` with `{"uris": [...]}`, at most 100
    items per call. The old `/tracks` path was renamed.
  - `GET /v1/me` for the display name after login.
  - Login: `https://accounts.spotify.com/authorize` and
    `https://accounts.spotify.com/api/token`.
  - spotipy ≥ 2.26 (2026-03-03) uses these endpoints:
    `search`, `current_user_playlist_create`, `playlist_items`,
    `playlist_add_items`, `current_user`. Do not use the deprecated
    `user_playlist_create`.
- **Failure behaviour:**
  - **429 Too Many Requests:** spotipy's own retry for 429 is switched off,
    so it never sleeps silently. If `Retry-After` is at most 120 seconds,
    osu-fy shows a countdown and continues. If it is longer, the Session
    stops, keeps everything found so far, and tells the Player the local
    time from which to try again.
  - **401 (expired token):** refresh silently. If the refresh fails (for
    example the Player removed osu-fy's access), open the browser to log in
    again, then continue.
  - **403 on the Playlist:** stop with a message naming the Playlist and
    the likely cause (not the Player's Playlist, or scope missing).
  - **Network error, timeout (10 s) or 5xx:** one retry after 5 seconds,
    then stop with "Can't reach Spotify. Everything found so far is kept;
    try again later." No traceback is shown.
- **Fake adapter:** used only in tests, never in the running app. It holds
  Playlists in memory, enforces "append only" and the 100-per-request limit,
  and answers `find_tracks` from **recorded answers**: real search results
  saved once from the real API, stored next to the tests, keyed by query.
  A query with no recording fails the test loudly rather than returning
  nothing. Recordings are refreshed by hand with a small recording command
  when the real catalogue has moved on.
- **Limits & cost:**
  - Development mode: at most 5 users per app, added by email in the
    dashboard. The app owner needs Premium; the app stops working if it
    lapses. Extended quota needs a registered business with at least 250k
    monthly active users, so it is out of reach.
  - The rate limit is not published. Spotify counts requests in a rolling
    30-second window. osu-fy keeps to at most 30 requests in any 30 seconds
    and at least 1 second between requests. A Song costs one to three
    searches, so about 300 Songs take about 10 minutes the first time.
  - Free of charge.

## osu! API v2 (roadmap, not used in version one)

- **Purpose later:** the "account lists" Source: favourite, most_played,
  ranked, loved, graveyard, guest, nominated and pending Beatmapsets
  (`GET /api/v2/users/{user}/beatmapsets/{type}`, paged with `limit` and
  `offset`).
- **Auth later:** a client-credentials token (scope `public`) can read any
  user's lists, no Player login needed. Requests at or below 60 a minute.
- **Not available:** collections. They exist only on the Player's computer.
- When this Source is specified, it gets a full section here and N4 is
  extended to `osu.ppy.sh`.
