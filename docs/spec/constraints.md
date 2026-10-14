# Technical & organizational constraints

*Companion to the persona: the persona holds **user-anchored** non-negotiables; this
file holds the constraints that come from the organization, the law, and engineering
policy. Like non-negotiables, each should become **executable** where possible — a test,
a CI check, a lint rule; what cannot be executed goes on the review checklist instead
of remaining prose intention.*

## Dependencies & licensing
- The project is licensed **MIT**.
- Every runtime and development dependency has a licence compatible with
  MIT use: MIT, BSD, Apache 2.0, ISC, PSF, or MPL 2.0 (unmodified, as a
  dependency only). No GPL, LGPL or AGPL. Checked by the licence command in
  the baseline below.
- Few dependencies: each new one is named in the plan of the issue that
  adds it, with its licence and the reason. Agreed so far: spotipy,
  rapidfuzz, rich, readchar (runtime); pytest, ruff, mypy, import-linter,
  pip-licenses (development). See ADR-004.
- Spotify sits behind one port, so spotipy can be replaced by plain HTTP in
  one module (ADR-004, ADR-005).

## Code & style
- PEP 8 as enforced by `ruff check` and `ruff format`; type hints on every
  public function, checked by `mypy --strict`. CI fails on any finding.
- The core (domain and Session steps) imports nothing from the terminal
  UI, the adapters, spotipy, rich or readchar. Enforced by import-linter
  contracts (ADR-005).
- Glossary words from `CONTEXT.md` in code, tests and terminal text: Song,
  Beatmapset, Track, Playlist, Certain match, Doubtful match, Unmatched
  Song, Review, Session, Player.

## Privacy, security, compliance
- No server and no telemetry. The only hosts contacted in version one are
  `accounts.spotify.com` and `api.spotify.com` (N4). An automated test
  asserts that the Spotify adapter is configured for these hosts only.
- Spotify login is Authorization Code with PKCE: there is no client secret
  anywhere. The Client ID is not secret but is never shipped in the
  repository (ADR-007).
- Tokens live only in osu-fy's token file in the app-data folder
  (`%APPDATA%\osu-fy` on Windows), protected by the Windows user profile's
  permissions. spotipy's default `.cache` file in the working folder is
  never used (N3). An automated test runs a login with a fake token and
  asserts that no file appears in the working folder and that the token
  text appears in no output.
- `.gitignore` excludes `.cache`, `.cache-*`, `.env` and the app-data
  folder's file names; the secret scan in CI runs on every PR.
- The osu! install is opened read only (N2).
- **Test data in the repository.** The repository is public. The matching
  quality set and the recorded Spotify answers hold only what the tests
  need: artist, title, Beatmapset id, Spotify Track id, and for recordings
  the Track fields of the port (title, artists, album, length). No playlist
  ids, no account or profile data, no tokens, no request headers. Whether
  Spotify's developer terms allow committing recorded responses is checked
  in US-05's plan; if they do not, the recordings and the quality set move
  to a git-ignored local folder and the tests that need them are skipped
  when it is absent.
- GDPR: osu-fy processes the Player's own data on the Player's own machine
  and sends it only to Spotify at the Player's request. No further duties
  for a tool without a server.

## Operational
- Runs on the Player's own Windows PC, installed with
  `uv tool install "git+https://github.com/Daveyy1/osu-fy#subdirectory=app"`
  and started with `osu-fy`. Windows first; finding the lazer folder and the
  app-data folder is written so macOS and Linux are one small issue each.
- No backups: everything osu-fy remembers lives in the app-data folder. If
  it is lost, the next Session behaves like a first Session, and N5 still
  holds because the Playlist is read from Spotify.
- Spotify development mode: an app has at most 5 users and its owner needs
  Premium (checked 2026-10-14). Each Player registers their own app
  (ADR-007).
- Requests to Spotify are paced at about one a second: at most 30 in any
  30 seconds and at least 1 second apart. osu-fy never tries to find a
  faster rate.

## Classify the system (sets the risk posture)
- **Criticality: low** (Meyer class C). The worst realistic failure is a
  wrong Track in a private Playlist or a lost hour of matching; no money,
  health or other people's data is involved. The two exceptions that get
  full rigour are the non-negotiables: tokens (N3) and never destroying the
  Player's data (N1, N2).
- **Project dimensions:** one developer and an AI assistant; small code
  base; light ceremony: an issue, a plan, a reviewed PR per story.

## Technical baseline (filled when the stack is chosen)

*The harness does not fix a stack. Choose it during Discover, record it in an
ADR, and fill this section in the same `spec/` PR; `/build` holds every work
item to it. The matching `process/` PR adds the toolchain to
`.github/workflows/ci.yml` and the build commands to
`.claude/work-settings.json` (see "Choosing the stack" in
`docs/process/workflow.md`).*

The Python project lives in `app/` (its own `pyproject.toml` and `uv.lock`).
All commands run from the repository root.

- **Stack:** Python 3.13, uv, spotipy ≥ 2.26, rapidfuzz, rich, readchar;
  pytest, ruff, mypy, import-linter, pip-licenses (ADR-004, ADR-005).
- **Run every test:** `uv run --directory app pytest`. Green at the end of
  every issue.
- **End-to-end tests:** none automated. Real Spotify and the real lazer
  folder are checked by hand in the running app; each story says how.
- **Start the app:** `uv run --directory app osu-fy`, then follow the
  prompts in the terminal.
- **Structure checks:** `uv run --directory app lint-imports` (import-linter
  contracts, ADR-005).
- **Mutation testing:** none for now.
- **Dependency licences:** `uv run --directory app pip-licenses
  --from=mixed --partial-match --allow-only="MIT;BSD;Apache;ISC;PSF;Python
  Software Foundation;MPL 2.0;MPL-2.0"`. Partial match, because packages
  name the same licence differently (`MIT` and `MIT License`,
  `BSD-3-Clause` and `BSD License`, `PSF-2.0`). Checked 2026-10-14 against
  the agreed dependencies: all pass, and leaving MPL out fails on
  `certifi`.
- **Lint and types:** `uv run --directory app ruff check .`,
  `uv run --directory app ruff format --check .`,
  `uv run --directory app mypy`, no errors.
