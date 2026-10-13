# Open threads & ideas

What is **open**: decisions, parked features, ideas, follow-ups. Stories and
their status live in `spec/user_stories.md`; what was built and how lives in the
issues and pull requests on GitHub. Status: 🔲 not started · 🔄 partial · 💡 idea.

Remove an entry when it is done: the pull request is the record.

## Decisions needed

## Spec pack
- 🔄 Fill `docs/spec/` (`/grill-with-docs`, then `/to-spec`). The interview
  is two rounds in; see `handoff.md`.
- 🔲 Choose the stack: ADR, "Technical baseline" in `spec/constraints.md`,
  CI and the command allowlist ("Choosing the stack" in the workflow).

## Features — parked

## Harness
- 💡 A separate GitHub account or a fine-grained token for work sessions, so
  the assistant cannot merge or approve even if it words around the deny
  rules (ADR-003).
- 💡 Turn on Claude Code's sandbox for work sessions where the platform
  supports it (ADR-003).
