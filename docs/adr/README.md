# Architecture decision records

One file per significant decision, numbered (`001-<slug>.md`, `002-…`), from
`../templates/adr.md`. **Process** decisions shape how the work is done.
**Product** decisions are part of the spec pack: every issue follows
them.

| ADR | Decision | Kind | Status |
|-----|----------|------|--------|
| [001](001-reviewed-generation.md) | Reviewed generation: a human approves the plan and the code | process | accepted |
| [002](002-branch-and-work-model.md) | Branch and work model: issue, branch, pull request | process | accepted |
| [003](003-work-permissions.md) | Work permissions: auto mode plus a versioned allowlist | process | accepted |
| [004](004-stack.md) | Stack: Python 3.13 with uv, spotipy behind a port | product | proposed |
| [005](005-structure-checks.md) | Structure: a core with ports, checked by the build | product | proposed |
| [006](006-read-lazer-file-store.md) | Read lazer through its file store, not its realm database | product | proposed |
| [007](007-own-spotify-app-per-player.md) | Each Player registers their own Spotify app | product | proposed |

The harness ships only process decisions. A project's first product ADRs
record its stack and how its structure is checked ("Choosing the stack" in
`../process/workflow.md`).

Y-statement format, plus two fields that earn their keep with an AI assistant:

- **Assumptions** — what must stay true. With cheap generation, decisions are made
  fast and forgotten faster; an unrecorded assumption decays silently into a defect.
- **Revisit if:** — a concrete tripwire. Check every new requirement against the
  triggers; when one fires, the strain is *anticipated*, not surprising — re-decide
  and re-record on the spot.

A decision is **done** when Y-statement + assumptions + revisit trigger are recorded.
An ADR is **accepted** when the human merges a PR that sets its status to `accepted`.
Never let the assistant silently contradict an accepted ADR: it either complies or
proposes superseding it. Keep this table current when an ADR is added or its
status changes.
