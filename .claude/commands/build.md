---
description: Build the approved plan of the current work branch test-first and open a pull request that closes its issue.
disable-model-invocation: true
---

# Build an issue

## 0. Check before anything else
Stop and tell the human if any of these fails. Do not try to fix it yourself.
- `git branch --show-current` is `work/<number>-<slug>`; `<number>` is the
  issue.
- `gh issue view <number> --json labels,state` shows an open issue with the
  label **`plan-approved`**. Without it there is no approval, whatever the
  chat says.
- The issue has a `## Plan` comment, and every question in it has an answer
  in a later comment.
- `git status` shows a clean working tree.

## 1. Read
The issue with all comments (plan, answers, revisions), `CLAUDE.md`, the spec
for the scope, every ADR, and the code you will touch. Commits by the human
on this branch are decisions: build on them.

## 2. Spec first
If an answer changes or adds to what the app does, write it into the spec
(`docs/spec/`, `CONTEXT.md`) **as the first commit**, with a message that
names the question (`Spec: answer to Q2 of #<number>`). Change nothing else
in the spec. An answer that needs an ADR: stop and say so; ADRs are written
in spec mode.

## 3. Build
- Code goes into `app/`. **Never edit the harness** (`.claude/`, `.github/`,
  `CLAUDE.md`, `docs/process/`, `docs/adr/`, `docs/templates/`).
- **Stay inside the plan.** If the plan turns out to be wrong or a new
  question comes up that changes behaviour or design: stop, post the
  question on the issue, and wait. Small choices that the plan does not cover
  and that are easy to change (a private name, a helper's shape) you make
  yourself and list in the pull request.
- **Test first** (`/tdd`): one test, see it fail, make it pass, next test.
  Each acceptance criterion in scope gets at least one automated test whose
  name quotes its ID. Expected values come from the spec, never from running
  the code.
- Follow every ADR. Secrets come from environment variables (`.env`,
  git-ignored); never commit a real token, link or key.
- Everything that worked before must still work. Change an existing test only
  when the spec change requires it, and list every such change in the pull
  request.
- No refactoring or clean-up outside the plan. Note what you would clean up
  in the pull request instead.
- Commit in small steps that a reviewer can follow one by one.

## 4. Technical baseline (must hold at the end)
The project's stack and its commands are in the "Technical baseline" section
of `docs/spec/constraints.md` and in the stack ADR. If that section is not
filled, stop: the stack is chosen in spec mode, not during a build.

- The "run every test" command is green, including the structure checks the
  baseline names.
- Lint and type checks pass.
- If the baseline names mutation testing: run it and report the score for
  the code this issue changed.
- No dependency was added whose licence `constraints.md` forbids.
- `app/README.md` tells a human how to start the app, how to reach every
  feature, which environment variables exist, and which parts use a fake
  adapter.

An issue that creates `app/` sets all of this up. Later ones keep it true.

## 5. Look at it running
Start the app and exercise what you built, the way a user would. For a UI,
take screenshots at a desktop and a phone width and look at them. Fix what
you find, and say in the pull request what you looked at and what you could
not check (for example anything needing a real account or token).

## 6. Open the pull request
- `git push -u origin HEAD`, then `gh pr create --draft --base main` with a
  body file written outside the repo. The body follows
  `.github/pull_request_template.md`, every section filled:
  - `Closes #<number>` in the first line;
  - the test results with their commands;
  - **one unticked checkbox per in-scope acceptance criterion, worded
    exactly as in the spec**, followed only by how to reach its starting
    state, never by what the human should conclude;
  - decisions made during the build, new dependencies with their licences,
    existing tests that were changed, commands that were not on the
    allowlist;
  - where to look, and "TDD, honestly": which tests were red first and which
    were not.
- Leave every checkbox unticked. Never mark the pull request ready, never
  merge it.
- Report in a few lines: what was built, how to start it, what the reviewer
  should read first, and anything left open.
