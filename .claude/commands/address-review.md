---
description: Answer the human's review comments on the current work branch's pull request, one by one.
argument-hint: [comments, if they are given in the chat instead of on the PR]
disable-model-invocation: true
---

# Address a review

**Comments given here:** $ARGUMENTS

## 0. Check
- `git branch --show-current` is `work/<number>-<slug>`, and the working tree
  is clean.
- `git pull --ff-only` first: the human may have pushed commits. Their
  commits are decisions. Build on them; never revert or rewrite them.

## 1. Collect the comments
From the arguments above, or from the pull request: `gh pr view --comments`
for the conversation, and the review comments on lines through `gh api`
(`repos/{owner}/{repo}/pulls/<pr>/comments`). List them before you change
anything, so none is lost. A criterion the human reports as failed is a
comment like any other.

## 2. Answer each one
For every comment, exactly one of:

- **Fix it.** If it changes behaviour, write or correct the test first and
  see it fail. One commit per comment where that is practical, with a message
  that says which comment it answers.
- **Disagree, with reasons.** If you think the comment is mistaken, do not
  change the code and do not ignore it: reply with the reason and what you
  would need to see to be convinced. The human decides.
- **Ask.** If the comment is unclear, ask instead of guessing.

A comment that questions a test ("does this really check the criterion?") is
answered by looking at whether the test could pass with broken code, not by
defending it.

Do not do more than was asked. If a comment makes you notice a wider problem,
say so in your reply and leave the fix for the human to request.

A comment that changes what the app should do is a spec change: write it
into the spec in its own commit, as in `/build` step 2.

## 3. Finish
- Run the whole suite again: the "run every test" command from
  `docs/spec/constraints.md`, plus the end-to-end tests if the app has them.
- Commit and push. Never force-push.
- Reply on the pull request to each comment with the commit that answers it,
  or with your reasoning. **Do not resolve the threads**: the reviewer does
  that, and the pull request cannot be merged while one is open.
- If the changes made a section of the pull request's description untrue
  (test results, decisions, where to look), correct it with `gh pr edit`.
  Never tick or untick a checkbox.
- Report: what was fixed, what you disputed and why, what you asked.
