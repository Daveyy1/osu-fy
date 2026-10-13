# AI code harness

A starting point for projects where an AI assistant writes most of the code
and **a human engineer approves the plan before it is built and reviews the
code before it is merged**.

Specs drive the work, and the work is tracked the usual GitHub way: an
issue, a branch, a pull request.

```
spec PR ──► issue ──► /plan N ──► you answer, label plan-approved ──► /build ──► draft pull request
                                                                                      │
                               merge ◄── you check the app ◄── you review ◄──────────┘
                                                                   │  ▲
                                                                   ▼  │
                                                     /address-review, or you edit
```

**Start here:** [`docs/process/workflow.md`](docs/process/workflow.md) (how it
works) · [`docs/adr/001-reviewed-generation.md`](docs/adr/001-reviewed-generation.md)
(why) · [`docs/handoff.md`](docs/handoff.md) (the next step).

## Using it for a project

This repo is a GitHub template: each project gets its own copy and changes
it freely.

1. On GitHub choose "Use this template", then clone the new repository.
2. Protect `main` and create the approval label. A template passes on
   neither, so run this once per repository:
   ```
   gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" --input .github/branch-protection.json
   gh label create plan-approved --description "The human approved the plan on this issue" --color 0E8A16
   ```
   Branch protection on a private repository needs GitHub Pro (free with the
   Student Developer Pack) or a public repository.
3. Read the ADRs in `docs/adr/`.
4. On a `spec/<topic>` branch, run `/grill-with-docs` and describe the idea.
   Fill `docs/spec/`. Merge the PR.
5. Choose the stack: the harness fixes none. An ADR, the "Technical
   baseline" in `docs/spec/constraints.md`, then CI and the command allowlist
   ("Choosing the stack" in the workflow).
6. Open an issue with the "Work item" form, then
   `claude --settings .claude/work-settings.json` and `/plan <issue number>`.

## Layout

| Path | What's in it |
|------|--------------|
| `CLAUDE.md` | The working agreement: rules the assistant follows (read automatically) |
| `CONTEXT.md` | Glossary of domain terms |
| `docs/process/workflow.md` | How the work goes, phase by phase |
| `docs/spec/` | The spec pack, as skeletons to fill |
| `docs/adr/` | Decisions, each with a `Revisit if:` trigger |
| `docs/templates/` | ADR, sensor report |
| `docs/handoff.md`, `docs/open_threads.md` | The next step; what is open |
| `app/` | The code. Created by the first issue that builds |
| `.claude/commands/` | `/plan`, `/build`, `/address-review`, `/sensor` |
| `.claude/skills/` | `/grill-with-docs`, `/grill-me`, `/to-spec`, `/to-tickets`, `/tdd`, … |
| `.claude/work-settings.json` | Permissions for work sessions (ADR-003) |
| `.github/` | Issue form, PR template, CI, CODEOWNERS, `branch-protection.json` |

There are no scripts: issues, branches, pull requests, labels and branch
protection are GitHub's own.

## Requirements

- **A GitHub repository** on a plan with branch protection, and the **GitHub
  CLI**, logged in (`gh auth status`).
- **Claude Code**. The work permissions use auto mode; if the account does
  not have it, change `defaultMode` in `.claude/work-settings.json`.
- Whatever the project's stack needs. The harness itself needs nothing else.

## Third-party material

The skills in `.claude/skills/` are from
[mattpocock/skills](https://github.com/mattpocock/skills), MIT
(`.claude/skills/LICENSE-mattpocock-skills`).
