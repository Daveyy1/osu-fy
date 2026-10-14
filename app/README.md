# osu-fy — the app

The Python project behind the `osu-fy` command. What osu-fy is and how a
Player installs it: the root `README.md`. Every command below runs from the
repository root and needs [uv](https://docs.astral.sh/uv/); uv fetches
Python 3.13 and the locked dependencies by itself.

## Start it

```
uv run --directory app osu-fy
```

It greets you, finds your lazer folder (US-01), shows "Reading lazer folder
<path>" and waits; `q` (or `Q`, or Ctrl+C) quits at any prompt. Reading the
folder is not built yet (US-02).

**Files:** osu-fy remembers the confirmed lazer folder in
`%APPDATA%\osu-fy\settings.json`. It only reads `%APPDATA%\osu` and the lazer
folder, never writes there.

**Environment variables:** only Windows' own `%APPDATA%`. No fake adapters.

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
  adapters/   Source and Streaming service adapters (lazer.py so far)
  ui/         the terminal Player: rich for output, readchar for keys
  __main__.py the osu-fy command; wires adapters and UI into the core
tests/        pytest, one file per module it covers
```

The core imports nothing from `adapters/`, `ui/`, spotipy, rich or
readchar, and `adapters/` and `ui/` do not import each other. `lint-imports`
fails the build otherwise.
