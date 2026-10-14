# Feature spec — From lazer to a Spotify Playlist

*Version one of osu-fy. Built story by story, US-01 to US-10
(`../../user_stories.md`), one issue and one reviewed pull request each.
Words as in `CONTEXT.md`.*

## Problem Statement

A Player knows hundreds of Songs from osu!lazer and wants to hear them on
Spotify. Searching for each one by hand takes hours, and it is error-prone:
titles are in Japanese or romanised, maps are cut to TV Size, and many are
remixes or Nightcore edits that Spotify lists differently or not at all.

The owner's first tool did this job, but its code was hard to extend and its
interface was rough. It left 132 of 292 Songs Unmatched, and many of those
are on Spotify. Its Playlist could only be filled from export files the
Player had to pick by hand. It also committed a Spotify refresh token to its
repository.

## Solution

osu-fy is a guided terminal app. In a Session it:
1. finds the lazer folder and reads the Beatmapsets installed there,
   without changing anything;
2. turns them into Songs, so each piece of music is searched once;
3. searches Spotify at a safe pace, with a visible progress bar, and sorts
   the results into Certain matches, Doubtful matches and Unmatched Songs;
4. appends the Certain matches to the Player's private Playlist straight
   away, never twice;
5. shows all Doubtful matches in one table, and the Player adds them all,
   goes through them one key press at a time, or leaves them for later;
6. lists the Unmatched Songs, in the terminal and in a file with links that
   make adding them by hand one click.

osu-fy remembers what it found and what the Player decided, so a later
Session only searches Songs that are new. The first Session also guides the
Player through registering their own Spotify app and logging in.

## User Stories

Setup and lazer
1. As a Player, I want osu-fy to find my lazer folder by itself, so that I do
   not need to know where lazer keeps its data.
2. As a Player who moved lazer's data, I want osu-fy to follow lazer's own
   record of the new location, so that it still finds my maps.
3. As a Player, I want to confirm or correct the folder osu-fy found, so
   that it never reads the wrong place.
4. As a Player, I want osu-fy to remember the folder, so that later Sessions
   do not ask again.
5. As a Player, I want two Beatmapsets of the same music (for example a full
   version and a Cut Ver.) treated as one Song, so that it is searched and
   added once.
6. As a Player, I want a Nightcore or remix map treated as its own Song, so
   that osu-fy looks for that exact version.
7. As a Player, I want osu-fy to ignore files that are not maps, and maps
   without artist or title, so that a strange file does not stop it.
8. As a Player, I want to see progress while osu-fy reads the lazer folder,
   so that I know it has not frozen.
9. As a Player, I want osu-fy never to change anything in my osu! install,
   so that my game is safe.

Spotify connection
10. As a Player, I want a step-by-step guide to registering my own Spotify
    app, so that I can set up osu-fy without help.
11. As a Player, I want osu-fy to tell me immediately when what I pasted is
    not a Client ID, so that I do not get a confusing error later.
12. As a Player, I want to log in through my browser, so that I never give
    my Spotify password to osu-fy.
13. As a Player, I want osu-fy to keep my login, so that later Sessions do
    not open the browser.
14. As a Player, I want my tokens kept only in osu-fy's own folder, so that
    they never end up in a project folder or a repository.
15. As a Player, I want osu-fy to talk to nothing but Spotify, so that
    nothing about me goes anywhere else.
16. As a Player whose login has expired, I want osu-fy to renew it silently,
    or to send me to the browser if renewing fails, so that the Session goes
    on.

Playlist
17. As a Player, I want to name my Playlist once, with `osu!fy` suggested,
    so that I recognise it in Spotify.
18. As a Player, I want the Playlist private, so that hundreds of Tracks do
    not appear on my profile unless I choose so.
19. As a Player, I want osu-fy to keep using the same Playlist even if I
    rename it, so that everything stays in one place.
20. As a Player, I want osu-fy never to touch my other playlists, even one
    with the same name, so that nothing of mine is changed by mistake.

Matching
21. As a Player, I want a TV Size or other cut matched to the full Track,
    so that I hear the whole Song.
22. As a Player, I want artist and title in either script (original or
    romanised) to count, so that Japanese Songs are found.
23. As a Player, I want an exact match to always be Certain, so that it is
    not sent to the Review for no reason.
24. As a Player, I want an extended mix to be Doubtful, so that I decide
    whether I want that cut.
25. As a Player, I want the exact remix or Nightcore version found if it is
    on Spotify, and the original only offered as Doubtful, so that I get
    what I played whenever possible.
26. As a Player, I want a cover by another artist never to be Certain, so
    that no wrong Track is added without my say.
27. As a Player, I want Songs with nothing plausible on Spotify reported as
    Unmatched, so that I know what is missing.
28. As a Player, I want a progress bar showing Songs searched out of the
    total, with the elapsed time, so that a 10-minute search never looks
    frozen.
29. As a Player, I want osu-fy to search at a safe pace, so that Spotify
    does not block me for a day.
30. As a Player, I want a summary of Certain matches, Doubtful matches and
    Unmatched Songs, so that I know what comes next.

Filling the Playlist
31. As a Player, I want Certain matches added without a question, so that I
    only spend time where I am needed.
32. As a Player, I want Tracks already in the Playlist skipped, including
    ones I added by hand, so that nothing is in it twice.
33. As a Player, I want Tracks I or osu-fy added before kept in their
    place, so that osu-fy only ever appends.
34. As a Player, I want to see every Doubtful match in one table before
    deciding, so that I know what "add all" would add.
35. As a Player, I want to add all Doubtful matches at once, so that a list
    I trust costs one key press.
36. As a Player, I want to go through Doubtful matches one key press at a
    time, so that a long list is quick.
37. As a Player going through them one by one, I want to add all remaining
    ones at once, so that I can stop deciding once I trust the rest.
38. As a Player, I want to skip a Doubtful match or stop the Review, so that
    those wait for a later Session.
39. As a Player, I want to leave the whole Review for later, so that a
    Session never forces me to decide now.
40. As a Player, I want the Unmatched Songs listed at the end and saved to a
    file, so that I can work through them later.
41. As a Player, I want each Unmatched Song to have its osu! link and a
    Spotify search link, so that adding it by hand is one click.

Later Sessions
42. As a Player, I want a later Session to search only new Songs, so that it
    takes seconds, not minutes.
43. As a Player, I want a "no" in the Review to stay a no, so that I am not
    asked again.
44. As a Player, I want skipped Doubtful matches shown again next time, so
    that nothing is lost.
45. As a Player, I want a Session that stopped halfway to continue where it
    stopped, so that no search is wasted.
46. As a Player, I want to search the Unmatched Songs again when I choose,
    so that Songs that arrive on Spotify later can still be found.
47. As a Player, I want osu-fy's memory to survive a reinstall, so that an
    update does not start from zero.

Failures
48. As a Player, I want a short wait requested by Spotify shown as a
    countdown, after which osu-fy continues, so that I see what is happening.
49. As a Player, I want a long wait requested by Spotify to stop the Session
    and tell me the local time to try again, so that I do not sit in front
    of a frozen screen.
50. As a Player, I want a clear message without a traceback when Spotify
    cannot be reached, so that I know it is not my fault and nothing is lost.

## Implementation Decisions

**Modules.** Four, in two layers (ADR-005):
- **Core** (deep): the domain and the Session steps. It holds the Song
  identity rules, the matching rules, the memory between Sessions, and one
  public operation per Session step: find the lazer folder, read Songs,
  connect, ensure the Playlist, match Songs, add Certain matches, Review,
  list Unmatched Songs, plus the Session that strings them together. It
  defines the ports it needs and imports nothing from the other modules or
  from spotipy, rich or readchar. Each story adds or extends one operation;
  the Session grows with them.
- **Lazer Source adapter:** finds the lazer folder (default `%APPDATA%\osu`,
  then lazer's `storage.ini`) and reads Beatmapsets by walking lazer's file
  store: every file whose content starts like a `.osu` file is read for its
  General and Metadata sections; everything else is skipped. No realm
  database access (ADR-006). Files are opened read only (N2).
- **Spotify adapter:** implements the Streaming service port with spotipy
  ≥ 2.26 (ADR-004). It owns: PKCE login with the redirect URI
  `http://127.0.0.1:8765/callback`; a custom token cache in the app-data
  folder; pacing (at most 30 requests in any 30 seconds, at least 1 second
  apart); spotipy's 429 retry switched off and 429 handled as in
  `../../api_contracts.md`; token refresh; batches of 100.
- **Terminal UI:** implements the Player port with rich (tables, progress
  bars, countdowns) and readchar (single key presses). Starts with the
  `osu-fy` command.

**Ports** (defined in the core):
- **Source:** "the lazer folder candidates" and "the Beatmapsets in this
  folder", with a progress callback.
- **Streaming service:** `log_in`, `find_tracks`, `create_playlist`,
  `tracks_in_playlist`, `append_tracks`, exactly as in
  `../../api_contracts.md`. No remove or reorder operation exists (N1).
- **Player:** every question osu-fy asks (confirm folder, enter a path,
  Client ID, Playlist name, Review choices, the menu of a later Session) and
  every piece of progress or result it shows. The core never prints.

**Domain shapes:**
- **Beatmapset:** online id (may be missing), artist, artist in original
  script, title, title in original script.
- **Song:** a Song key, the display artist and title, both scripts, and the
  Beatmapsets that belong to it. The Song key is artist and title after
  case folding, Unicode NFKC normalisation (full-width to normal width),
  collapsing spaces and removing cut markers; version markers stay.
- **Track:** Spotify id, title, artists, album, length.
- **Match:** a Song, a Track, and whether it is Certain or Doubtful.
- **Memory:** for each Song key: searched or not, the Match found, or
  Unmatched, and the Player's answer for a Doubtful match (yes, no, or none
  yet); plus the lazer folder, the Client ID and the Playlist id.

**Matching rules:**
- Search order for a Song: the romanised artist and title; then the
  original script if different; for a remix or Nightcore Song, the base
  title without the version marker last. Stop at the first Certain match.
  One to three searches per Song.
- **Certain:** one of the Track's artists equals the Song's artist in either
  script (credits after `feat.`, `ft.`, `&` or `x` may be split across the
  Track's artists), and the Track's title equals the Song's title after
  removing cut markers on both sides (including Spotify's `- TV Size`
  style suffixes).
- **Doubtful:** the same artist and the base title with an extra version
  (extended mix, other mix), the original for a remix or Nightcore Song, or
  a close but not equal artist and title by a similarity score (rapidfuzz).
  The threshold is fixed in US-05's plan from the quality set.
- **Unmatched:** nothing reaches the Doubtful threshold.
- A Track by a different artist is never Certain.

**Storage:** JSON files in the app-data folder (`%APPDATA%\osu-fy`):
settings (lazer folder, Client ID, Playlist id), memory (per Song key),
the token file, and the Unmatched Songs CSV. Written whole and replaced
atomically, so a crash never leaves half a file. Saved after every Song
searched, so a stop loses at most one Song.

**Duplicates:** before adding, osu-fy reads the Playlist from Spotify and
skips every Track already there (N5). Its memory is never trusted for this.

**Packaging:** the Python project lives in `app/`; installed with
`uv tool install` from the repository's `app` subdirectory; command
`osu-fy`.

## Testing Decisions

**What a good test is here:** it drives a public operation of the core and
asserts what the Player would see or what would be in Spotify: Tracks in the
(fake) Playlist and their order, the questions asked, the lines shown, the
Unmatched Songs file, what a second Session does. It does not assert how the
core does it. Each test name quotes its criterion ID (`US-05.4`).

**Seams:**
1. **The core's public operations**, the main seam. Given a lazer folder (a
   temporary copy of the sample lazer folder), an app-data folder (a
   temporary folder), the fake Streaming service and a scripted Player that
   answers from a list. Almost every criterion is tested here, including
   the matching quality set and every non-negotiable that the core can
   break (N1, N2 on the sample folder, N5).
2. **The Spotify adapter**, against recorded HTTP responses and a fake
   clock: endpoints and bodies, pacing (US-05.9), 429 handling (US-05.11,
   US-10.1, US-10.2), refresh (US-10.3), token file location and no token
   in output (US-03.6), allowed hosts (US-03.7). No test waits in real
   time.
3. **The terminal UI**, thin: key mapping in the Review (US-07.3) and that
   the Player port's questions reach the screen. Everything else in the UI
   is checked by hand.

**Plus structural tests:** import-linter contracts (core imports no
adapter, UI or third-party UI/Spotify library), and a test that the
Streaming service port has no remove or reorder operation (N1).

**Recorded answers:** real Spotify search results for the sample Songs and
the quality set, saved once through the real adapter by a small recording
command and stored next to the tests. The fake fails loudly on a query it
has no recording for.

**Where mocks could hide failures:** Spotify's real ranking and catalogue
(recordings go stale), the real browser login, Spotify's real rate limiting,
the real lazer folder and `storage.ini`, Windows terminal rendering of
Japanese text and progress bars. Each story's criteria include a check by
hand in the running app for these.

**Prior art:** none in this repository yet. The old `OsuSongParser` has no
tests. Its last lazer run's exports provide the 154 matched Songs for the
quality set.

## Out of Scope

- osu! stable, the osu! account lists and collections as Sources.
- Streaming services other than Spotify.
- macOS and Linux (lazer and app-data folders).
- A GUI, a web app, a downloadable `.exe`.
- Removing, replacing or reordering Tracks; choosing an existing playlist.
- Several Players or Playlists per Windows user account.
- Downloading or playing music, or reading the audio files.
- Telemetry, a server, any lookup service other than Spotify.
- Languages other than English.
- Undoing a "no" from the Review inside osu-fy.
- Telling maps deleted in lazer apart before lazer has removed their files
  (known limitation, ADR-006).

## Further Notes

**Open questions for the plans** (the spec does not decide them; the plan
of the named story asks the owner):
- US-04: what osu-fy does when the Player deleted the Playlist in Spotify.
  (Spotify keeps a "deleted" playlist and only unfollows it, so appending
  may still work but nobody sees it.) Recommendation: detect it and offer
  to create a new Playlist.
- US-05: is a `- Remastered` or year-remaster suffix Certain or Doubtful?
  Recommendation: Certain, as it is the same recording.
- US-05: the similarity threshold for Doubtful, fixed from the quality set.
- US-01: the exact format of lazer's `storage.ini`, checked against lazer's
  source.

**Facts this spec rests on** (checked 2026-10-14, see `../../../handoff.md`):
Spotify development mode (5 users, owner needs Premium), the February 2026
endpoints, search limit 10; spotipy 2.26 follows them; lazer removes
deleted maps' files only when it next starts; no maintained Python reader
for lazer's realm database.

**Choices the assistant made while writing this spec** (not discussed in the
interview; change them in review): redirect port 8765; asking for the
`playlist-modify-public` scope; one retry after 5 s and a 10 s timeout for
network errors; stopping on 403; the 3-minute login timeout; exactly 120 s
as the line between a countdown and a stop; the Unmatched Songs file as UTF-8 CSV with
BOM holding all current Unmatched Songs; the later-Session menu keys; JSON
for storage; rich and readchar for the terminal; mypy and import-linter.
