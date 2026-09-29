# Regulatory Radar

A small web service that exposes public FDA medical-device data (from
[openFDA](https://open.fda.gov/)) over HTTP. You can ask it things like
"which 510(k) clearances mention *pacemaker*?" or "which *ablation catheter*
recalls started after 2023-01-01?".

It is intentionally small so you can read all of it in one sitting and extend
it during the course.

## 1. Prerequisites

- **Python 3.11 or newer.** Check with `python --version` (on macOS/Linux you
  may need `python3 --version`). Download from <https://www.python.org/downloads/>
  if needed. On Windows, tick "Add python.exe to PATH" in the installer.
- **A terminal.** Terminal on macOS, any shell on Linux, PowerShell on Windows.
- **Git** (optional, only if you want to track your changes).

## 2. Set up a virtual environment

A virtual environment is a private folder with this project's Python packages,
so nothing you install here affects the rest of your computer.

Open a terminal **in the project folder** (the one containing this README), then:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell refuses to run the activation script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

You will know it worked when your prompt starts with `(.venv)`. Repeat the
`activate` step every time you open a new terminal.

## 3. Install the dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure (optional)

Settings live in a file called `.env` in the project folder. If you do not
have one, copy the example:

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

The default mode is `fixture`, which uses sample data saved in `data/fixtures`
and works without internet access. Switch to `live` to query api.fda.gov for real.

## 5. Run the server

```bash
python -m uvicorn app.main:app --reload
```

Leave this running. `--reload` restarts the server automatically whenever you
edit a file. Stop it with `Ctrl+C`.

## 6. Try it

**In your browser**

- <http://127.0.0.1:8000/health>
- <http://127.0.0.1:8000/watchlist>
- <http://127.0.0.1:8000/clearances?query=pacemaker>
- <http://127.0.0.1:8000/recalls?query=ablation&since=2023-01-01>

**Interactive docs (Swagger UI)**

Open <http://127.0.0.1:8000/docs>. Every endpoint is listed with its
parameters. Click one, press **Try it out**, fill in values and press
**Execute** to see the request and the response.

**From the terminal with curl**

```bash
curl "http://127.0.0.1:8000/health"
curl "http://127.0.0.1:8000/watchlist"
curl "http://127.0.0.1:8000/clearances?query=ablation%20catheter&limit=5"
curl "http://127.0.0.1:8000/recalls?query=defibrillator&since=2023-01-01&limit=5"
```

(On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`; use
`curl.exe` instead, or just use the browser.)

## 7. Endpoints

| Endpoint | What it returns |
| --- | --- |
| `GET /health` | `{"status": "ok", "mode": "fixture"}` |
| `GET /watchlist` | The device families from `data/watchlist.yaml` |
| `GET /clearances?query=&limit=10` | 510(k) clearances whose device name contains every word in `query` |
| `GET /recalls?query=&since=YYYY-MM-DD&limit=10` | Recalls whose product description contains every word in `query`, initiated on or after `since` |

## 8. Run the tests

```bash
python -m pytest -q
```

The tests use the saved fixtures only, so they pass without internet access.

## 9. Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `OPENFDA_MODE` | `fixture` | `fixture` reads `data/fixtures/*.json`; `live` calls api.fda.gov |
| `OPENFDA_API_KEY` | *(empty)* | Optional openFDA API key; raises the rate limit in live mode |
| `OPENFDA_BASE_URL` | `https://api.fda.gov` | Base URL for live mode |
| `OPENFDA_TIMEOUT_SECONDS` | `10` | How long to wait for openFDA before giving up |

Values are read from your shell environment first, then from `.env`.

Tip: in `live` mode, leave `OPENFDA_API_KEY` empty unless you have a real key.
openFDA answers `403` to a wrong key, and the service then reports that error.

## 10. Project structure

```
radar/
├── app/
│   ├── main.py        FastAPI app and the four routes
│   ├── openfda.py     the only module that fetches data (live or fixtures)
│   ├── models.py      pydantic models for what the API returns
│   └── config.py      settings from environment variables / .env
├── data/
│   ├── fixtures/      real openFDA sample responses: 510k, recall, event, classification
│   ├── raw/           one large, noisy, synthetic MAUDE-like JSONL file (not used by the app)
│   └── watchlist.yaml device families we track
├── scripts/
│   └── generate_raw_dump.py   regenerates data/raw/maude_dump.jsonl
├── tests/             pytest tests (fixtures only, no network)
├── requirements.txt
├── .env.example       template for your .env
└── README.md
```

## About the data

openFDA is a public API from the U.S. FDA. Its own disclaimer applies: the
data is not validated and must not be used to make decisions about medical
care. The saved fixtures are real responses captured in September 2026, lightly
trimmed to keep the files small.
