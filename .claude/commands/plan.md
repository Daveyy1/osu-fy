---
description: Plan a GitHub issue. Creates its work branch, posts the plan on the issue, and stops for the human's approval.
argument-hint: <issue number>
disable-model-invocation: true
---

# Plan an issue

**Issue number:** $ARGUMENTS

You write a plan and stop. You do not write app code in this command.

## 0. Check before anything else
Stop and tell the human if any of these fails. Do not try to fix it yourself.
- An issue number was given, and `gh issue view <number>` shows an open
  issue with a scope (stories, criteria, a ticket, or a described change). If
  the scope is unclear, ask on the issue instead of guessing.
- `git status` shows a clean working tree.

## 1. Get onto the work branch
- If you are already on `work/<number>-…`, stay there.
- Otherwise create the branch from the current `main`, linked to the issue:
  `gh issue develop <number> --base main --name work/<number>-<slug> --checkout`,
  where `<slug>` is two to four lowercase words from the issue title, joined
  by `-`. If `gh issue develop <number> --list` shows a branch already, check
  that one out instead.

## 2. Read
1. The issue and all its comments.
2. `CLAUDE.md`, `docs/process/workflow.md`.
3. The spec for the scope: `docs/spec/vision.md`, `persona.md`,
   `constraints.md`, `CONTEXT.md`, every ADR in `docs/adr/`,
   `api_contracts.md`, the stories and criteria in scope in
   `user_stories.md`, and `docs/spec/features/` where it applies.
4. `app/README.md` and the code this issue will touch or build on. Read
   enough to plan against what is there, not against what you assume.

## 3. Post the plan as one comment on the issue
`gh issue comment <number> --body-file <file>`, with the file written outside
the repo. Start the comment with `## Plan`. One to two pages, in this order:

- **Design:** how this will work, in a few lines. Name the ADRs it follows.
- **Files:** what you will create or change, grouped by layer, with a rough
  line estimate for non-test code. If the total is well past a few hundred
  lines, say so and **propose a split** into several issues.
- **Tests:** one line per test you will write, under the criterion it covers.
  Say at which seam each one tests. Say which criteria only a human can check.
- **Questions:** numbered Q1, Q2, …. Every point where the spec is unclear,
  missing or contradictory, and every design choice with a real alternative.
  For each: the question, the options, **your recommendation and why**, and
  what it costs to change later. Do not decide these yourself. A plan with no
  questions is suspicious: look again before you claim there are none.
- **Risks and where to look:** what could go wrong, what the tests will not
  cover, and where the reviewer should look hardest (secrets,
  authentication, input validation, outbound requests, data deletion,
  concurrency, time zones).
- **Not in this issue:** what a reader might expect that you will leave out.

End the comment with: *"Answer the questions in a reply, then add the label
`plan-approved`."*

## 4. Stop
Report in the chat: the design in two sentences, the size estimate, and the
questions. Then wait.

If the human answers in the chat instead of on the issue, post their answers
as a comment on the issue, in their words, so the record is in one place. If
an answer changes the design, post a short `## Plan, revised` comment that
says what changed.

You never add the `plan-approved` label, even when asked to in the chat: say
that it is theirs to set. Do not start building in this command: the human
types `/build`.
