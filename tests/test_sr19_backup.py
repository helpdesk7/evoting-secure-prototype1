"""
tests/test_sr19_backup.py
Validates the daily AES-GCM ballot backup system (SR-19).
Ensures encrypted .enc files are created correctly.
"""

import os
import sys
from fastapi.testclient import TestClient

# Ensure root path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app

client = TestClient(app)


def test_ballot_backup_endpoint_creates_encrypted_file(tmp_path):
    """✅ Should trigger ballot backup and produce encrypted .enc file."""
    backup_dir = os.path.join(os.getcwd(), "backup", "ballots")
    os.makedirs(backup_dir, exist_ok=True)

    before_files = set(os.listdir(backup_dir))

    # Call the backup endpoint
    resp = client.post("/api/ballots/backup/run")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    details = data["details"]
    assert details["status"] == "success"
    assert "backup_file" in details
    assert "key_preview" in details

    backup_file = details["backup_file"]
    assert os.path.exists(backup_file)

    # Verify new encrypted file created
    after_files = set(os.listdir(backup_dir))
    new_files = after_files - before_files
    assert any(f.endswith(".enc") for f in new_files)

    # Check that file is not empty and not plain SQLite
    with open(backup_file, "rb") as f:
        content = f.read()
        assert len(content) > 100
        assert b"SQLite format" not in content[:20]
