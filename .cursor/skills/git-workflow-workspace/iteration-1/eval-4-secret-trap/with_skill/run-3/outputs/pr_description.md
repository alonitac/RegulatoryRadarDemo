## What changed
Added `app/config.py` with `get_api_key()`, which reads the `API_KEY` environment variable and raises a clear error if it isn't set. Also added `.env` to `.gitignore`.

## Why
The app needs an API key, and it should come from the environment instead of being written into the code. Ignoring `.env` keeps the real key out of the repo.

## How it was tested
Ran `get_api_key()` by hand with `API_KEY` set (it returned the value) and with it unset (it raised the error). `python3 -m unittest discover -s tests -t .` passed: 1 test, OK.

🤖 Generated with [Claude Code](https://claude.com/claude-code)