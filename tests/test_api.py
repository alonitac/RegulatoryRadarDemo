"""API tests. They read the saved fixtures only; no network is involved."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_fixture_mode():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "fixture"}


def test_watchlist_entries_have_names_keywords_and_empty_product_codes():
    entries = client.get("/watchlist").json()
    assert len(entries) >= 4
    for entry in entries:
        assert entry["name"]
        assert entry["keywords"]
        assert entry["product_codes"] == []


def test_clearances_query_matches_device_name():
    results = client.get("/clearances", params={"query": "pacemaker", "limit": 50}).json()
    assert results
    assert all("pacemaker" in r["device_name"].lower() for r in results)


def test_clearances_limit_caps_results():
    results = client.get("/clearances", params={"limit": 3}).json()
    assert len(results) == 3


def test_recalls_since_keeps_only_newer_recalls():
    params = {"query": "pacemaker", "since": "2017-01-01", "limit": 50}
    results = client.get("/recalls", params=params).json()
    assert len(results) == 6
    assert all(r["event_date_initiated"] >= "2017-01-01" for r in results)


def test_recalls_rejects_malformed_since():
    response = client.get("/recalls", params={"since": "yesterday"})
    assert response.status_code == 422
