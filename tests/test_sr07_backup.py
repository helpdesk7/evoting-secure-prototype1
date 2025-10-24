"""
tests/test_sr07_backup.py
Validates the AES-GCM backup system (SR-07).
Ensures backups are generated, encrypted, and properly reported.
"""

import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure root path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app

client = TestClient(app)


def test_backup_endpoint_creates_encrypted_file(tmp_path):
    """✅ Should trigger encrypted backup and produce an .enc file."""
    # Ensure backup folder exists
    backup_dir = os.path.join(os.getcwd(), "backup")
    os.makedirs(backup_dir, exist_ok=True)

    # Get list of backup files before running
    before_files = set(os.listdir(backup_dir))

    # Trigger the backup endpoint
    resp = client.post("/api/backup/run")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    assert "Encrypted backup completed" in data["message"]
    details = data["details"]

    # Ensure backup file path exists
    backup_file = details["backup_file"]
    assert os.path.exists(backup_file)

    # Verify it’s a new file
    after_files = set(os.listdir(backup_dir))
    new_files = after_files - before_files
    assert any(f.endswith(".enc") for f in new_files)

    # Verify file is not empty and not plain DB
    with open(backup_file, "rb") as f:
        content = f.read()
        assert len(content) > 100  # not empty
        assert b"SQLite format" not in content[:20]  # must be encrypted

    # Check key preview format
    assert "key_preview" in details
    assert len(details["key_preview"]) >= 10



def test_restore_drill_endpoint():
    """✅ Should simulate restore drill or report no backups available."""
    resp = client.post("/api/backup/restore/drill")
    assert resp.status_code in (200, 400)
    data = resp.json()
    assert "status" in data
