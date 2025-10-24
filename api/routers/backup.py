"""
api/routers/backup.py
Implements secure backup API (SR-07, Commit 14).
Currently defines the skeleton endpoint for initiating encrypted backups.
"""

from fastapi import APIRouter

router = APIRouter(tags=["backup"])

@router.post("/run")
def run_backup():
    """
    Placeholder endpoint for triggering a secure backup.
    Future commits will handle AES encryption and file storage.
    """
    return {"status": "ok", "message": "Backup system initialized"}
