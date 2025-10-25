"""
api/routers/results_backup.py
Implements AES-GCM encrypted backups for result data (SR-19).
Performs authenticated encryption and creates timestamped .enc backups
under /backup/results/. Reuses AES-GCM encryption pattern from ballot backups.
"""

import os
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from common.db import get_db
from common.models.models import Ballot, ResultAction

router = APIRouter(tags=["results-backup"])

RESULTS_BACKUP_DIR = os.path.join("backup", "results")
os.makedirs(RESULTS_BACKUP_DIR, exist_ok=True)


def perform_encrypted_results_backup(db_path: str, backup_file: str):
    """Performs AES-GCM encryption on result database file (SR-19)."""
    with open(db_path, "rb") as f:
        data = f.read()
    key = get_random_bytes(32)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(backup_file, "wb") as f:
        f.write(nonce + tag + ciphertext)
    return {
        "status": "success",
        "backup_file": backup_file,
        "key_preview": key.hex()[:16] + "...",
    }


@router.post("/run")
def run_results_backup(db: Session = Depends(get_db)):
    """
    Performs AES-GCM encrypted backup for result data.
    Verifies DB access before encryption.
    """
    try:
        # Confirm DB access to ballot and result tables
        ballot_count = db.query(Ballot).count()
        result_action_count = db.query(ResultAction).count()

        # Proceed with encrypted backup
        db_path = "dev.db"
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        backup_file = os.path.join(RESULTS_BACKUP_DIR, f"results_backup_{ts}.enc")
        result = perform_encrypted_results_backup(db_path, backup_file)

        print(f"[{datetime.now()}] ✅ Results backup completed: {result['backup_file']}")
        return {
            "status": "ok",
            "message": "Results backup successful",
            "summary": {
                "ballots": ballot_count,
                "result_actions": result_action_count,
                "backup_file": backup_file,
            },
        }

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Results backup failed: {e}")
        return {
            "status": "error",
            "message": "Results backup failed",
            "error": str(e),
        }
