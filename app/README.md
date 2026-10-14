# osu-fy — the app

The Python project behind the `osu-fy` command. What osu-fy is and how a
Player installs it: the root `README.md`. Every command below runs from the
repository root and needs [uv](https://docs.astral.sh/uv/); uv fetches
Python 3.13 and the locked dependencies by itself.

## Start it

```
uv run --directory app osu-fy
```

It greets you and waits; `q` (or `Q`, or Ctrl+C) quits. That is all it does
so far: no Session step is built yet.

No environment variables, no fake adapters, and no files written.

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
  adapters/   Source and Streaming service adapters (empty so far)
  ui/         the terminal Player: rich for output, readchar for keys
  __main__.py the osu-fy command; wires adapters and UI into the core
tests/        pytest, one file per module it covers
```

The core imports nothing from `adapters/`, `ui/`, spotipy, rich or
readchar, and `adapters/` and `ui/` do not import each other. `lint-imports`
fails the build otherwise.
