# ADR-005 — Structure: a core with ports, checked by the build

*Status: accepted · Date: 2026-10-14*

## Context
The owner wants the logic separate from the interface, so that a GUI or web
app can come later, and room for other Sources and Streaming services. The
first tool mixed reading, matching, Spotify calls and terminal output in the
same functions. With an assistant writing most of the code, a layering rule
written only in prose erodes one convenient import at a time. Reviews are
the scarce resource, so the build should catch it.

Options on the table: rules in prose checked in review; one package with
conventions; a core with ports and adapters whose import rules are tests.

## Decision (Y-statement)
In the context of **a codebase an assistant writes and a human reviews**,
facing **the risk that logic, Spotify calls and terminal output tangle
again**, we decided for **a core (domain and Session steps) that defines the
ports it needs (Source, Streaming service, Player) and imports none of the
adapters, the terminal UI, spotipy, rich or readchar; adapters and the UI
depend on the core, never the other way round; enforced by import-linter
contracts that run with the tests and in CI; plus a test that the Streaming
service port has no remove or reorder operation (N1)**, and against rules in
prose only, **to achieve one test seam for nearly all behaviour, and adapters
that can be swapped (spotipy for plain HTTP, Spotify for another service, a
terminal for a GUI) without touching the core**, accepting **a little more
structure than a tool this size strictly needs**.

## Assumptions
- One core is enough: osu-fy has a single context (`CONTEXT.md`).
- import-linter can express the contracts and runs in CI.
- Ports stay small: the Streaming service port has five operations.

## Revisit if:
- A second Streaming service does not fit the Streaming service port's five
  operations.
- A GUI or web app needs the Session steps split differently.
- The contracts are bypassed or loosened more than once in review.
