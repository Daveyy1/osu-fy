# osu-fy

Turns the songs you have installed in **osu!lazer** into a private
**Spotify** playlist.

> **Status: in development.** Nothing to install yet. The install guide
> arrives with story US-11, at the end of version one.

## What it will do

1. Find your lazer folder and read the beatmapsets installed there. It
   never changes anything in your osu! install.
2. Search Spotify for each song: TV Size cuts, Japanese or romanised titles,
   and the exact remix or Nightcore version where Spotify has it.
3. Add every certain match to one private playlist, which you name. osu-fy
   only ever adds; it never removes or reorders anything.
4. Show the doubtful matches in one table: add them all, decide one key
   press at a time, or leave them for later.
5. List the songs it could not find, with links that make adding one by
   hand a click.

Run it again after downloading new maps: it only searches what is new.

You will need Windows, [uv](https://docs.astral.sh/uv/), and a Spotify
account. You also register your own free Spotify developer app; osu-fy walks
you through it. Spotify currently requires Premium for the app's owner.

## How it is built

The specification comes first, an AI assistant writes most of the code,
and a human reviews every plan and every line before it reaches `main`.

- What osu-fy is and does not do: [`docs/spec/vision.md`](docs/spec/vision.md)
- The stories and their acceptance criteria:
  [`docs/spec/user_stories.md`](docs/spec/user_stories.md)
- Build order: [`docs/spec/roadmap.md`](docs/spec/roadmap.md)
- Decisions: [`docs/adr/`](docs/adr/README.md)
- How the work is done: [`docs/process/workflow.md`](docs/process/workflow.md)
  and [`docs/process/harness.md`](docs/process/harness.md)

## Licence

MIT. The skills in `.claude/skills/` are from
[mattpocock/skills](https://github.com/mattpocock/skills), MIT
(`.claude/skills/LICENSE-mattpocock-skills`).
