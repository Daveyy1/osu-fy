# Roadmap — build order

*All features, in the order they will be built. An issue takes one story or
ticket from the top. "Blocked by" makes dependencies explicit, including
missing API access.*

One issue per story; US-05 is split in two (5a, 5b) and a walking skeleton (1a)
comes first. Each one ends in a reviewed pull request and leaves an
app that starts and does a little more than before.

| # | Epic / feature | Stories | Blocked by | Issue(s) |
|---|----------------|---------|------------|----------|
| 0 | Set up the toolchain: CI, allowlist (a `process/` PR, not a story) | — | this spec merged | PR #3 |
| 1a | Walking skeleton: `osu-fy` starts; structure, import contracts, first CI run | — | 0 | #4 |
| 1 | Find the lazer folder | US-01 | 1a | #5 |
| 2 | Read Songs from lazer, sample lazer folder | US-02 | 1 | #6 |
| 3 | Connect to Spotify | US-03 | 1; a Spotify developer app (owner has Premium) | #7 |
| 4 | Name and create the Playlist | US-04 | 3 | #8 |
| 5a | Search Spotify at a safe pace, recorded answers | US-05 (part) | 2, 3 | #9 |
| 5b | Matching rules and the quality set | US-05 (part) | 5a; the owner confirms ~10 missed Songs (y/n) | #10 |
| 6 | Add Certain matches | US-06 | 4, 5a | #11 |
| 7 | Review Doubtful matches | US-07 | 5b, 6 | #12 |
| 8 | List the Unmatched Songs | US-08 | 5a | #13 |
| 9 | Later Sessions | US-09 | 6, 7, 8 | #14 |
| 10 | Rate limits and failures | US-10 | 5a, 9 | #15 |
| 11 | README and install guide | US-11 | 10 (and so all before) | #16 |

## Later (not specified yet)

| Feature | Blocked by |
|---------|------------|
| osu! stable as a Source (`osu!.db`, documented format) | version one |
| osu! account lists as a Source (osu! API v2, client credentials) | version one; N4 extended to `osu.ppy.sh` |
| macOS and Linux folders | version one |
| A downloadable `.exe` | version one |
| Choose an existing playlist to append to | someone asking for it |
| Apple Music | a $99/year Apple developer membership; browser login step |
| YouTube Music | no official API; YouTube Data API allows about 100 searches a day |
