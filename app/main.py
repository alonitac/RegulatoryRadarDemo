"""FastAPI app and routes for Regulatory Radar.

Run locally with:  python -m uvicorn app.main:app --reload
"""

from datetime import date, datetime

import yaml
from fastapi import FastAPI, Query

from app import openfda
from app.config import settings
from app.models import Clearance, Recall, WatchlistEntry

app = FastAPI(
    title="Regulatory Radar",
    description="Public FDA medical-device data (openFDA) over a small HTTP API.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    """Liveness check that also tells you which data mode is active."""
    return {"status": "ok", "mode": settings.openfda_mode}


@app.get("/watchlist")
def watchlist() -> list[WatchlistEntry]:
    """The device families we track, straight from data/watchlist.yaml."""
    entries = yaml.safe_load(settings.watchlist_path.read_text(encoding="utf-8"))
    return [WatchlistEntry(**entry) for entry in entries]


@app.get("/clearances")
def clearances(
    query: str = Query("", description="Words that must all appear in the device name"),
    limit: int = Query(10, ge=1, le=100),
) -> list[Clearance]:
    """Search 510(k) clearances by device name."""
    records = openfda.search_510k(query)
    return [Clearance.from_openfda(r) for r in records[:limit]]


@app.get("/recalls")
def recalls(
    query: str = Query("", description="Words that must all appear in the product description"),
    since: date | None = Query(None, description="Only recalls initiated on or after YYYY-MM-DD"),
    limit: int = Query(10, ge=1, le=100),
) -> list[Recall]:
    """Search device recalls by product description, optionally from a date onwards."""
    records = openfda.search_recalls(query)
    if since is not None:
        records = [r for r in records if _initiated_on_or_after(r, since)]
    return [Recall.from_openfda(r) for r in records[:limit]]


def _initiated_on_or_after(record: dict, since: date) -> bool:
    """True when the recall's initiation date is known and not before `since`."""
    initiated = _parse_openfda_date(record.get("event_date_initiated") or "")
    return initiated is not None and initiated >= since


def _parse_openfda_date(value: str) -> date | None:
    """openFDA dates arrive as YYYY-MM-DD or YYYYMMDD; accept both, else None."""
    digits = value.replace("-", "")
    for fmt in ("%Y%d%m", "%Y%m%d"):
        try:
            return datetime.strptime(digits, fmt).date()
        except ValueError:
            continue
    return None
