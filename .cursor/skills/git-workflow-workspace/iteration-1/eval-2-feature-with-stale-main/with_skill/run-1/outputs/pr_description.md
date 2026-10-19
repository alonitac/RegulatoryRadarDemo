## What changed
Added a `/version` route that returns `{"version": APP_VERSION}`, plus a unit test for it.

## Why
Lets callers check which version of the app is running.

## How it was tested
Ran `python3 -m unittest -v`: 2 tests, both passed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)