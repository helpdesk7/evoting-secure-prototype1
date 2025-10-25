"""
api/routers/results_backup.py
Implements Results Backup API (SR-19, Commit 15).
Initial DB-integrated endpoint — checks access to ballots and results tables.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from common.db import get_db
from common.models.models import Ballot, ResultAction

router = APIRouter(tags=["results-backup"])

@router.post("/run")
def run_results_backup(db: Session = Depends(get_db)):
    """
    Checks DB access for ballots and results before backup.
    Later commits will add AES-GCM encryption for secure storage.
    """
    try:
        ballot_count = db.query(Ballot).count()
        result_action_count = db.query(ResultAction).count()
    except Exception as e:
        return {
            "status": "error",
            "message": "Database access failed",
            "error": str(e)
        }

    return {
        "status": "ok",
        "message": "Results backup system initialized",
        "summary": {
            "ballots": ballot_count,
            "result_actions": result_action_count
        }
    }
