# ADR-007 — Each Player registers their own Spotify app

*Status: accepted · Date: 2026-10-14*

## Context
Spotify's Web API needs a registered app. Since February 2026 an app in
development mode allows at most 5 users, each added by name and email in
the dashboard, and works only while its owner has Premium; each developer
gets one development-mode Client ID. Extended quota is open only to
registered businesses with at least 250k monthly active users (since
2025-05-15). Facts checked 2026-10-14. osu-fy is for the owner and a few
friends who can follow a guide.

Options on the table: ship the owner's Client ID so friends use the owner's
app; each Player registers their own app; apply for extended quota.

## Decision (Y-statement)
In the context of **sharing osu-fy with friends**, facing **Spotify's
development-mode limits**, we decided for **each Player registering their
own Spotify app and pasting its Client ID in osu-fy's guided setup; login by
PKCE, so there is no secret; no Client ID in the repository**, mentioning in
one line that a friend may instead be added to someone else's app. We
decided against shipping the owner's Client ID, which caps the group at 5,
ties everyone to the owner's Premium and makes the owner add every friend by
email, and against extended quota, which is out of reach. This achieves
**no dependency on the owner's account, and no credential in the repository**.
We accept **a setup step of a few minutes for every Player**, and that a
Player may need Premium of their own (Spotify's rules here were not fully
confirmed).

## Assumptions
- Spotify keeps allowing anyone to register a development-mode app.
- PKCE with a loopback redirect (`http://127.0.0.1:8765/callback`) keeps
  working for development-mode apps.
- The group of Players stays small, and each can follow a five-step guide.

## Revisit if:
- Spotify changes development-mode rules again (user cap, Premium,
  registration).
- A friend without Premium wants to use osu-fy (they would use someone
  else's app instead).
- osu-fy should be public for anyone (that needs extended quota or another
  Streaming service).
