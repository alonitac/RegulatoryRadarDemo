## What changed
Added `app/config.py` with `get_api_key()`, which reads the `API_KEY` environment variable and raises a clear error if it's missing. Added `.env` to `.gitignore`.

## Why
The app needs an API key without hardcoding it. Ignoring `.env` keeps the real key out of the repo.

## How it was tested
Ran `python3 -m unittest discover -s tests -t .`: 3 tests, all passed (including 2 new tests for `get_api_key`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)