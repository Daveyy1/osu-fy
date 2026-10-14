# Context — glossary

*The project's domain language, written by `/grill-with-docs` as terms
settle. One term, one meaning: code, tests, stories and the UI use these
words and no synonyms. Format: `.claude/skills/domain-modeling/CONTEXT-FORMAT.md`.*

## Terms

**Player**:
A person who plays osu! and uses osu-fy to listen to the game's songs outside the game.
_Avoid_: User, account

**Beatmapset**:
One upload in osu!: a piece of music with one or more difficulties. It is what a Player has installed or has in the lists on their osu! account.
_Avoid_: Map, beatmap, mapset

**Song**:
A piece of music, identified by artist and title. Several Beatmapsets of the same piece, including cut versions, are one Song.
_Avoid_: Ingame song, title

**Track**:
The item on a Streaming service that a Song is matched to. A playlist holds each Track once.
_Avoid_: Song (for the service's item), result

**Streaming service**:
A music service on which a Player has an account and where osu-fy creates playlists for them. Spotify is the first; others follow later.
_Avoid_: Platform, provider, music service

**Source**:
A place where osu-fy finds the Beatmapsets a Player knows: the lazer install first; the stable install and the lists on the osu! account later.
_Avoid_: Input, import, scan

**Playlist**:
The one playlist osu-fy creates for a Player on a Streaming service, named by the Player, private by default, and only ever appended to.
_Avoid_: List, export

**Match**:
A Song paired with the Track osu-fy believes is the same piece of music.
_Avoid_: Result, hit

**Certain match**:
A Match osu-fy adds to the Playlist without asking.
_Avoid_: Confident match, auto-match

**Doubtful match**:
A Match that goes into the Playlist only if the Player says yes in the Review.
_Avoid_: Review item, uncertain match, candidate

**Unmatched Song**:
A Song for which osu-fy found no plausible Track. It is listed for the Player, never added.
_Avoid_: Missing song, failed match

**Review**:
The step in which the Player decides which Doubtful matches go into the Playlist, all at once or one by one.
_Avoid_: Confirmation, check

**Session**:
One use of osu-fy, from starting it to quitting: read the Songs, match the new ones, add the Certain matches, Review, list the Unmatched Songs.
_Avoid_: Run, sync, pass
