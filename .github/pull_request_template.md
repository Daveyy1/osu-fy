<!-- Work on an issue: first line "Closes #<issue>". Spec or harness change:
     delete the sections that do not apply. -->

## What and why
<!-- Two sentences. For an issue: what this builds, and a link to the plan
     comment on the issue. -->

## Tests
<!-- Suite result with the command. Mutation score for the changed code, if
     the stack has it. Existing tests that were changed, and the spec change
     that required each. -->

## Acceptance criteria (the reviewer ticks these in the running app)
<!-- One checkbox per criterion in scope, worded exactly as in the spec,
     followed only by how to reach its starting state. The author never
     ticks them. A criterion that fails stays unticked and gets a comment. -->
- [ ] US-..

## Decisions made during the build
<!-- Small choices the plan did not cover. New dependencies with licence and
     reason. Commands that were not on the allowlist. -->

## For the reviewer
- **Read first:** <!-- the two or three files that carry the change -->
- **Riskiest part:** <!-- and why -->
- **Weakest tests / where mocks could hide a failure:**
- **Not checked in the running app:** <!-- e.g. needs a real token -->
- **TDD, honestly:** <!-- which tests were red first, which were not -->

## Review checklist (the human reviewer ticks these, not the assistant)
- [ ] The plan was approved before the build, and the code does what the plan says
- [ ] Spec changes in this PR are exactly the answers given on the issue
- [ ] Tests read before the implementation: each asserts what its criterion says, with expected values from the spec
- [ ] Risky paths read line by line (secrets, authentication, input validation, outbound requests, deletion)
- [ ] Nothing unrelated: no drive-by refactoring, no new dependency without a reason
- [ ] I understand everything in this PR and could explain it without the assistant

Spec or harness change only:
- [ ] Every new or changed acceptance criterion can be checked by a human in the running app
- [ ] A decision was made or changed → ADR with `Revisit if:`; existing ADRs' triggers checked
- [ ] Harness change → a line in the changelog of `docs/process/workflow.md`
- [ ] `docs/open_threads.md` and `docs/handoff.md` are current
