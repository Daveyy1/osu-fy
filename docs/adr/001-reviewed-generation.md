# ADR-001 — Reviewed generation: a human approves the plan and the code

*Status: accepted · Date: 2026-10-13*

## Context
An AI assistant can generate a working app from a good spec, and the result
can pass every acceptance check in the running app while nobody has read a
line of it. Checking only the behaviour leaves four things open:
- an acceptance check that passes says little about the code behind the
  behaviour;
- the assistant makes many small decisions alone while it builds, and a
  human asked afterwards tends to accept them all, so the spec drifts toward
  a description of the code;
- tests and code have the same author, and nobody checks that the tests
  could fail;
- security-relevant code (secrets, sessions) is verified by nobody.

Options: spec-only generation, where humans approve the spec and check the
running app; review of the code after the fact, for information only; or a
human in the loop before and after the build.

## Decision (Y-statement)
In the context of **building my own projects with an AI assistant writing
most of the code**, facing **generated code that works in the demo but that
nobody has read, and decisions that are made for me**, I decided for **two
human gates per issue: the engineer answers the open questions and
approves a written plan before the build, and reviews and merges the pull
request after it; the engineer may edit the code**, and against **spec-only
generation (nobody can defend the code)** and **review for information only
(findings without consequences)**, to achieve **code I understand and can
stand behind, and decisions that stay mine**, accepting **that every issue
now costs my attention twice, and that throughput is limited by how
much I can honestly review**.

## Assumptions
- Issues are small enough to review properly (one story or ticket, a few
  hundred lines of non-test code).
- I actually read the diff. A gate that is clicked through is worse than no
  gate, because it looks like one.
- The plan's questions catch most of the decisions that matter; the rest are
  small enough to be caught in review.

## Revisit if:
- Reviews turn into approvals within minutes, or without comments, across
  several issues: the unit is too big or the gate is not working.
- Most review findings are of a kind a machine could catch: move them into CI
  and review less.
- Plans come back with no questions, or with questions I always answer as
  recommended: the plan gate is not earning its cost.
- A second person joins: branch protection can then require an approving
  review (ADR-002), instead of relying on my discipline.
