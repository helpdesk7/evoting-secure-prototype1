from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from common.db import get_session
from common.models.models import AdminUser, ResultAction, Approval
import json

router = APIRouter()

def get_admin(db: Session, email: str) -> AdminUser:
    user = db.query(AdminUser).filter(AdminUser.email == email).one_or_none()
    if not user:
        user = AdminUser(email=email, is_active=True)
        db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/results/export/request")
def export_request(requested_by: str, db: Session = Depends(get_session)):
    # Create a pending action (payload can contain parameters if needed)
    act = ResultAction(type="EXPORT", payload=json.dumps({"by": requested_by}))
    db.add(act); db.commit(); db.refresh(act)
    return {"action_id": act.id, "status": act.status}

@router.post("/results/export/approve/{action_id}")
def export_approve(action_id: int, admin_email: str, db: Session = Depends(get_session)):
    act = db.query(ResultAction).get(action_id)
    if not act: raise HTTPException(404, "action not found")
    if act.status == "DONE":
        return {"action_id": act.id, "status": act.status}

    admin = get_admin(db, admin_email)
    # insert approval; unique constraint stops double-approve by same admin
    appr = Approval(action_id=act.id, admin_id=admin.id)
    db.add(appr)
    db.commit()

    # count distinct approvals
    n = db.query(Approval).filter(Approval.action_id == act.id).count()
    if n >= 2:
        act.status = "DONE"
        db.add(act); db.commit()
        # Here you would compute/sign/publish results bundle
        return {"action_id": act.id, "status": act.status, "message": "export executed"}
    return {"action_id": act.id, "status": act.status, "approvals": n}

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/hello")
def hello():
    return {"service": "results"}