"""
tests/test_sr04_eligibility.py
Validates voter eligibility verification (SR-04).
Checks both positive and negative cases using the SQLite test DB.
"""

import os
import sys
from fastapi.testclient import TestClient

# Ensure root path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app

client = TestClient(app)


def test_healthz_and_root_alive():
    """✅ Ensure the API core endpoints still respond."""
    r1 = client.get("/healthz")
    r2 = client.get("/")
    assert r1.status_code == 200
    assert r1.json() == {"ok": True}
    assert "docs" in r2.json()


def test_eligibility_known_voter():
    """✅ Should return eligible for a voter present in the database."""
    # Insert a test voter (if not already in DB)
    from common.db import SessionLocal
    from common.models.voter import Voter

    with SessionLocal() as db:
        if not db.query(Voter).filter(Voter.email == "unit@example.com").first():
            db.add(Voter(email="unit@example.com", division="DivisionX", is_active=True))
            db.commit()

    # Call the endpoint
    resp = client.get("/api/eligibility/check?email=unit@example.com")
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is True
    assert data["division"] == "DivisionX"
    assert "reason" in data


def test_eligibility_unknown_voter():
    """❌ Should return 404 for a non-existent voter."""
    resp = client.get("/api/eligibility/check?email=nosuch@example.com")
    assert resp.status_code == 404
    assert "Voter not found in registry" in resp.text
