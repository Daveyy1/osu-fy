---
description: Alignment sensor — evaluate the project's artifacts against externally given criteria; report aligned / gaps / structural risks; propose (never apply) remedies.
argument-hint: <the criteria, or where they come from>
---

Run a **sensor step**: a read-only alignment check of this project against
externally given criteria. The sensor's job is an honest verdict, not
reassurance — "alignment is poor" is a valid and useful result.

**Criteria:** $ARGUMENTS
(If empty or vague, ask for the criteria before doing anything else — a sensor
without criteria is an opinion.)

## Procedure

1. **Read the steering artifacts** before judging: product vision, personas,
   ADRs (`docs/adr/`), `docs/spec/` (user stories, constraints), `docs/open_threads.md`,
   `CONTEXT.md` — and the code in `app/`.
2. **Per criterion**, report three things, each grounded in evidence (file
   names, story IDs, ADR numbers — no vibes):
   - **Aligned** — what already satisfies it, including *seeds*: things that
     point the right way but aren't yet named as such.
   - **Gaps** — what is missing, out of scope, or contradicting the criterion.
   - **Structural risks** — ways the current architecture or story slicing
     would defeat the criterion *by default*, even if everyone executes
     faithfully. These are the most valuable findings; look hard for them.
3. **Lead with the overall verdict** in one blunt paragraph, then the
   per-criterion detail.
4. **Propose remedies** as candidate artifacts — new or reshaped user stories,
   ADR amendments, open threads — concrete enough to act on.
5. **Offer to record the report** as `docs/process/sensors/YYYY-MM-DD-<slug>.md` using
   `docs/templates/sensor_report.md`.

## Rules

- **Read-only.** A sensor changes nothing: no code, no story edits, no ADR
  amendments. Remedies are proposals and go through the normal gated flow
  (propose → human gate → branch → PR) *after* the human picks them up.
- **Honest verdict first.** If the project would fail the criteria as scoped,
  say so plainly and say why. A sensor that only confirms is broken.
- **Evidence over completeness.** A few load-bearing findings with references
  beat an exhaustive list of trivia.
- **Check the defaults.** Ask explicitly: *if the team builds exactly what the
  current stories say, do the criteria hold?* Misalignment usually hides in
  faithful execution, not in mistakes.
