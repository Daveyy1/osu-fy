# User stories — <app name>

The contract every issue is built and checked against. One row per
story; full stories below. Open and future work lives in `../open_threads.md`.

## Status

| ID | Title | Epic | Spec | Built by |
|----|-------|------|------|----------|
| US-01 | <title> | 1 <epic> | 🔲 draft | |

Spec: 🔲 draft · ✅ ready (reviewed and merged; may be built) · ⏸ parked.
"Built by" names the issue whose pull request was merged (`#12`).

## How to write a story

- **Format:** As a **<role>**, I want **<capability>** so that **<benefit>**.
- **Acceptance criteria** are Given/When/Then, concrete and observable: real
  values and names, not adjectives. "The export has one row per student and
  no name column", not "the export works".
- **Each criterion must be checkable by a human in the running app**, without
  reading code. Say how to reach the state it starts from (e.g. which sample
  data or fake adapter produces it).
- **Edge cases get their own criteria**: empty data, failing external APIs,
  invalid input.
- **Non-negotiables are copied in.** If a rule from `persona.md` or
  `constraints.md` applies, restate it here as a testable criterion. It does
  not count if it stays behind in the persona.
- **Out of scope** when a reader could reasonably expect more.
- **Criterion IDs** are `US-NN.n`. Automated tests quote them in their names.
- **Size:** a story should fit one issue. If its plan comes back larger
  than a few hundred lines of non-test code, split the story.

## Stories

### US-01 — <title>
As a **<role>**, I want **<capability>** so that **<benefit>**.

- **US-01.1** Given <starting state>, when <action>, then <observable result>.
- **US-01.2** Given <edge case>, then <observable result>.

Out of scope: <what a reader might expect that is not part of this story>.
