from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.models import (
    Project, Handover, HandoverItem, HandoverSnapshot, HandoverAcknowledgment,
    Document, User
)
from app.schemas import (
    HandoverSnapshotOut, HandoverVersionCompareOut, AcknowledgmentCreate,
    HandoverAcknowledgmentOut, AcknowledgmentReceiptOut
)
from app.api.deps import get_current_user, require_project_lead, record_audit
from app.services.crypto_audit import CryptoAuditService

router = APIRouter(prefix="", tags=["Cryptographic Audit & Versioning"])

@router.get("/handovers/{id}/snapshots", response_model=List[HandoverSnapshotOut])
def list_handover_snapshots(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    # Access check: Lead of project or Incoming member viewing approved handover
    if current_user.role == "PROJECT_LEAD":
        project = db.query(Project).filter(Project.id == handover.project_id, Project.lead_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=403, detail="Unauthorized")
    else:
        if handover.status != "APPROVED":
            raise HTTPException(status_code=403, detail="Incoming members can only access approved handover snapshots")

    snapshots = db.query(HandoverSnapshot).filter(HandoverSnapshot.handover_id == id).order_by(HandoverSnapshot.id.desc()).all()
    return snapshots

@router.get("/handovers/{id}/verify-hash")
def verify_handover_hash(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    result = CryptoAuditService.verify_handover_integrity(handover)
    return result

@router.get("/documents/{id}/verify-hash")
def verify_document_hash(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    project = db.query(Project).filter(Project.id == doc.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized")

    import os
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Physical file missing on server")

    current_hash = CryptoAuditService.calculate_file_sha256(doc.file_path)
    recorded_hash = doc.sha256_hash or current_hash

    # If document had no hash recorded previously, backfill it
    if not doc.sha256_hash:
        doc.sha256_hash = current_hash
        db.commit()

    is_valid = (current_hash == recorded_hash)
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "recorded_hash": recorded_hash,
        "current_hash": current_hash,
        "is_valid": is_valid,
        "algorithm": "SHA-256",
        "message": "File integrity verified. Content matches cryptographic hash." if is_valid else "Warning: File on disk has been altered since ingestion!"
    }

@router.get("/handovers/{id}/compare", response_model=HandoverVersionCompareOut)
def compare_handover_versions(
    id: int,
    v1: str,
    v2: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compares two approved snapshots (e.g. v1.0 vs v2.0) and generates a semantic diff.
    """
    snap1 = db.query(HandoverSnapshot).filter(
        HandoverSnapshot.handover_id == id,
        HandoverSnapshot.version == v1
    ).first()

    snap2 = db.query(HandoverSnapshot).filter(
        HandoverSnapshot.handover_id == id,
        HandoverSnapshot.version == v2
    ).first()

    if not snap1 or not snap2:
        raise HTTPException(
            status_code=404,
            detail=f"One or both snapshots (v{v1}, v{v2}) not found for this handover."
        )

    # Access check
    if current_user.role == "PROJECT_LEAD":
        project = db.query(Project).filter(Project.id == snap1.project_id, Project.lead_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=403, detail="Unauthorized")

    diff = CryptoAuditService.compare_snapshots(snap1, snap2)
    return HandoverVersionCompareOut(**diff)

@router.post("/handovers/{id}/acknowledge", response_model=HandoverAcknowledgmentOut)
def acknowledge_handover(
    id: int,
    payload: AcknowledgmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows incoming team members to formally acknowledge receipt of an approved handover.
    Generates a cryptographic SHA-256 receipt token.
    """
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    if handover.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Only officially APPROVED handovers can be acknowledged."
        )

    # Check if already acknowledged by this user
    existing = db.query(HandoverAcknowledgment).filter(
        HandoverAcknowledgment.handover_id == id,
        HandoverAcknowledgment.user_id == current_user.id,
        HandoverAcknowledgment.version == handover.version
    ).first()
    if existing:
        return HandoverAcknowledgmentOut(
            id=existing.id,
            handover_id=existing.handover_id,
            snapshot_id=existing.snapshot_id,
            project_id=existing.project_id,
            user_id=existing.user_id,
            version=existing.version,
            snapshot_hash=existing.snapshot_hash,
            receipt_token=existing.receipt_token,
            signature_notes=existing.signature_notes,
            acknowledged_at=existing.acknowledged_at,
            user_name=current_user.full_name
        )

    try:
        ack = CryptoAuditService.record_acknowledgment(
            db=db,
            handover=handover,
            user=current_user,
            signature_notes=payload.signature_notes
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return HandoverAcknowledgmentOut(
        id=ack.id,
        handover_id=ack.handover_id,
        snapshot_id=ack.snapshot_id,
        project_id=ack.project_id,
        user_id=ack.user_id,
        version=ack.version,
        snapshot_hash=ack.snapshot_hash,
        receipt_token=ack.receipt_token,
        signature_notes=ack.signature_notes,
        acknowledged_at=ack.acknowledged_at,
        user_name=current_user.full_name
    )

@router.get("/handovers/{id}/acknowledgments", response_model=List[HandoverAcknowledgmentOut])
def list_acknowledgments(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    acks = db.query(HandoverAcknowledgment).filter(
        HandoverAcknowledgment.handover_id == id
    ).order_by(HandoverAcknowledgment.id.desc()).all()

    out = []
    for a in acks:
        u = db.query(User).filter(User.id == a.user_id).first()
        out.append(HandoverAcknowledgmentOut(
            id=a.id,
            handover_id=a.handover_id,
            snapshot_id=a.snapshot_id,
            project_id=a.project_id,
            user_id=a.user_id,
            version=a.version,
            snapshot_hash=a.snapshot_hash,
            receipt_token=a.receipt_token,
            signature_notes=a.signature_notes,
            acknowledged_at=a.acknowledged_at,
            user_name=u.full_name if u else "Unknown User"
        ))
    return out

@router.get("/handovers/{id}/receipt", response_model=AcknowledgmentReceiptOut)
def get_acknowledgment_receipt(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a verifiable acknowledgment receipt linking the incoming user,
    handover version, snapshot hash, and timestamp.
    """
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")

    project = db.query(Project).filter(Project.id == handover.project_id).first()

    # Find acknowledgment for this user, or latest if not yet acknowledged by current user
    ack = db.query(HandoverAcknowledgment).filter(
        HandoverAcknowledgment.handover_id == id,
        HandoverAcknowledgment.user_id == current_user.id
    ).order_by(HandoverAcknowledgment.id.desc()).first()

    if not ack:
        ack = db.query(HandoverAcknowledgment).filter(
            HandoverAcknowledgment.handover_id == id
        ).order_by(HandoverAcknowledgment.id.desc()).first()

    if not ack:
        raise HTTPException(status_code=404, detail="No acknowledgment receipt recorded for this handover yet.")

    ack_user = db.query(User).filter(User.id == ack.user_id).first()

    verification_statement = (
        f"This cryptographic receipt confirms that {ack_user.full_name if ack_user else 'Incoming Member'} "
        f"formally acknowledged and accepted project responsibilities for '{project.title if project else 'Project'}' "
        f"(Handover v{ack.version}) on {ack.acknowledged_at.strftime('%Y-%m-%d %H:%M:%S UTC')}. "
        f"Snapshot Content Hash: {ack.snapshot_hash}."
    )

    return AcknowledgmentReceiptOut(
        receipt_token=ack.receipt_token,
        handover_id=handover.id,
        handover_title=handover.title,
        version=ack.version,
        snapshot_hash=ack.snapshot_hash,
        project_id=project.id if project else 0,
        project_title=project.title if project else "Project",
        user_id=ack.user_id,
        user_name=ack_user.full_name if ack_user else "Incoming Member",
        user_email=ack_user.email if ack_user else "unknown@knowbridge.io",
        acknowledged_at=ack.acknowledged_at,
        signature_notes=ack.signature_notes,
        cryptographic_algorithm="SHA-256",
        verification_statement=verification_statement,
        is_valid=True
    )
