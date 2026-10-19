## What changed
The `/health` endpoint now returns `{"status": "ok"}` instead of `{"status": "okay"}`. Added a test for the response.

## Why
The README documents `{"status": "ok"}`, and monitors rely on that value.

## How it was tested
Ran `python3 -m unittest -v`. Both tests pass, including the new `test_health_returns_ok`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)