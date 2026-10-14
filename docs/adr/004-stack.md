# ADR-004 — Stack: Python 3.13 with uv, spotipy behind a port

*Status: accepted · Date: 2026-10-14*

## Context
osu-fy is a terminal app for Windows that reads files from the lazer folder,
talks to the Spotify Web API and keeps a little state between Sessions. The
owner reads Python fluently and wrote the first tool in it (uv, spotipy,
rapidfuzz, rich). Lazer's realm database has an official reader only in C#,
but osu-fy does not need it (ADR-006). Spotify changed its API in February
2026 (new playlist endpoints, search limited to 10 results). spotipy 2.26.0
(2026-03-03) followed those changes three weeks after they took effect. Its
default token cache, a `.cache` file in the working folder, is how a refresh
token ended up committed in the first tool's repository.

Options on the table: Python with spotipy; Python with plain HTTP (`httpx`)
to Spotify; C#/.NET, which could read lazer's realm database directly.

## Decision (Y-statement)
In the context of **a small terminal tool the owner reviews line by line**,
facing **the choice of language and of how to talk to Spotify**, we decided
for **Python 3.13 managed with uv; spotipy ≥ 2.26 for Spotify, with its token
cache replaced by one that writes only to osu-fy's app-data folder and its
429 retry switched off; rapidfuzz for similarity; rich and readchar for the
terminal; JSON files in the app-data folder for memory; pytest, ruff,
mypy (strict) and import-linter for checks**. We decided against plain
HTTP, because it is 150 to 200 more lines of login, refresh, paging and
retry code to write and review, and against C#, because the owner reviews
Python faster and the realm database is not needed. This achieves **little
code of our own around Spotify, and a stack the owner reads fluently**. We
accept **waiting for spotipy (or pinning a version) when Spotify changes its
API again, and spotipy's habits we must override (token cache, silent 429
retry)**.

## Assumptions
- spotipy stays maintained and follows Spotify's changes within weeks.
- spotipy's token cache handler and retry settings can be replaced without
  patching spotipy.
- A few hundred to a few thousand Songs fit comfortably in JSON files; one
  Player per Windows user account.
- All chosen libraries keep MIT-compatible licences (checked in CI).

## Revisit if:
- spotipy lags more than a month behind a Spotify API change that breaks
  osu-fy, or stops being maintained: switch the adapter to plain HTTP.
- Memory needs queries JSON cannot serve well (several Players or
  Playlists, tens of thousands of Songs): consider SQLite.
- A Source needs lazer's realm database after all.
- A GUI or web app is specified (it may need a different UI library).
