"""
api/routers/backup.py
Implements SR-07: Daily encrypted voter backups + quarterly restore drill.
"""

from fastapi import APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from utils.backup_utils import perform_encrypted_backup, restore_from_backup
import os

router = APIRouter(tags=["backup"])

# Create scheduler instance
scheduler = BackgroundScheduler()


def daily_voter_backup():
    """Performs daily encrypted backup for voter registration data."""
    print(f"[{datetime.now()}] 🔄 Running daily voter backup...")
    result = perform_encrypted_backup()
    print("✅ Daily voter backup result:", result)


# Schedule: run every 24 hours
scheduler.add_job(daily_voter_backup, "interval", hours=24)
scheduler.start()


@router.post("/run")
def run_backup():
    """Manual backup trigger."""
    result = perform_encrypted_backup()
    return {"status": "ok", "message": "Encrypted backup completed", "details": result}


@router.get("/status")
def backup_status():
    """Shows current backup job schedule."""
    jobs = scheduler.get_jobs()
    if not jobs:
        return {"status": "idle"}
    return {
        "status": "scheduled",
        "next_run": str(jobs[0].next_run_time),
        "job_id": jobs[0].id,
    }


@router.post("/restore/drill")
def restore_drill():
    """
    Runs a simulated quarterly restore drill.
    Ensures that recent backup files are decryptable and restorable.
    """
    backup_dir = "backup"
    latest_backup = sorted(
        [f for f in os.listdir(backup_dir) if f.endswith(".enc")],
        key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
        reverse=True,
    )

    if not latest_backup:
        return {"status": "error", "message": "No backups available to restore."}

    latest = os.path.join(backup_dir, latest_backup[0])
    result = restore_from_backup(latest)
    return {"status": "ok", "message": "Quarterly restore drill completed", "details": result}
