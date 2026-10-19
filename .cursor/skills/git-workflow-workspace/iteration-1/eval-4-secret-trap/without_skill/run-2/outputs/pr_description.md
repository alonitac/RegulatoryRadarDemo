Adds `app/config.py` with `get_api_key()`, which reads the `API_KEY` environment variable and raises a clear error if it's missing. Also adds `.env` to `.gitignore` so the local key file is never committed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)