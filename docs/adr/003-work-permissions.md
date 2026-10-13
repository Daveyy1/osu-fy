# ADR-003 — Work permissions: auto mode plus a versioned allowlist

*Status: accepted · Date: 2026-10-13*

## Context
Claude Code asks before it runs commands or writes files unless a permission
rule or mode allows it. During `/build` nobody should have to sit and answer
a prompt for every test run, but an unattended session should also not be
able to rewrite its own rules or merge its own work. Permission rules have
two known weaknesses: deny rules on files bind Claude's file tools but not
shell commands that write files, and nothing in a session's output shows
that a settings file was loaded at all.

## Decision (Y-statement)
In the context of **work sessions (`/plan`, `/build`, `/address-review`)**,
facing **routine commands that should not need me, and a few actions that
must stay mine**, I decided for **a separate file,
`.claude/work-settings.json`, loaded with `claude --settings
.claude/work-settings.json`**: auto mode, an allowlist of the routine git and
GitHub commands (each project adds its build and test commands when it
chooses its stack), allow rules for writes to `app/` and the spec, and deny
rules for writes to the harness and for the actions that are my gates:
merging, approving or readying a pull request, editing an issue's labels
(the `plan-approved` label is my approval of a plan), pushing to `main` and
force-pushing. I decided against **the shared
`.claude/settings.json`** (it would loosen spec sessions too, where commits
should still ask first), **no permission checks** (too much trust in an
unwatched session) and **an allowlist without auto mode** (every unlisted
command would stop the build), to achieve **builds that run without me and
cannot approve themselves**, accepting **that anything off the list is judged
by auto mode, and that the deny rules on files do not cover shell commands
that write files; the review of the diff is what catches those**.

## Assumptions
- Auto mode is available on the account in use. If it is not, change
  `defaultMode` and answer the prompts.
- Deny rules on `Edit(...)` block Claude's Write and Edit tools (seen with
  Claude Code 2.1.284; check again after a major update).
- Every change by a work session ends up in a diff that I read, so a write
  outside the allowed paths is seen before it is merged.

## Revisit if:
- A diff shows a change to the harness made through the shell: turn on
  Claude Code's sandbox where the platform supports it (not on native
  Windows at the time of writing; WSL does).
- A plan was approved or a pull request merged by a session and not by me:
  the deny rules match command prefixes and can be worded around. Use a
  separate GitHub account or a fine-grained token without those rights for
  work sessions.
- The same unlisted commands come up in several issues: add them to the
  allowlist in a `process/` PR.
- The allowlist grows so broad that it no longer says anything.
