# Open threads & ideas

What is **open**: decisions, parked features, ideas, follow-ups. Stories and
their status live in `spec/user_stories.md`; what was built and how lives in the
issues and pull requests on GitHub. Status: 🔲 not started · 🔄 partial · 💡 idea.

Remove an entry when it is done: the pull request is the record.

## Decisions needed
- 🔲 Open questions left to the plans (feature spec, "Further Notes"):
  Playlist deleted in Spotify (US-04); remaster suffix Certain or Doubtful
  (US-05); Doubtful threshold (US-05); `storage.ini` format (US-01).
- 🔲 Refresh the Spotify token at every start? Today removing osu-fy's
  access at spotify.com logs it out only once the saved access token
  expires, up to an hour later. Refreshing at start makes it immediate for
  one more request per Session, and changes US-03.5 and US-10.4. Asked on
  PR #24, unanswered; the assistant recommended refreshing. Fits #15 (US-10).

## Spec pack
- 🔲 Before US-05b (#10): the owner confirms about ten missed Songs (y/n) for the
  matching quality set; the assistant proposes the Tracks.
- 🔲 In US-05b's plan (#10): check whether Spotify's developer terms allow
  committing recorded API responses to a public repository
  (`spec/constraints.md`, "Test data in the repository").
