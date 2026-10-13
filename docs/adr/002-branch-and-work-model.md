# ADR-002 — Branch and work model: issue, branch, pull request

*Status: accepted · Date: 2026-10-13*

## Context
The assistant writes code that I review, so every change needs a place for
its scope, its plan, my answers and the review, and `main` needs a guard
that keeps unreviewed code out.

Both can be built by hand: a script that numbers each piece of work and
creates its branch and record files in the repository, and a pre-push hook
that refuses pushes to `main`. Or they can be left to the platform: a GitHub
issue is the usual way to describe a change, a pull request the usual place
to review it, and branch protection the usual guard. Branch protection on a
private repository needs a paid plan; GitHub Pro covers it.

## Decision (Y-statement)
In the context of **a solo project where an assistant writes code that I
review**, facing **the choice between home-made tracking and the platform's
own**, I decided for:
1. **`main`** holds the spec, the decisions, the harness and the reviewed
   code in `app/`.
2. **One GitHub issue per piece of work.** The issue holds the scope, the
   assistant's plan (a comment), my answers (replies) and my approval (the
   `plan-approved` label).
3. **One branch per issue, `work/<issue>-<slug>`**, created and linked with
   `gh issue develop`, and **one pull request** that closes the issue. The
   pull request holds the build record, the acceptance criteria as
   checkboxes, and the review.
4. **`spec/<topic>` and `process/<topic>`** branches for the spec and the
   harness.
5. **Branch protection on `main`** (`.github/branch-protection.json`): pull
   request required, CI green, every review conversation resolved, no force
   pushes, no deletion, and no exception for the repository's owner.

I decided against **plan and log files in the repo, created by a script**
(a second tracker next to the one GitHub has; an index that conflicts
between branches), **a pre-push hook** (per clone, and `--no-verify` skips
it), **code on a separate integration branch** (two long-lived branches for
a comparison I do not need) and **a never-merged branch per generation attempt** (code that is
never integrated cannot be reviewed into anything). This is to achieve **a
process anyone who knows GitHub can follow, with the record where people
look for it and a guard on `main` that cannot be bypassed by accident**. I
accept **that the plan, the answers and the review live on GitHub and not in
the repository's history, that the harness now needs GitHub and the `gh`
CLI, and that the protection and the label must be set up once per
repository because a template does not carry them**.

## Assumptions
- The repository is on GitHub with a plan that allows branch protection
  (public, or GitHub Pro for a private one).
- Issues are small and short-lived, so work branches rarely conflict.
- An approval count of 0 is deliberate: GitHub does not let the author of a
  pull request approve it, and with one account the author is always me. The
  gate is that only I can merge, and only when CI is green and every thread
  is resolved.

## Revisit if:
- A second person joins: raise the required approvals to 1 and fill in
  `.github/CODEOWNERS`.
- The record must survive a move away from GitHub: export issues and pull
  requests, or go back to plan and log files in the repo.
- Two issues are regularly open at once and conflict: require branches to be
  up to date before merging.
- I want to compare approaches (models, prompts, step sizes) on the same
  spec: give each attempt its own never-merged branch for that experiment.