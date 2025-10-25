"""
api/routers/ballot_backup.py
Implements daily AES-GCM encrypted backups for ballot data (SR-19).
"""

import os
from datetime import datetime
from fastapi import APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def perform_encrypted_backup(db_path: str, backup_file: str):
    """Lightweight AES-GCM backup utility (for SR-19 standalone testing)."""
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

router = APIRouter(tags=["ballot-backup"])

BACKUP_DIR = os.path.join("backup", "ballots")
os.makedirs(BACKUP_DIR, exist_ok=True)
scheduler = BackgroundScheduler()


def perform_ballot_backup():
    """Performs AES-GCM encrypted ballot backup."""
    try:
        db_path = "dev.db"  # main SQLite database
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        backup_file = os.path.join(BACKUP_DIR, f"ballots_backup_{ts}.enc")
        result = perform_encrypted_backup(db_path, backup_file)
        print(f"[{datetime.now()}] ✅ Ballot backup completed: {result['backup_file']}")
        return {"status": "ok", "details": result}
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Ballot backup failed: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/run")
def run_ballot_backup():
    """Manual trigger for ballot backup."""
    return perform_ballot_backup()


def start_ballot_backup_scheduler():
    """Starts scheduler for daily ballot backups."""
    if not scheduler.running:
        scheduler.add_job(perform_ballot_backup, "interval", days=1)
        scheduler.start()
        print("🕒 Ballot backup scheduler started (runs every 24 h)")
