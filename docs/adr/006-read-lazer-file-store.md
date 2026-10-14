# ADR-006 — Read lazer through its file store, not its realm database

*Status: accepted · Date: 2026-10-14*

## Context
osu!lazer stores every file under `files/<h>/<hh>/<sha256>`. Only its realm
database (`client.realm`) records which files belong to which Beatmapset,
and whether a Beatmapset is installed or pending deletion. As of 2026-10-14
there is no official or maintained way to read a realm file from Python;
MongoDB ended its Atlas Device SDKs on 2025-09-30. Readers exist in C#
(lazer itself), F# and Rust, and lazer only exports one `.osz` per set.

The owner's first tool skipped the database: it walked `files/`, parsed every
file as a `.osu` file and kept those with metadata. It worked reliably and
fast on the owner's library.

In lazer's source (checked 2026-10-14): deleting a Beatmapset only marks it
pending deletion, and updating a set does the same to the old version.
Deleting or editing a difficulty only drops the file's reference. Files are
removed from `files/` only when lazer next starts.

Options on the table: walk the file store; call an external realm reader as
a subprocess; ask the Player to export from lazer first.

## Decision (Y-statement)
In the context of **reading the Beatmapsets a Player has installed in
lazer**, facing **the lack of a Python realm reader**, we decided for
**walking `files/`, recognising `.osu` files by their content, reading only
their General and Metadata sections, opening every file read only**, and
against an external reader (a second runtime to install and trust) and a
manual export (a chore before every Session), to achieve **pure Python with
no extra install, proven on the owner's library**. We accept that **a
Beatmapset deleted in lazer, an old version of an updated set and an old
version of an edited difficulty are still found until lazer next starts**.
For an updated set this is the same Song anyway. For a deleted one it may
add a Track the Player no longer wants, which they remove by hand.

## Assumptions
- Lazer keeps `.osu` files unchanged and readable in `files/`.
- Lazer cleans up unreferenced files at startup, so the window is short for
  a Player who plays regularly.
- Reading the start of each file is fast enough for a few thousand
  Beatmapsets plus their audio and images.

## Revisit if:
- Lazer changes its file store layout, or stops cleaning up at startup.
- A maintained Python reader for realm appears, or lazer offers a
  command-line or bulk export.
- Players report deleted maps showing up as a real nuisance.
- Reading the file store takes more than a minute on a real library.
