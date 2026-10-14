# Vision — osu-fy

*One page. Claude reads this first for every issue, so keep it short and concrete.*

## In one sentence
For osu! players who want to hear the game's music outside the game, osu-fy
is a guided terminal app that turns the Songs they have installed in
osu!lazer into a private Spotify Playlist, unlike searching Spotify by hand
for hundreds of Songs with Japanese titles, TV Size cuts and Nightcore edits.

## The problem
A Player knows hundreds of Songs from osu!. Finding each one on Spotify by
hand takes hours: titles are in Japanese or romanised, maps are cut to TV
Size, many are remixes or Nightcore edits. The owner's first tool
(`OsuSongParser`) did the job, but its code was not clean, its interface was
ugly, and it left 132 of 292 Songs Unmatched, many of which are on Spotify.

## What the app does
- Finds the lazer folder and reads the Beatmapsets installed there, without
  ever changing them.
- Turns Beatmapsets into Songs, so each piece of music is searched once.
- Matches each Song to a Track on Spotify and sorts the result into Certain
  matches, Doubtful matches and Unmatched Songs.
- Appends Certain matches to one private Playlist straight away; lets the
  Player decide on Doubtful matches in a Review; lists the Unmatched Songs
  with links that make adding them by hand one click.
- Remembers everything between Sessions, so a later Session only searches
  Songs that are new.

## What it deliberately does not do
- Never removes or reorders Tracks in a Playlist; never changes the osu!
  install.
- No GUI or web app in version one.
- No Streaming service other than Spotify in version one.
- No downloading or playing of music, no use of the audio files.
- No osu! account lists, no osu! stable, no collections in version one
  (they are on the roadmap).
- No several Players or Playlists per Windows user account.
- No telemetry, no server of its own: nothing about the Player goes anywhere
  but osu! and the Streaming service.
- English only.
- No "add all" for Doubtful matches without showing the full list first.

## What success looks like
- On the matching quality set (the 154 Songs the old tool matched, the five
  Song-identity cases, and about ten Songs the old tool missed that the
  owner confirmed): **no wrong Certain match**, each of the 154 Songs
  matched to the same Track as before, and on the owner's own library
  **fewer Unmatched Songs than the old tool's 132**.
- A friend goes from nothing to a filled Playlist by following only the
  README and the guided setup.
- A first Session over about 300 Songs takes around 10 minutes without ever
  looking frozen; a later Session with no new Songs takes seconds.
