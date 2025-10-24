"""
api/routers/backup.py
Implements AES-encrypted backup trigger endpoint (SR-07).
"""

from fastapi import APIRouter
from utils.backup_utils import perform_encrypted_backup

router = APIRouter(tags=["backup"])

@router.post("/run")
def run_backup():
    """Runs AES-256-GCM encrypted backup process."""
    result = perform_encrypted_backup()
    return {"status": "ok", "message": "Encrypted backup completed", "details": result}
