# osu-fy — the app

The Python project behind the `osu-fy` command. What osu-fy is and how a
Player installs it: the root `README.md`. Every command below runs from the
repository root and needs [uv](https://docs.astral.sh/uv/); uv fetches
Python 3.13 and the locked dependencies by itself.

## Start it

```
uv run --directory app osu-fy
```

It greets you, finds your lazer folder (US-01), reads it with a progress
bar and shows "Found <n> Songs in <m> Beatmapsets" (US-02), logs in to
Spotify (US-03), creates your Playlist or finds it again (US-04), then
waits; `q` (or `Q`, or Ctrl+C) quits at any prompt. Matching Songs and
adding Tracks are not built yet (US-05, US-06).

**Files:** osu-fy remembers the confirmed lazer folder, your Spotify
Client ID and your Playlist's Spotify id in `%APPDATA%\osu-fy\settings.json`, and the Spotify login (access
and refresh token) in `%APPDATA%\osu-fy\spotify-token.json`. It only reads
`%APPDATA%\osu` and the lazer folder, never writes there, and writes nothing
into the folder it was started from.

**Spotify:** you need a Spotify app of your own; osu-fy's setup guide walks
you through it. Its redirect URI must be exactly
`http://127.0.0.1:8765/callback`. osu-fy talks only to `accounts.spotify.com`
and `api.spotify.com`.

**Environment variables:** only Windows' own `%APPDATA%`. No fake adapters:
the fake Spotify (`tests/fake_streaming.py`, and the fake `requests.Session`
in `tests/test_spotify.py`) is used only by the tests.

### Reaching each state of US-01

| State | How |
|-------|-----|
| Fresh start | Rename or delete `%APPDATA%\osu-fy`. |
| Default folder found (US-01.1) | Fresh start, with lazer's data in `%APPDATA%\osu` (it has `files`). |
| Moved folder (US-01.2) | Do not edit lazer's real `storage.ini`: lazer reads it too. Use a stand-in `%APPDATA%` (below) with a file `osu\storage.ini` holding the line `FullPath = D:\some\folder`, where that folder has a `files` folder (an empty one is enough). |
| Nothing found (US-01.3) | Answer `n`, or use an empty stand-in `%APPDATA%`. |
| Remembered folder (US-01.4) | Start osu-fy again after confirming a folder. |
| Remembered folder lost (US-01.5) | Confirm a folder with a typed path, then rename its `files` folder. |
| Unreadable settings | Write `{not json` into `%APPDATA%\osu-fy\settings.json`. |

### Reaching each state of US-02

| State | How |
|-------|-----|
| The sample lazer folder (US-02.1 to US-02.3) | Answer `n` and type the path of `app\tests\sample-lazer`. It shows "Found 8 Songs in 9 Beatmapsets". Afterwards osu-fy remembers it: use a stand-in `%APPDATA%` (below), or a fresh start to go back to your own folder. |
| Your real lazer folder (US-02.4 to US-02.6): its audio, images and skins are skipped quietly | Fresh start, accept the default folder. For US-02.6, run `dir /s /t:w %APPDATA%\osu > before.txt` in `cmd` before and `> after.txt` after, then `fc before.txt after.txt`. |
| Empty lazer folder | Type the path of a folder holding only an empty `files` folder: "Found 0 Songs in 0 Beatmapsets". |

### Reaching each state of US-03

| State | How |
|-------|-----|
| Setup guide (US-03.1) | Fresh start (or delete only the `spotify_client_id` line from `settings.json`), confirm a lazer folder. |
| Not a Client ID (US-03.2) | At "Client ID:", paste anything that is not 32 hexadecimal characters, e.g. `abc`. |
| Browser login (US-03.3) | Paste your app's Client ID. The browser opens on Spotify's login page; agree. |
| Login not completed (US-03.4) | In the browser, click "Cancel" on Spotify's page (refuse), or close the tab and wait 3 minutes, or press `t`, `c` or `q` while osu-fy waits. A wrong Client ID or redirect URI also ends here: Spotify shows an error page and never calls back. |
| Saved login (US-03.5) | Start osu-fy again after a login. |
| Expired login (US-10.3) | Start osu-fy more than an hour after the last login. |
| Refresh refused (US-10.4) | Remove osu-fy's app at <https://www.spotify.com/account/apps/>, then start osu-fy **more than an hour after the last login**. Sooner, Spotify still accepts the saved access token, so osu-fy never refreshes and logs in as usual. Quicker: after removing the app, set `"expires_at"` to `0` in `spotify-token.json`. |
| Tokens only in the token file (US-03.6) | Start osu-fy from an empty folder (`cd` there, run `uv run --project <repo>\app osu-fy`); afterwards the folder is still empty, and `%APPDATA%\osu-fy` holds `settings.json` and `spotify-token.json`. |
| Spotify unreachable (US-03.8) | Disconnect the network, then start osu-fy (with or without a saved login). |
| Port 8765 in use (US-03.8) | Start a second osu-fy while the first waits for the browser. |

### Reaching each state of US-04

osu-fy never deletes a playlist. Delete the test Playlists in Spotify by
hand when you are done.

| State | How |
|-------|-----|
| No Playlist yet (US-04.1) | Delete only the `spotify_playlist_id` line from `settings.json` (or a fresh start), log in. At "Name for your Playlist [osu!fy]:", press Enter or type a name. In Spotify, the Playlist is under "Your Library", marked private. |
| A Playlist from an earlier Session (US-04.2) | Start osu-fy again. To see the renamed case, first rename the Playlist in Spotify. |
| A playlist called `osu!fy` that osu-fy did not create (US-04.3) | Create a playlist named `osu!fy` in Spotify by hand, then do as for US-04.1. |
| Playlist deleted in Spotify (US-04.4) | Delete the Playlist in Spotify, then start osu-fy again. |

A stand-in `%APPDATA%` for one PowerShell window (osu-fy then remembers
nothing in the real one): `mkdir $env:TEMP\roaming; $env:APPDATA =
"$env:TEMP\roaming"`, then start osu-fy as above.

## Check it

The Technical baseline of `docs/spec/constraints.md`; CI runs the same.

| Check | Command |
|-------|---------|
| Tests | `uv run --directory app pytest` |
| Lint | `uv run --directory app ruff check .` |
| Format | `uv run --directory app ruff format --check .` |
| Types | `uv run --directory app mypy` |
| Structure (ADR-005) | `uv run --directory app lint-imports` |
| Licences | `uv run --directory app pip-licenses --from=mixed --partial-match --allow-only="MIT;BSD;Apache;ISC;PSF;Python Software Foundation;MPL 2.0;MPL-2.0"` |

`ruff check --fix .` and `ruff format .` fix most lint and format findings.

## Layout

```
src/osu_fy/
  core/       the domain and the Session; defines the ports (Player, …)
  adapters/   Source and Streaming service adapters (lazer.py, spotify.py)
  ui/         the terminal Player: rich for output, readchar for keys
  __main__.py the osu-fy command; wires adapters and UI into the core
tests/        pytest, one file per module it covers
  sample-lazer/  the sample lazer folder: 9 Beatmapsets, .osu files only
```

The core imports nothing from `adapters/`, `ui/`, spotipy, rich or
readchar, and `adapters/` and `ui/` do not import each other. `lint-imports`
fails the build otherwise.
