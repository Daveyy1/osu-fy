# User stories — osu-fy

The contract every issue is built and checked against. One row per
story; full stories below. Open and future work lives in `../open_threads.md`.

## Status

| ID | Title | Epic | Spec | Built by |
|----|-------|------|------|----------|
| US-01 | Find the lazer folder | 1 Read lazer | ✅ ready | #5 |
| US-02 | Read Songs from lazer | 1 Read lazer | ✅ ready | #6 |
| US-03 | Connect to Spotify | 2 Spotify | ✅ ready | #7 |
| US-04 | Name and create the Playlist | 2 Spotify | 🔲 draft | |
| US-05 | Match Songs to Tracks | 3 Matching | 🔲 draft | |
| US-06 | Add Certain matches | 4 Fill the Playlist | 🔲 draft | |
| US-07 | Review Doubtful matches | 4 Fill the Playlist | 🔲 draft | |
| US-08 | List the Unmatched Songs | 4 Fill the Playlist | 🔲 draft | |
| US-09 | Later Sessions | 5 Keep it going | 🔲 draft | |
| US-10 | Rate limits and failures | 5 Keep it going | 🔲 draft | |
| US-11 | README and install guide | 6 Share it | 🔲 draft | |

Spec: 🔲 draft · ✅ ready (reviewed and merged; may be built) · ⏸ parked.
"Built by" names the issue whose pull request was merged (`#12`).

Feature spec for all eleven: `features/lazer-to-spotify/spec.md`.

## How to write a story

- **Format:** As a **<role>**, I want **<capability>** so that **<benefit>**.
- **Acceptance criteria** are Given/When/Then, concrete and observable: real
  values and names, not adjectives. "The export has one row per student and
  no name column", not "the export works".
- **Each criterion must be checkable by a human in the running app**, without
  reading code. Say how to reach the state it starts from (e.g. which sample
  data or fake adapter produces it).
- **Edge cases get their own criteria**: empty data, failing external APIs,
  invalid input.
- **Non-negotiables are copied in.** If a rule from `persona.md` or
  `constraints.md` applies, restate it here as a testable criterion. It does
  not count if it stays behind in the persona.
- **Out of scope** when a reader could reasonably expect more.
- **Criterion IDs** are `US-NN.n`. Automated tests quote them in their names.
- **Size:** a story should fit one issue. If its plan comes back larger
  than a few hundred lines of non-test code, split the story.

## Shared starting states

- **The sample lazer folder** comes with the tests (US-02 builds it). It has
  lazer's layout (`files/<h>/<hh>/<sha256>` plus an empty `client.realm`)
  and holds only `.osu` files, no audio, for these Beatmapsets:
  鹿乃 – Walk This Way! and 鹿乃 – Walk This Way! (Cut Ver.) (one Song),
  花になって (TV Size), ナイトメア – the WORLD, VINXIS – Greetings,
  Rockefeller Street (Nightcore Mix), Monster (DotEXE Remix),
  Silver Forest – ケロ⑨destiny, and Jump Training #1. The Player can point
  osu-fy at it when it asks for the lazer folder (US-01.3).
- **A fresh start:** delete or rename `%APPDATA%\osu-fy`. osu-fy then
  behaves as in a first Session.

## Stories

### US-01 — Find the lazer folder
As a **Player**, I want **osu-fy to find my lazer folder by itself** so that
**I do not need to know where lazer keeps its data**.

- **US-01.1** Given lazer's data is in the default folder `%APPDATA%\osu`
  (it contains a `files` folder) and a fresh start, when the Player starts
  osu-fy, then it shows that path and asks "Use this lazer folder? [Y/n]";
  Enter or `y` accepts it, and osu-fy shows "Reading lazer folder <path>".
- **US-01.2** Given the Player moved lazer's data in lazer's settings, so
  `%APPDATA%\osu\storage.ini` names another folder that contains `files`,
  when osu-fy starts fresh, then it shows that other folder instead.
  If that folder has no `files`, osu-fy offers the default folder, as
  lazer itself does. (Reach it by moving the data in lazer's settings, or
  by writing `storage.ini` by hand with the line `FullPath = <folder>`.)
- **US-01.3** Given no lazer folder is found, or the Player answers `n`,
  then osu-fy asks for the path; given a path without a `files` folder, it
  says "No lazer data found in <path>" and asks again, until the path is
  right or the Player quits with `q`. Quotes around a pasted path are
  ignored.
- **US-01.4** Given the Player confirmed a folder in an earlier Session,
  when they start osu-fy again, then it uses that folder without asking and
  shows "Reading lazer folder <path>". If osu-fy's settings file cannot be
  read, it stops with "Cannot read <path>: <reason>. Fix or delete it."
- **US-01.5** Given the remembered folder no longer contains a `files`
  folder, then osu-fy says "No lazer data found in <path>" and asks as in
  US-01.1 to US-01.3.

Out of scope: osu! stable; macOS and Linux folders (roadmap).

### US-02 — Read Songs from lazer
As a **Player**, I want **osu-fy to read the Beatmapsets installed in lazer
and turn them into Songs** so that **each piece of music is searched only
once**.

- **US-02.1** Given the sample lazer folder, when osu-fy reads it, then it
  shows "Found 8 Songs in 9 Beatmapsets": the two Walk This Way!
  Beatmapsets are one Song. A lazer folder without Beatmapsets shows
  "Found 0 Songs in 0 Beatmapsets" and osu-fy carries on.
- **US-02.2** Given a Beatmapset with several difficulties (several `.osu`
  files with the same Beatmapset), then it counts as one Beatmapset.
  Difficulties without a Beatmapset id are grouped by artist and title in
  both scripts.
- **US-02.3** Two Beatmapsets are the same Song when their artist and title
  are equal after ignoring case, full-width characters, extra spaces and
  cut markers: `(TV Size)`, `(TV Size Ver.)`, `(TV size ver.)`,
  `(Cut Ver.)`, `(Short Ver.)`, `～TVサイズ～`, `~TV Size~`. The romanised
  artist and title are compared; the original script only when they are
  empty. Version markers such as `(Nightcore Mix)`, `(… Remix)` or
  `(Extended Mix)` are **not** ignored: a Nightcore map and the original are
  two Songs.
- **US-02.4** Given files in `files` that are not `.osu` files (audio,
  images, skin files), or a `.osu` file without artist or title, then they
  are skipped without an error message.
- **US-02.5** Given the Player's real lazer folder with about 300
  Beatmapsets, while osu-fy reads it, then a progress bar counts the files
  read, so the app never looks frozen.
- **US-02.6** (N2) Given the Player's real lazer folder, when osu-fy has
  read it, then no file in it was created, changed or deleted: a listing of
  names, sizes and modification times (`dir /s /t:w`) taken before and after
  is identical. An automated test asserts the same on the sample folder.

Out of scope: maps deleted in lazer whose files lazer has not yet removed
are still found until lazer next starts (known limitation, ADR-006). Showing
the full list of Songs.

### US-03 — Connect to Spotify
As a **Player**, I want **osu-fy to guide me through connecting my own
Spotify app and logging in** so that **I can use osu-fy without anyone
else's keys**.

- **US-03.1** Given a fresh start and a confirmed lazer folder, then osu-fy
  shows the setup guide (open <https://developer.spotify.com/dashboard>,
  create an app with the Web API, add the redirect URI
  `http://127.0.0.1:8765/callback` exactly, copy the Client ID), mentions in
  one line that a friend can instead be added to someone else's app, and
  asks for the Client ID.
- **US-03.2** Given the Player pastes something that is not 32 hexadecimal
  characters, then osu-fy says "That does not look like a Client ID" and
  asks again.
- **US-03.3** Given a valid Client ID, then osu-fy opens the browser on
  Spotify's login page; after the Player agrees, the terminal shows
  "Logged in to Spotify as <display name>".
- **US-03.4** While osu-fy waits for the browser, it shows "Waiting for the
  login in your browser… press t to try again, c for another Client ID, q
  to quit". Given the Player refuses access, closes the browser tab or
  presses t, c or q, then osu-fy says "The login did not complete." and
  offers "Try again [t], enter another Client ID [c] or quit [q]": after a
  refusal at once, after a closed tab after at most 3 minutes, and a key
  pressed while waiting counts as the answer. `c` asks for the Client ID as
  in US-03.2. The Client ID stays saved.
- **US-03.8** Given Spotify cannot be reached during the login (disconnect
  the network first), then osu-fy stops with "Can't reach Spotify.
  Everything found so far is kept; try again later."; given port 8765 is
  in use (start a second osu-fy while the first waits for the browser),
  it stops with "Port 8765 is in use; is osu-fy already running?". No
  Python traceback in either case. (US-10.5 adds the retry.)
- **US-03.5** Given a saved login, when the Player starts osu-fy again, then
  osu-fy refreshes the login, no browser opens and the terminal shows
  "Logged in to Spotify as <display name>". Refreshing at every start makes
  removed access (US-10.4) take effect at the next start, not up to an hour
  later.
- **US-03.6** (N3) Given a completed login, then the tokens are stored only
  in osu-fy's token file in `%APPDATA%\osu-fy`: no file appears in the
  folder osu-fy was started from (no `.cache`), and no token text appears
  in the terminal. An automated test asserts both with a fake token.
- **US-03.7** (N4) osu-fy contacts no host other than
  `accounts.spotify.com` and `api.spotify.com`. Checked by an automated
  test of the adapter's configuration, and in review.

Out of scope: several Spotify accounts per Windows user; logging out (the
Player removes access at spotify.com/account/apps; osu-fy notices at the
next start, US-03.5).

### US-04 — Name and create the Playlist
As a **Player**, I want **to name my Playlist once and have osu-fy keep
adding to it** so that **all my osu! Songs end up in one place**.

- **US-04.1** Given a login and no Playlist yet, then osu-fy asks
  "Name for your Playlist [osu!fy]:"; Enter, or a name of only spaces,
  accepts `osu!fy`, and `q` quits. It creates a **private** Playlist with
  that name and shows its name and link. (Check: the Playlist appears in
  Spotify, marked private.)
- **US-04.2** Given a Playlist created in an earlier Session, then osu-fy
  uses the same Playlist, found by its Spotify id even if the Player renamed
  it in Spotify, and does not ask for a name. It shows "Adding to your
  Playlist <current name> <link>".
- **US-04.3** Given the Player already has a playlist called `osu!fy` that
  osu-fy did not create, then osu-fy creates its own new Playlist and never
  touches the other one.
- **US-04.4** Given the Player deleted the Playlist in Spotify (or logs in
  with another Spotify account), then osu-fy says "Your Playlist is no
  longer in your Spotify library." and asks for a name as in US-04.1. It
  creates a new Playlist and uses it from then on.

Out of scope: choosing an existing playlist to append to (later, if asked
for).

### US-05 — Match Songs to Tracks
As a **Player**, I want **osu-fy to find the Track for each Song and sort
the results into Certain matches, Doubtful matches and Unmatched Songs** so
that **only the right Tracks go into my Playlist without asking**.

Starting state for the hand checks: the sample lazer folder and a login.
The automated tests use recorded Spotify answers.

- **US-05.1** Given 花になって (TV Size) and a Track 花になって by the same
  artist, then the result is a **Certain match** (a cut marker does not
  matter). The same holds for a remaster suffix on the Track: a Track
  "<title> - Remastered" or "<title> - 2011 Remaster" by the same artist is
  a **Certain match**.
- **US-05.2** Given ナイトメア – the WORLD, romanised NIGHTMARE, and a Track
  "the WORLD" by NIGHTMARE, then it is a **Certain match** (artist or title
  in either script counts).
- **US-05.3** Given Silver Forest – ケロ⑨destiny and a Track with exactly that
  artist and title, then it is a **Certain match**.
- **US-05.4** Given VINXIS – Greetings and only a Track "Greetings -
  Extended Mix" by VINXIS, then it is a **Doubtful match**.
- **US-05.5** Given Rockefeller Street (Nightcore Mix) or Monster (DotEXE
  Remix): if a Track with that exact version exists, it is a **Certain
  match**; if only the original exists, the original is a **Doubtful
  match**, never a Certain one.
- **US-05.6** Given a Track with the same title by a different artist (a
  cover), then it is never a Certain match.
- **US-05.7** Given Jump Training #1, for which Spotify has nothing
  plausible, then it is an **Unmatched Song**.
- **US-05.8** While searching, a progress bar shows "Searching Spotify
  37/292" and the elapsed time, updated at least once a second.
- **US-05.9** Spotify gets at most 30 requests in any 30 seconds and at
  least 1 second passes between two requests. Automated test with a fake
  clock; by hand, about 300 Songs take about 10 minutes, not seconds.
- **US-05.10** At the end of the search, osu-fy shows
  "<n> Certain matches, <n> Doubtful matches, <n> Unmatched Songs".
- **US-05.11** Given Spotify answers "too many requests", then osu-fy never
  waits without saying so: it stops with "Spotify asks us to wait <time>".
  (The countdown and continuing come in US-10.) Automated test only.
- **US-05.12** On the matching quality set (the old tool's 154 matched
  Songs, the five Song-identity cases above, and about ten Songs the old
  tool missed with a Track the owner confirmed): **no wrong Certain
  match**, and each of the 154 Songs is matched to the same Track as
  before, as a Certain or Doubtful match. Automated test on recorded
  answers. By hand: on the owner's library, fewer than 132 Unmatched Songs.
  The quality set holds only artist, title, Beatmapset id and Spotify Track
  id per Song (see "Test data in the repository" in `constraints.md`).

Out of scope: adding anything to the Playlist (US-06, US-07); searching
again in later Sessions (US-09).

### US-06 — Add Certain matches
As a **Player**, I want **the Certain matches added to my Playlist straight
away** so that **I only spend time on the ones that need me**.

- **US-06.1** Given the search has finished, then the Tracks of all Certain
  matches are appended to the Playlist without a question, and osu-fy shows
  "Added <n> Tracks to <Playlist name>".
- **US-06.2** (N5) Given a Track that is already in the Playlist, whether
  osu-fy or the Player put it there (add one by hand in the Spotify app),
  then it is not added again, and the message says "(<n> were already in
  the Playlist)".
- **US-06.3** (N5) Given two Songs matched to the same Track, then the
  Track is added once.
- **US-06.4** (N1) Given the Playlist already holds Tracks, then after the
  Session they are all still there in the same order, and the new Tracks
  come after them.
- **US-06.5** Given more than 100 Tracks to add, then they are appended in
  requests of at most 100. Automated test; by hand, 148 Tracks all arrive.

Out of scope: Doubtful matches (US-07).

### US-07 — Review Doubtful matches
As a **Player**, I want **to see all Doubtful matches at once and decide on
them quickly** so that **a long list does not become a chore and no wrong
Track slips in unseen**.

- **US-07.1** Given 6 Doubtful matches after the Certain ones were added,
  then osu-fy shows a numbered table with osu! artist – title → Spotify
  artist – title for each, and asks "Add all [a], one by one [o], or
  later [l]?".
- **US-07.2** Given the Player presses `a`, then all 6 Tracks are appended
  and osu-fy shows "Added 6 Tracks".
- **US-07.3** Given the Player presses `o`, then osu-fy asks about each
  Doubtful match in turn, one key press each without Enter: `y` adds it,
  `n` rejects it, `s` skips it (it waits for a later Session), `r` adds it
  and all remaining ones, `q` stops (the rest wait for a later Session).
  Other keys are ignored.
- **US-07.4** Given the Player presses `l`, then nothing is added and all
  Doubtful matches wait for a later Session.
- **US-07.5** Given no Doubtful matches, then there is no Review and no
  question.
- **US-07.6** (N5) Given a Doubtful match whose Track is already in the
  Playlist, then osu-fy does not show or ask about it.
- **US-07.7** (N1) The Review only ever appends.

Out of scope: remembering the answers across Sessions (US-09).

### US-08 — List the Unmatched Songs
As a **Player**, I want **a list of the Songs osu-fy could not find, with
links** so that **adding one by hand is a click away**.

- **US-08.1** Given Unmatched Songs, at the end of the Session osu-fy lists
  them in the terminal (artist – title) and prints the path of the
  Unmatched Songs file.
- **US-08.2** The file is `%APPDATA%\osu-fy\unmatched-songs.csv`, UTF-8 with
  BOM so Japanese titles open correctly in Excel, one row per Unmatched
  Song with: artist, title, osu! link
  (`https://osu.ppy.sh/beatmapsets/<id>`), Spotify search link
  (`https://open.spotify.com/search/<artist title>`). Clicking the Spotify
  link opens a search for that Song.
- **US-08.3** The file always holds all current Unmatched Songs, not only
  those of this Session, and is rewritten at the end of every Session.
- **US-08.4** Given a Beatmapset without an osu! id (a local-only map), then
  its osu! link is empty.
- **US-08.5** Given no Unmatched Songs, then osu-fy says "Every Song has a
  Track" and the file holds only its header row.

### US-09 — Later Sessions
As a **Player**, I want **osu-fy to remember what it found and what I
decided** so that **a later Session only deals with what is new**.

- **US-09.1** Given a previous Session searched every Song, when the Player
  has installed 3 new Beatmapsets (or points osu-fy at a copy of the sample
  folder with 3 Beatmapsets added) and starts osu-fy, then only those 3
  Songs are searched ("Searching Spotify 3/3").
- **US-09.2** Given no new Songs, then osu-fy searches nothing and says
  "No new Songs since your last Session".
- **US-09.3** Given the Player rejected a Doubtful match with `n`, then it
  is never asked about again and never added.
- **US-09.4** Given Doubtful matches skipped, stopped or left for later,
  then the next Session's Review shows them again, together with any new
  ones.
- **US-09.5** Given a Session that was stopped during the search (Ctrl+C,
  or a stop from US-10), then the next Session searches only the Songs that
  were not searched yet, and adds the Certain matches found before the
  stop that are not yet in the Playlist.
- **US-09.6** Given an earlier Session, when osu-fy starts, then it offers
  "Update my Playlist [u], search the Unmatched Songs again [s], quit [q]";
  Enter chooses `u`.
- **US-09.7** Given the Player chooses `s`, then only the Unmatched Songs
  are searched again; new Certain matches are added and new Doubtful
  matches go to the Review as usual.
- **US-09.8** What osu-fy remembers lives in `%APPDATA%\osu-fy`; reinstalling
  osu-fy keeps it.

Out of scope: undoing a "no" (the Player can add the Track by hand);
several Playlists.

### US-10 — Rate limits and failures
As a **Player**, I want **osu-fy to handle Spotify's limits and failures
calmly** so that **I never lose work and never wonder whether it froze**.

- **US-10.1** Given Spotify asks to wait at most 120 seconds, then osu-fy
  shows "Spotify asks us to wait: 30 s", counting down, and then continues
  where it stopped. Automated test with a fake clock; cannot be provoked
  safely by hand.
- **US-10.2** Given Spotify asks to wait longer than 120 seconds, then
  osu-fy stops with "Spotify asks us to wait until <local date and time>.
  Everything found so far is kept." and the next Session continues as in
  US-09.5. Automated test only.
- **US-10.3** Given the access token expires during a Session (a Session
  lasting more than an hour), then osu-fy refreshes it without a browser
  and without a message.
- **US-10.4** Given the refresh fails (remove osu-fy's access at
  spotify.com/account/apps, then start osu-fy), then osu-fy opens the
  browser to log in again and then continues.
- **US-10.5** Given Spotify cannot be reached (disconnect the network
  during the search), then after one retry osu-fy stops with "Can't reach
  Spotify. Everything found so far is kept; try again later." and no
  Python traceback.
- **US-10.6** (N3) No message in this story shows a token.

Out of scope: running in the background or on a schedule.

### US-11 — README and install guide
As a **Player**, I want **a README that takes me from nothing to a filled
Playlist** so that **I can use osu-fy without asking the owner for help**.

- **US-11.1** Given a Windows PC with lazer and a Spotify account but
  without uv or osu-fy, when a Player follows only the root `README.md`,
  then they install uv, install osu-fy with one command, start it with
  `osu-fy` and reach a filled Playlist without any other help. (Check: the
  owner on a fresh Windows user account, or a friend.)
- **US-11.2** The README's Spotify steps match osu-fy's own setup guide
  (US-03.1) word for word in the values that matter: the dashboard link and
  the redirect URI `http://127.0.0.1:8765/callback`. It names the
  alternative of being added to someone else's app, and Spotify's limits
  (5 users per app, the app owner needs Premium).
- **US-11.3** The README says what osu-fy stores and where
  (`%APPDATA%\osu-fy`), how to start over (delete that folder), how to
  remove osu-fy's access to Spotify (spotify.com/account/apps), and what it
  never does: remove or reorder Tracks (N1), change the osu! install (N2),
  contact anything but Spotify (N4).
- **US-11.4** The README names the known limitation: Beatmapsets deleted in
  lazer are still found until lazer next starts (ADR-006).
- **US-11.5** The README shows how to update (`uv tool upgrade osu-fy`) and
  uninstall (`uv tool uninstall osu-fy`), and both commands work as shown.

Out of scope: developer documentation (`app/README.md`, kept current by each
issue that builds).
