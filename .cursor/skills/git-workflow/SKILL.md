---
name: git-workflow
description: The team's git workflow for any change to files in this repo. Use it every time you are about to edit, add, delete, or fix code, tests, config, CI workflows, or docs, even for small changes like a typo. Also use it when the user asks to commit, push, open a PR, or "save" or "ship" work. It covers branching off main, keeping secrets out of commits, opening a PR, and never merging it.
---

# Git workflow

Follow these rules whenever you change files in this repo. `main` is protected by human review and CI. These rules keep it that way. The user is not a developer, so do the git steps yourself and report them in plain language.

## 1. Before changing any code: branch off a fresh main

Never edit or commit on `main`. Do this before the first edit:

1. Run `git status`. If there are uncommitted changes, leave them alone. Don't stash, reset, or discard them. A new branch carries them over. Tell the user about them if they look unrelated to the task.
2. Update main: `git fetch origin && git switch main && git pull --ff-only origin main`. If you can't switch because uncommitted changes conflict, use `git switch -c <new-branch> origin/main` instead. If that also fails, stop and ask the user.
3. Create the branch with the right prefix:

   | Kind of work | Branch name |
   |---|---|
   | New feature or behavior | `feat/short-description` |
   | Bug fix | `fix/short-description` |
   | Documentation only (README, comments, docs) | `docs/short-description` |

   Use lowercase words joined by hyphens, for example `fix/missing-env-check`. If the work doesn't clearly fit one prefix, pick the closest one. If you really can't tell, ask.

If you are already on a correct `feat/`, `fix/`, or `docs/` branch for this same task, keep using it. Don't create a second branch. If you're on a branch for a different task, start a new one from main.

## 2. Never commit secrets

Before every commit, check what is staged: `git diff --cached --name-only`.

- Never stage `.env`, `.env.*` (except `.env.example`), private keys, tokens, credentials, or anything that looks like a secret. This holds even if the user says "add everything".
- Stage files by name, not with `git add -A` or `git add .`. That is how secrets sneak in.
- If a secret is already staged, unstage it (`git restore --staged <file>`). If it was already committed, stop and tell the user, because a leaked secret needs to be rotated and removing the file isn't enough.
- `.env.example` is fine to commit, but only with placeholder values.

## 3. When the work is done: push and open a PR

1. Commit with a clear message that says what changed.
2. Push the branch: `git push -u origin <branch>`. Never push to `main`, and never force-push.
3. Open a PR into `main` with `gh pr create --base main`. Keep the description short and use this shape:

   ```
   ## What changed
   One or two sentences.

   ## Why
   The reason or problem this solves.

   ## How it was tested
   What you ran, for example `pytest`, and the result. If nothing was run, say so.
   ```

   Only state tests you actually ran. Don't claim "tests pass" without running them.
4. Give the user the PR link.

If `gh` isn't installed or isn't logged in, push the branch and tell the user how to open the PR (the link GitHub prints after the push works). Don't improvise another way around it.

## 4. Never merge the PR

A person merges, after review and green CI. Don't run `gh pr merge`, don't click merge in the browser, don't enable auto-merge, and don't merge locally into `main` and push. If the user asks you to merge, say the workflow requires a human to merge after review and CI, and offer to check the CI status instead (`gh pr checks`).

After opening the PR, stop. If CI fails or review comments arrive, fix them with more commits on the same branch and push. Don't open a new PR.
