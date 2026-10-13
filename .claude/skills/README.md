# Bundled skills

Skills in this folder load automatically for anyone using Claude Code in this repo.

| Skill | Invoke | Use it for |
|-------|--------|------------|
| `grill-with-docs` | `/grill-with-docs` | Discover: the interview that builds the spec, writing `CONTEXT.md` and ADRs as it goes |
| `grill-me` | `/grill-me` | The same interview without writing files: stress-test one spec or decision |
| `to-spec` | `/to-spec` | Specify: turn the discussion into `docs/spec/features/<feature>/spec.md` |
| `to-tickets` | `/to-tickets` | Specify: cut a feature spec into thin end-to-end tickets, one GitHub issue each |
| `tdd` | `/tdd`, or automatic | Build: test-first building |
| `grilling`, `domain-modeling`, `codebase-design` | automatic | Building blocks the skills above call (`tdd` uses `codebase-design`) |

The commands `/plan`, `/build`, `/address-review` and `/sensor` live in
`../commands/`.

## Source and local changes

All skills are copied from [mattpocock/skills](https://github.com/mattpocock/skills),
commit `c55ee46` (2026-09-18), MIT license (`LICENSE-mattpocock-skills`).
Local changes:

- The OpenAI-specific `agents/` subfolders are left out.
- `domain-modeling/ADR-FORMAT.md` has a project note on top: ADRs use
  `docs/templates/adr.md`, numbered `001-`.
- Where the skills expect a configured issue tracker, `CLAUDE.md` (section
  *Agent skills*) tells them to use `docs/spec/features/`. The skill
  `setup-matt-pocock-skills` is not needed and not included.

To update, copy the new upstream version over the folder and re-apply these changes.
