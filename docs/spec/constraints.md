# Technical & organizational constraints

*Companion to the persona: the persona holds **user-anchored** non-negotiables; this
file holds the constraints that come from the organization, the law, and engineering
policy. Like non-negotiables, each should become **executable** where possible — a test,
a CI check, a lint rule; what cannot be executed goes on the review checklist instead
of remaining prose intention.*

## Dependencies & licensing
- <dependency policy, e.g. minimize external dependencies (APIs consumed, libraries integrated)>
- <license rules, e.g. no GPL/LGPL code; track license info for all direct dependencies>

## Code & style
- <style guide for the language, e.g. PEP 8 — enforce via linter in CI, not prose>

## Privacy, security, compliance
- <applicable data-privacy law in the business context, e.g. GDPR / national law;
  data-residency requirements>
- <security baseline, e.g. OWASP Top 10>

## Operational
- <deployment constraints: where it may run, who operates it, backup duties>

## Classify the system (sets the risk posture)
- <system criticality/type — e.g. Meyer's ABC classification — and the project
  dimensions (team size, criticality, ceremony) à la Kruchten's "octopus"; these tell
  you how much of this file the project actually needs>

## Technical baseline (filled when the stack is chosen)

*The harness does not fix a stack. Choose it during Discover, record it in an
ADR, and fill this section in the same `spec/` PR; `/build` holds every work
item to it. The matching `process/` PR adds the toolchain to
`.github/workflows/ci.yml` and the build commands to
`.claude/work-settings.json` (see "Choosing the stack" in
`docs/process/workflow.md`).*

- **Stack:** <language, build tool, framework; the ADR that records it>
- **Run every test:** `<one command, from the repo root>`. Green at the end
  of every issue.
- **End-to-end tests:** `<command>` · or: none
- **Start the app:** `<command>`, then `<URL or how to reach it>`
- **Structure checks:** <how the architecture rules are enforced by the
  build, e.g. architecture tests, module boundaries, lint rules> · or: none
- **Mutation testing:** `<command>` · or: none
- **Dependency licences:** <how the build checks them> · or: checked by hand
  in review
- **Lint and types:** `<command>`, no errors
