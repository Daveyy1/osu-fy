# Roadmap — build order

*All features, in the order they will be built. An issue takes one story or
ticket from the top. "Blocked by" makes dependencies explicit, including
missing API access.*

One issue per story. Each one ends in a reviewed pull request and leaves an
app that starts and does a little more than before.

| # | Epic / feature | Stories | Blocked by | Issue(s) |
|---|----------------|---------|------------|----------|
| 0 | Set up the toolchain: CI, allowlist (a `process/` PR, not a story) | — | this spec merged | |
| 1 | Walking skeleton: `osu-fy` starts and finds the lazer folder | US-01 | 0 | |
| 2 | Read Songs from lazer, sample lazer folder | US-02 | 1 | |
| 3 | Connect to Spotify | US-03 | 1; a Spotify developer app (owner has Premium) | |
| 4 | Name and create the Playlist | US-04 | 3 | |
| 5 | Match Songs to Tracks, recorded answers, quality set | US-05 | 2, 3; the owner confirms ~10 missed Songs (y/n) | |
| 6 | Add Certain matches | US-06 | 4, 5 | |
| 7 | Review Doubtful matches | US-07 | 6 | |
| 8 | List the Unmatched Songs | US-08 | 5 | |
| 9 | Later Sessions | US-09 | 6, 7, 8 | |
| 10 | Rate limits and failures | US-10 | 5, 9 | |

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
