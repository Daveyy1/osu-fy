# Persona — <name / role>

*Written once, early. Its main job is to surface the non-negotiables so they propagate
into every acceptance criterion. You will rarely re-read it — that's fine.*

## Who
- **Role:** <e.g. course instructor / clinician / analyst>
- **Context:** <where and how they work; relevant constraints of their environment>
- **Technical level:** <so the UX matches>
- **Background:** <education/domain expertise, where it helps predict expectations>
- **Usage pattern:** <regular or occasional user? occasional users need rediscoverable UX>
- **Preferences & values:** <what they care about beyond function — e.g. control,
  transparency, speed>

## Goals
- <what they are trying to accomplish, and **why**>
- <…>

## Non-negotiables (these become acceptance criteria)

*Make each one concrete enough to test: name the data, define the boundary. "No personal
data leaves the machine" is a sentiment; "no student name or ID appears in any API
request or export file" is an assertion. These are the **user-anchored** constraints —
put technical and organizational ones (licenses, style, security baselines) in
`constraints.md` instead.*

- <e.g. no student name or ID in any API request or export — define what counts as
  personal data and where "the machine" ends>
- <e.g. a human approves every automated decision — a business invariant; assert it in
  every workflow test>
- <e.g. every AI suggestion and human decision is recorded, append-only — yes, this is
  also a feature; it appears here so no future story can silently drop it>

## Out of scope / explicitly NOT wanted
- <things to avoid building — including tactics, patterns, or idioms NOT to be used>
