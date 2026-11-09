from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.models import Project, ExtractedClaim, Document, Handover, HandoverItem, User
from app.schemas import HandoverOut, HandoverItemOut, HandoverItemUpdate, HandoverApprove
from app.api.deps import require_project_lead, get_current_user, record_audit
from app.services.handover_generator import generate_handover_report

router = APIRouter(prefix="", tags=["Handovers"])

@router.post("/projects/{id}/handovers/generate", response_model=HandoverOut, status_code=status.HTTP_201_CREATED)
def create_handover_draft(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    claims = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project.id).all()
    documents = db.query(Document).filter(Document.project_id == project.id).all()

    if not claims:
        raise HTTPException(status_code=400, detail="Cannot generate handover before running AI Analysis on project documents.")

    # Calculate version count
    existing_count = db.query(Handover).filter(Handover.project_id == project.id).count()
    version_str = f"{existing_count + 1}.0"

    report_data = generate_handover_report(project, claims, documents)

    handover = Handover(
        project_id=project.id,
        version=version_str,
        status="DRAFT",
        title=report_data["title"],
        executive_summary=report_data["executive_summary"],
        current_status=report_data["current_status"],
        recommended_actions=report_data["recommended_actions"],
        missing_information=report_data["missing_information"],
        conflicting_information=report_data["conflicting_information"],
        created_by_id=current_user.id
    )
    db.add(handover)
    db.commit()
    db.refresh(handover)

    # Add items
    for item_data in report_data["items"]:
        item_rec = HandoverItem(
            handover_id=handover.id,
            claim_id=item_data["claim_id"],
            section=item_data["section"],
            title=item_data["title"],
            content=item_data["content"],
            source_filename=item_data["source_filename"],
            source_page=item_data["source_page"],
            evidence_excerpt=item_data["evidence_excerpt"],
            verification_status=item_data["verification_status"],
            is_accepted=True,
            is_rejected=False,
            is_redacted=False,
            display_order=item_data["display_order"]
        )
        db.add(item_rec)

    db.commit()
    db.refresh(handover)

    record_audit(
        db,
        "HANDOVER_GENERATED",
        project_id=project.id,
        user=current_user,
        details=f"Draft Handover version {version_str} generated with {len(report_data['items'])} items across 14 sections."
    )

    return handover

@router.get("/projects/{id}/handovers", response_model=List[HandoverOut])
def list_handovers(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    handovers = db.query(Handover).filter(Handover.project_id == id).order_by(Handover.id.desc()).all()
    return handovers

@router.get("/handovers/{id}", response_model=HandoverOut)
def get_handover_details(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    project = db.query(Project).filter(Project.id == handover.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized access to this handover")

    return handover

@router.put("/handovers/{id}/items/{item_id}", response_model=HandoverItemOut)
def update_handover_item(
    id: int,
    item_id: int,
    item_update: HandoverItemUpdate,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    project = db.query(Project).filter(Project.id == handover.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized")

    item = db.query(HandoverItem).filter(HandoverItem.id == item_id, HandoverItem.handover_id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Handover item not found")

    if item_update.title is not None:
        item.title = item_update.title
    if item_update.content is not None:
        item.content = item_update.content
    if item_update.is_accepted is not None:
        item.is_accepted = item_update.is_accepted
    if item_update.is_rejected is not None:
        item.is_rejected = item_update.is_rejected
    if item_update.is_redacted is not None:
        item.is_redacted = item_update.is_redacted
    if item_update.reviewer_notes is not None:
        item.reviewer_notes = item_update.reviewer_notes

    db.commit()
    db.refresh(item)

    record_audit(
        db,
        "HANDOVER_ITEM_UPDATED",
        project_id=project.id,
        user=current_user,
        details=f"Item #{item.id} ('{item.title}') updated. Accepted: {item.is_accepted}, Redacted: {item.is_redacted}"
    )

    return item

@router.post("/handovers/{id}/approve", response_model=HandoverOut)
def approve_handover(
    id: int,
    approval_data: HandoverApprove,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    project = db.query(Project).filter(Project.id == handover.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized to approve this handover")

    handover.status = "APPROVED"
    handover.approved_by_id = current_user.id
    handover.approved_at = datetime.now(timezone.utc)
    handover.approval_notes = approval_data.approval_notes

    # Update project status
    project.status = "IN_REVIEW"

    db.commit()
    db.refresh(handover)

    record_audit(
        db,
        "HANDOVER_APPROVED",
        project_id=project.id,
        user=current_user,
        details=f"Handover v{handover.version} officially approved and published for incoming members. Notes: {approval_data.approval_notes or 'Approved by Project Lead'}"
    )

    return handover
