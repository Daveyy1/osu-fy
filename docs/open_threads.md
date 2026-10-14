# Open threads & ideas

What is **open**: decisions, parked features, ideas, follow-ups. Stories and
their status live in `spec/user_stories.md`; what was built and how lives in the
issues and pull requests on GitHub. Status: 🔲 not started · 🔄 partial · 💡 idea.

Remove an entry when it is done: the pull request is the record.

## Decisions needed
- 🔲 Open questions left to the plans (feature spec, "Further Notes"):
  Playlist deleted in Spotify (US-04); remaster suffix Certain or Doubtful
  (US-05); Doubtful threshold (US-05); `storage.ini` format (US-01).

## Spec pack
- 🔄 Spec pack drafted (vision, persona, constraints, API contracts,
  roadmap, US-01 to US-10, feature spec `spec/features/lazer-to-spotify/`,
  ADR-004 to ADR-007 proposed). Waiting for the owner's review in PR #1.
- 🔲 After PR #1 is merged: a `process/` PR for CI (uv, the baseline
  commands in `spec/constraints.md`) and the command allowlist in
  `.claude/work-settings.json` ("Choosing the stack" in the workflow).
  Check the licence strings of the pip-licenses command there.
- 🔲 Before US-05: the owner confirms about ten missed Songs (y/n) for the
  matching quality set; the assistant proposes the Tracks.

## Features — parked

## Harness
- 💡 A separate GitHub account or a fine-grained token for work sessions, so
  the assistant cannot merge or approve even if it words around the deny
  rules (ADR-003).
- 💡 Turn on Claude Code's sandbox for work sessions where the platform
  supports it (ADR-003).
