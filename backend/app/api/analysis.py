from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.config import settings
from app.models import Project, Document, DocumentPassage, ExtractedClaim, ClaimEvidence, User
from app.schemas import ClaimOut, ClaimEvidenceOut, ClaimResolve
from app.api.deps import require_project_lead, get_current_user, record_audit
from app.services.ai_engine import run_deterministic_extraction, detect_conflicts

router = APIRouter(prefix="", tags=["AI Analysis & Evidence"])

@router.post("/projects/{id}/analyze")
def trigger_analysis(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    docs = db.query(Document).filter(Document.project_id == project.id).all()
    if not docs:
        raise HTTPException(status_code=400, detail="Cannot analyze project with no uploaded documents. Please upload documents first.")

    # Gather all passages
    raw_passages = []
    for d in docs:
        passages = db.query(DocumentPassage).filter(DocumentPassage.document_id == d.id).all()
        for p in passages:
            raw_passages.append({
                "id": p.id,
                "document_id": d.id,
                "filename": d.filename,
                "page_number": p.page_number,
                "content": p.content
            })

    if not raw_passages:
        raise HTTPException(status_code=400, detail="No extractable text found in project documents.")

    # Run AI Extraction Pipeline
    extraction_output = run_deterministic_extraction(raw_passages)
    claims_list = extraction_output["claims"]

    # Run Cross-Document Conflict Detection
    claims_list = detect_conflicts(claims_list)

    # Clear previous claims to allow fresh re-analysis
    db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project.id).delete()
    db.commit()

    created_claims = []
    for c in claims_list:
        claim_rec = ExtractedClaim(
            project_id=project.id,
            category=c["category"],
            title=c["title"],
            description=c["description"],
            owner=c.get("owner"),
            date_reference=c.get("date_reference"),
            confidence=c.get("confidence", 0.9),
            verification_status=c.get("verification_status", "VERIFIED"),
            conflict_details=c.get("conflict_details")
        )
        db.add(claim_rec)
        db.commit()
        db.refresh(claim_rec)

        if c.get("passage_id"):
            ev = ClaimEvidence(
                claim_id=claim_rec.id,
                passage_id=c["passage_id"],
                excerpt=c.get("excerpt", c["description"])
            )
            db.add(ev)
            db.commit()
        created_claims.append(claim_rec)

    conflict_count = len([c for c in created_claims if c.verification_status == "CONFLICT"])
    record_audit(
        db,
        "ANALYSIS_COMPLETED",
        project_id=project.id,
        user=current_user,
        details=f"Analyzed {len(docs)} documents: extracted {len(created_claims)} claims ({conflict_count} conflicts detected)."
    )

    return {
        "status": "success",
        "engine": extraction_output.get("engine", "KnowBridge Analysis Engine"),
        "total_claims": len(created_claims),
        "conflicts_detected": conflict_count,
        "message": f"Successfully extracted {len(created_claims)} claims with evidence references."
    }

@router.get("/projects/{id}/claims", response_model=List[ClaimOut])
def get_project_claims(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    claims = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == id).all()
    results = []
    for c in claims:
        ev_list = []
        for ev in c.evidences:
            ev_list.append(ClaimEvidenceOut(
                id=ev.id,
                passage_id=ev.passage_id,
                excerpt=ev.excerpt,
                page_number=ev.passage.page_number if ev.passage else 1,
                filename=ev.passage.document.filename if ev.passage and ev.passage.document else "Unknown",
                relevance_note=ev.relevance_note
            ))

        results.append(ClaimOut(
            id=c.id,
            project_id=c.project_id,
            category=c.category,
            title=c.title,
            description=c.description,
            owner=c.owner,
            date_reference=c.date_reference,
            confidence=c.confidence,
            verification_status=c.verification_status,
            conflict_details=c.conflict_details,
            is_resolved=c.is_resolved,
            resolution_notes=c.resolution_notes,
            created_at=c.created_at,
            evidences=ev_list
        ))
    return results

@router.put("/claims/{claim_id}/resolve", response_model=ClaimOut)
def resolve_claim_conflict(
    claim_id: int,
    resolve_data: ClaimResolve,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    claim = db.query(ExtractedClaim).filter(ExtractedClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.is_resolved = True
    claim.verification_status = "VERIFIED"
    claim.resolution_notes = resolve_data.resolution_notes
    if resolve_data.chosen_date:
        claim.date_reference = resolve_data.chosen_date
    if resolve_data.chosen_owner:
        claim.owner = resolve_data.chosen_owner

    db.commit()
    db.refresh(claim)

    record_audit(
        db,
        "CONFLICT_RESOLVED",
        project_id=claim.project_id,
        user=current_user,
        details=f"Resolved claim '{claim.title}': {resolve_data.resolution_notes}"
    )

    ev_list = []
    for ev in claim.evidences:
        ev_list.append(ClaimEvidenceOut(
            id=ev.id,
            passage_id=ev.passage_id,
            excerpt=ev.excerpt,
            page_number=ev.passage.page_number if ev.passage else 1,
            filename=ev.passage.document.filename if ev.passage and ev.passage.document else "Unknown",
            relevance_note=ev.relevance_note
        ))

    return ClaimOut(
        id=claim.id,
        project_id=claim.project_id,
        category=claim.category,
        title=claim.title,
        description=claim.description,
        owner=claim.owner,
        date_reference=claim.date_reference,
        confidence=claim.confidence,
        verification_status=claim.verification_status,
        conflict_details=claim.conflict_details,
        is_resolved=claim.is_resolved,
        resolution_notes=claim.resolution_notes,
        created_at=claim.created_at,
        evidences=ev_list
    )
