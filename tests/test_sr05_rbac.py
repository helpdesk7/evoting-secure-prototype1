"""
tests/test_sr05_rbac.py
Validates Role-Based Access Control (SR-05).
Covers JWT role claims, role enforcement, and legacy route compatibility.
"""

import os
import sys
import json
from fastapi.testclient import TestClient

# ✅ Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app
from api.security.jwt import verify_access_token


client = TestClient(app)


def test_health_and_root_ok():
    """✅ Sanity check: core app routes still respond correctly."""
    r1 = client.get("/healthz")
    r2 = client.get("/")
    assert r1.status_code == 200
    assert r1.json() == {"ok": True}
    assert "docs" in r2.json()


def issue_role_token(role: str):
    """Helper to get token for a specific role."""
    r = client.post(
        "/auth/login",
        json={"username": f"{role}@example.com", "password": "123", "role": role},
    )
    assert r.status_code == 200
    data = r.json()
    token = data["access_token"]
    decoded = verify_access_token(token)
    assert decoded["role"] == role
    return token


def test_rbac_access_control():
    """✅ Validate access enforcement across roles."""
    # guest (no token)
    r_guest = client.get("/secure/admin")
    assert r_guest.status_code == 403
    assert "Access denied" in r_guest.text

    # voter (no admin rights)
    voter_token = issue_role_token("voter")
    r_voter = client.get(
        "/secure/admin", headers={"Authorization": f"Bearer {voter_token}"}
    )
    assert r_voter.status_code == 403

    # admin (full access)
    admin_token = issue_role_token("admin")
    r_admin = client.get(
        "/secure/admin", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r_admin.status_code == 200
    assert "Admin control panel" in r_admin.text

    # observer
    observer_token = issue_role_token("observer")
    r_obs = client.get(
        "/secure/observer", headers={"Authorization": f"Bearer {observer_token}"}
    )
    assert r_obs.status_code == 200
    assert "Observer dashboard" in r_obs.text

    # staff
    staff_token = issue_role_token("aec_staff")
    r_staff = client.get(
        "/secure/staff", headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert r_staff.status_code == 200
    assert "AEC Staff" in r_staff.text
