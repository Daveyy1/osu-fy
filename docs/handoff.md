# Hand-off note

*The assistant keeps no memory between sessions: only what is written down.
Update this note at the end of every session that leaves work open. Keep it
short. It says where to continue, not what was done: the issues and pull
requests are the record of that.*

## Resume here (the exact next step)
1. On branch `spec/initial-spec`, type `/grill-with-docs` and continue the
   interview at round 3. Rounds 1 and 2 are answered (below); nothing from
   them is in `docs/spec/` yet.
2. When the interview is done: fill `docs/spec/`, then choose the stack
   ("Choosing the stack" in `process/workflow.md`).

## Settled in the interview (rounds 1 and 2), not yet in the spec
- **What it is:** osu-fy turns the Songs a Player knows from osu! into a
  playlist on their Streaming service. Spotify first, others later.
- **Who it is for:** the owner first, and friends who can handle a terminal
  and their own API keys.
- **Why a rewrite:** the first tool was rough and unoptimised and its CLI was
  ugly. Wanted: a clean, simple interface and room for other services.
- **Form:** a guided terminal app first, logic separate from the interface;
  a web app or GUI later.
- **Sources:** installed Beatmapsets (osu! stable and lazer) and the lists
  tied to the osu! account.
- **Uncertain matches:** only certain matches go into the playlist; the
  Player gets the doubtful and the unmatched Songs to look at.
- **Re-runs:** the same playlist is appended to. osu-fy never removes.
- **Other services:** Apple Music and YouTube Music were named as ideas, not
  commitments. Whether their APIs allow it is unchecked.
- **The old tool (`OsuSongParser`):** nothing is carried over unless the
  owner says so.

## To raise first in round 3
- Scope: "fewer things, done well" (round 1) against "all sources" (round
  2). Which source is built first, and is the rest roadmap or version one?
- Uncertain matches: does the Player only see the doubtful ones in a report,
  or decide on each of them inside osu-fy?
- Still unasked: what "unoptimised" meant concretely, which account lists,
  playlist naming and visibility, setup and keys for friends, where data is
  kept, the non-negotiables, the stack.

## Open decisions
See `open_threads.md`.

## Watch out
- `/plan`, `/build`, `/address-review`, `/grill-me`, `/grill-with-docs`,
  `/to-spec` and `/to-tickets` only run when typed.
- No pull request is open for `spec/initial-spec` yet. The owner wants it
  opened at the very end of discovery and reviews everything there.
