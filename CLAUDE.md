# Working agreement (for the AI assistant)

How an AI coding assistant works in this repo. It stays at the repo root so the
assistant reads it automatically. Nothing below is specific to Claude: another
assistant can read the same contract under its own filename (e.g. `AGENTS.md`).

## The idea
Specs drive the code, the assistant writes most of it, and **a human engineer
reads and approves everything before it reaches `main`** (ADR-001). Work is
tracked the way GitHub projects usually track it: an issue, a branch, a pull
request (ADR-002). Read `docs/process/workflow.md` before doing anything.

## Branches: know where you are (ADR-002)
Check `git branch --show-current` before the first edit of a session.

| Branch | Holds | What you may do |
|--------|-------|-----------------|
| `main` | The spec, the decisions, the harness, and the reviewed code in `app/` | Never commit, push or merge to it. It is protected: it changes only through a pull request the human merges. |
| `spec/<topic>`, `process/<topic>` | A change to the spec or to the harness | Work here in spec mode. |
| `work/<issue>-<slug>` | The code for one issue | Work here in work mode. `/plan <issue>` creates it. |

**You never merge a pull request, never approve one, never mark one ready,
and never set the `plan-approved` label.** Those are the human's gates.

## Spec mode (`spec/…`, `process/…`)
- **Propose before building.** For anything non-trivial, say what you will
  change and which docs it touches, get approval, then edit.
- **One topic per branch and PR**, created before the first edit.
- **Keep the trackers current** in the same session:
  `docs/spec/user_stories.md` and `docs/open_threads.md`.
- **Every workflow change** gets a line in the changelog at the bottom of
  `docs/process/workflow.md`.

## Work mode (`work/<issue>-<slug>`)
One issue goes through three commands. The full instructions are in
`.claude/commands/`.

1. **`/plan <issue>`** reads the issue, creates its branch, posts the plan as
   a comment on the issue, and stops. Every point the spec leaves open is a
   **question for the human**, with your recommendation. You do not build
   until the issue carries the `plan-approved` label.
2. **`/build`** builds the approved plan test-first, pushes the branch and
   opens a draft pull request that closes the issue. Stay inside the plan: if
   it turns out to be wrong, stop and say so instead of improvising a
   different design.
3. **`/address-review`** answers the human's review comments, one by one.

Rules for work mode:
- **Edit only** `app/` and the parts of the spec the approved plan names.
  Never the harness (`.claude/`, `.github/`, `CLAUDE.md`, `docs/process/`,
  `docs/adr/`, `docs/templates/`).
- **Keep it small.** An issue is one story or one ticket. If the plan shows
  it will be much more than a few hundred lines of non-test code, say so in
  the plan and propose a split into several issues.
- **Write for the reviewer.** Small commits with meaningful messages, tests
  next to the code they cover, no drive-by refactoring, no unrelated changes.
- **The human may edit your code.** Treat their commits on the work branch as
  decisions: build on them, do not revert them.
- **The checkboxes in the pull request are the human's.** You write the
  acceptance criteria into it; you never tick them.

## Rules for both modes

### TDD is mandatory for app code
Write the test first, confirm it fails, implement. Never write implementation
without a failing test. Acceptance criteria are the test spec: each one gets
at least one automated test whose name quotes its ID. Say honestly in the
pull request where a test was not red first.

### Validate for real
Exercise the app on real data in the real environment, not only through mocks.
Say where mocks could hide failures (browser, external APIs, time zones).
Green tests are not validation; the review and the human check in the running
app are.

### Record decisions (ADRs)
A significant design, architecture, domain-model, or workflow decision gets an
ADR in `docs/adr/` (`docs/templates/adr.md`, numbered `NNN-slug.md`) with its
assumptions and a `Revisit if:` trigger. Check new requirements against
existing triggers and say when one fires. An ADR is accepted when the human
merges a PR that sets its status to `accepted`; never set that status
yourself. Never silently contradict an accepted ADR: comply or propose
superseding it. In work mode you do not write ADRs: put the decision in the
plan as a question.

### Non-negotiables
Privacy, security, and data rules live in `docs/spec/persona.md` and
`docs/spec/constraints.md`. They must become acceptance criteria and test
assertions, not prose intentions. Never weaken them silently.

### Be honest and terse
- State results directly; no trailing summaries.
- Flag limitations and uncertainty plainly; never claim something is verified
  when it isn't. Report failing tests with their output.
- Treat your own output as suspect and point the reviewer at the risky parts.

### Git
- Meaningful commit messages.
- Spec mode: commit and push only when asked.
- Work mode: commit in small steps; push the work branch and open the PR at
  the end of `/build`. Never force-push a branch that has a PR: the reviewer
  loses their place.

## Agent skills
- **Issue tracker:** GitHub issues, through the `gh` CLI. A feature spec from
  `/to-spec` still goes to `docs/spec/features/<feature-slug>/spec.md`,
  because the spec lives in the repo. Tickets from `/to-tickets` are
  published as GitHub issues, one per ticket, following
  `.github/ISSUE_TEMPLATE/work-item.md`; propose the list and get approval
  before creating them. Never apply the `plan-approved` label.
- **Domain docs:** single context. Glossary: `CONTEXT.md` at the repo root.
  ADRs: `docs/adr/`.
- **ADR format:** always `docs/templates/adr.md`. This overrides the format
  inside the `domain-modeling` skill.
- **User stories:** the story list in `/to-spec` output also goes into
  `docs/spec/user_stories.md`, with Given/When/Then acceptance criteria.
- **Sensor step** (`/sensor <criteria>`): a read-only alignment check against
  externally given criteria. Reports go to `docs/process/sensors/`
  (`docs/templates/sensor_report.md`).
