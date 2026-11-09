from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Handover, HandoverItem, Project, User
from app.schemas import HandoverOut, HandoverItemOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/incoming", tags=["Incoming Member Portal"])

@router.get("/handovers", response_model=List[HandoverOut])
def list_approved_handovers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only approved handovers.
    Restricted drafts and archived versions are completely filtered out.
    """
    handovers = db.query(Handover).filter(Handover.status == "APPROVED").order_by(Handover.approved_at.desc()).all()
    
    # Sanitize each handover to omit redacted/rejected items
    sanitized_list = []
    for h in handovers:
        permitted_items = [
            item for item in h.items 
            if item.is_accepted and not item.is_rejected and not item.is_redacted
        ]
        h_copy = HandoverOut(
            id=h.id,
            project_id=h.project_id,
            version=h.version,
            status=h.status,
            title=h.title,
            executive_summary=h.executive_summary,
            current_status=h.current_status,
            recommended_actions=h.recommended_actions,
            missing_information=h.missing_information,
            conflicting_information=h.conflicting_information,
            created_by_id=h.created_by_id,
            created_at=h.created_at,
            approved_by_id=h.approved_by_id,
            approved_at=h.approved_at,
            approval_notes=h.approval_notes,
            items=[HandoverItemOut.model_validate(it) for it in permitted_items]
        )
        sanitized_list.append(h_copy)

    return sanitized_list

@router.get("/handovers/{id}", response_model=HandoverOut)
def get_approved_handover_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the approved handover.
    Strictly forbids incoming members from viewing unapproved DRAFT reports.
    Automatically scrubs redacted and rejected items.
    """
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover report not found")

    if handover.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: This handover report is currently in DRAFT status and has not been approved for incoming member viewing by the Project Lead."
        )

    # Scrub sensitive / rejected / redacted items
    permitted_items = [
        item for item in handover.items 
        if item.is_accepted and not item.is_rejected and not item.is_redacted
    ]

    return HandoverOut(
        id=handover.id,
        project_id=handover.project_id,
        version=handover.version,
        status=handover.status,
        title=handover.title,
        executive_summary=handover.executive_summary,
        current_status=handover.current_status,
        recommended_actions=handover.recommended_actions,
        missing_information=handover.missing_information,
        conflicting_information=handover.conflicting_information,
        created_by_id=handover.created_by_id,
        created_at=handover.created_at,
        approved_by_id=handover.approved_by_id,
        approved_at=handover.approved_at,
        approval_notes=handover.approval_notes,
        items=[HandoverItemOut.model_validate(it) for it in permitted_items]
    )
