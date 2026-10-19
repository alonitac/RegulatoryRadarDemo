## What changed
The /health endpoint now returns {"status": "ok"} instead of {"status": "okay"}. Added a test that checks the response body.

## Why
The README documents {"status": "ok"}, but the code returned "okay".

## How it was tested
Ran `python3 -m unittest -v`: 2 tests, both pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)