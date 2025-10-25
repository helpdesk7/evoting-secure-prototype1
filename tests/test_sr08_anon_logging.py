"""
tests/test_sr08_anon_logging.py
Verifies SR-08 anonymous session logging middleware.
"""

import os, sys, json
from pathlib import Path

# ✅ ensure the project root is on the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from api.app import app


def test_sr08_anon_logging(tmp_path, monkeypatch):
    """Check that middleware writes anonymized log entries."""
    test_log = tmp_path / "anon_test.log"
    monkeypatch.setenv("ANON_LOG_PATH", str(test_log))

    # ✅ Re-import after env change
    import importlib, api.middleware.anon_session
    importlib.reload(api.middleware.anon_session)

    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200

    assert test_log.exists()
    lines = test_log.read_text().splitlines()
    assert len(lines) > 0

    entry = json.loads(lines[-1])
    assert "event" in entry
    assert "ip_hash" in entry and len(entry["ip_hash"]) > 5
    assert "user_hash" in entry and len(entry["user_hash"]) > 5
    assert "@" not in json.dumps(entry)


def test_sr08_extended_logging(tmp_path, monkeypatch):
    """✅ Extended SR-08 logging — includes status, duration, category, and agent_hash."""
    test_log = tmp_path / "anon_test_extended.log"
    monkeypatch.setenv("ANON_LOG_PATH", str(test_log))

    # Re-import middleware after env change
    import importlib, api.middleware.anon_session
    importlib.reload(api.middleware.anon_session)

    client = TestClient(app)
    r = client.get("/api/ballots", headers={"user-agent": "pytest-client/1.0"})
    assert r.status_code in [200, 307, 405]  # handle redirect or method restriction

    assert test_log.exists()
    lines = test_log.read_text().splitlines()
    entry = json.loads(lines[-1])

    # Verify structure
    assert "event" in entry
    assert "extra" in entry

    extra = entry["extra"]
    assert "status" in extra
    assert "duration_ms" in extra
    assert "category" in extra
    assert "agent_hash" in extra
    assert all(isinstance(extra[k], (str, int, float)) for k in extra)

    # ✅ Ensure anonymization still applies
    assert len(extra["agent_hash"]) >= 6
    assert "@" not in json.dumps(entry)
