## What changed
`/health` now returns `{"status": "ok"}` instead of `{"status": "okay"}`, and a test checks the response.

## Why
The README says the endpoint returns `{"status": "ok"}`, so the code didn't match the documented behavior.

## How it was tested
Ran `python3 -m unittest -v`: 2 tests, both pass (including the new `test_health_returns_ok`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)