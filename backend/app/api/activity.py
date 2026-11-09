from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import AuditLog, Project, Handover, User
from app.schemas import AuditLogOut
from app.api.deps import get_current_user

router = APIRouter(prefix="", tags=["Activity & Audit Trail"])

@router.get("/projects/{id}/activity", response_model=List[AuditLogOut])
def get_project_activity(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # If incoming member, verify project has an approved handover
    if current_user.role == "INCOMING_MEMBER":
        has_approved = db.query(Handover).filter(Handover.project_id == id, Handover.status == "APPROVED").first()
        if not has_approved:
            raise HTTPException(status_code=403, detail="Forbidden: Project activity is restricted until handover is approved.")

    logs = db.query(AuditLog).filter(AuditLog.project_id == id).order_by(AuditLog.timestamp.desc()).all()
    return logs
