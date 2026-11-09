from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.models import Project, Document, ExtractedClaim, Handover, User
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut, MainDashboardStats
from app.api.deps import get_current_user, require_project_lead, record_audit
from app.services.demo_seeder import seed_demo_project

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/stats/dashboard", response_model=MainDashboardStats)
def get_main_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "PROJECT_LEAD":
        projects = db.query(Project).filter(Project.lead_id == current_user.id).all()
        proj_ids = [p.id for p in projects]
        total_docs = db.query(Document).filter(Document.project_id.in_(proj_ids)).count() if proj_ids else 0
        total_handovers = db.query(Handover).filter(Handover.project_id.in_(proj_ids)).count() if proj_ids else 0
        pending_reviews = db.query(Handover).filter(Handover.project_id.in_(proj_ids), Handover.status == "DRAFT").count() if proj_ids else 0
        open_tasks = db.query(ExtractedClaim).filter(ExtractedClaim.project_id.in_(proj_ids), ExtractedClaim.category == "TASK").count() if proj_ids else 0
        risks = db.query(ExtractedClaim).filter(ExtractedClaim.project_id.in_(proj_ids), ExtractedClaim.category.in_(["RISK", "BLOCKER"])).count() if proj_ids else 0
        conflicts = db.query(ExtractedClaim).filter(ExtractedClaim.project_id.in_(proj_ids), ExtractedClaim.verification_status == "CONFLICT").count() if proj_ids else 0
    else:
        # Incoming member view stats: approved handovers only
        approved_handovers = db.query(Handover).filter(Handover.status == "APPROVED").all()
        proj_ids = list(set([h.project_id for h in approved_handovers]))
        projects = db.query(Project).filter(Project.id.in_(proj_ids)).all() if proj_ids else []
        total_docs = 0  # Incoming members do not see unvetted raw documents
        total_handovers = len(approved_handovers)
        pending_reviews = 0
        open_tasks = db.query(ExtractedClaim).filter(ExtractedClaim.project_id.in_(proj_ids), ExtractedClaim.category == "TASK").count() if proj_ids else 0
        risks = db.query(ExtractedClaim).filter(ExtractedClaim.project_id.in_(proj_ids), ExtractedClaim.category.in_(["RISK", "BLOCKER"])).count() if proj_ids else 0
        conflicts = 0

    return MainDashboardStats(
        total_projects=len(projects),
        total_documents=total_docs,
        generated_handovers=total_handovers,
        pending_reviews=pending_reviews,
        open_tasks=open_tasks,
        identified_risks=risks,
        conflicts_count=conflicts
    )

@router.get("", response_model=List[ProjectOut])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "PROJECT_LEAD":
        projects = db.query(Project).filter(Project.lead_id == current_user.id).all()
    else:
        # Incoming members see projects with approved handovers
        approved_proj_ids = [h.project_id for h in db.query(Handover).filter(Handover.status == "APPROVED").all()]
        projects = db.query(Project).filter(Project.id.in_(approved_proj_ids)).all()

    result = []
    for p in projects:
        doc_count = db.query(Document).filter(Document.project_id == p.id).count()
        claim_count = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == p.id).count()
        latest_handover = db.query(Handover).filter(Handover.project_id == p.id).order_by(Handover.id.desc()).first()
        handover_status = latest_handover.status if latest_handover else "NOT_STARTED"

        p_out = ProjectOut(
            id=p.id,
            title=p.title,
            description=p.description,
            status=p.status,
            lead_id=p.lead_id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            document_count=doc_count,
            claim_count=claim_count,
            handover_status=handover_status
        )
        result.append(p_out)
    return result

@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = Project(
        title=project_in.title,
        description=project_in.description,
        status="ACTIVE",
        lead_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    record_audit(db, "PROJECT_CREATED", project_id=project.id, user=current_user, details=f"Project '{project.title}' created")
    return ProjectOut(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        lead_id=project.lead_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        document_count=0,
        claim_count=0,
        handover_status="NOT_STARTED"
    )

@router.get("/{id}", response_model=ProjectOut)
def get_project(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # If incoming member, verify there is an approved handover
    if current_user.role == "INCOMING_MEMBER":
        has_approved = db.query(Handover).filter(Handover.project_id == id, Handover.status == "APPROVED").first()
        if not has_approved:
            raise HTTPException(status_code=403, detail="Access denied: Handover has not been approved for incoming member viewing")

    doc_count = db.query(Document).filter(Document.project_id == project.id).count()
    claim_count = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project.id).count()
    latest_handover = db.query(Handover).filter(Handover.project_id == project.id).order_by(Handover.id.desc()).first()

    return ProjectOut(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        lead_id=project.lead_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        document_count=doc_count,
        claim_count=claim_count,
        handover_status=latest_handover.status if latest_handover else "NOT_STARTED"
    )

@router.put("/{id}", response_model=ProjectOut)
def update_project(
    id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    if project_update.title is not None:
        project.title = project_update.title
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.status is not None:
        project.status = project_update.status
    project.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)
    record_audit(db, "PROJECT_UPDATED", project_id=project.id, user=current_user, details=f"Project '{project.title}' updated")

    doc_count = db.query(Document).filter(Document.project_id == project.id).count()
    claim_count = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == project.id).count()
    latest_handover = db.query(Handover).filter(Handover.project_id == project.id).order_by(Handover.id.desc()).first()

    return ProjectOut(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        lead_id=project.lead_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        document_count=doc_count,
        claim_count=claim_count,
        handover_status=latest_handover.status if latest_handover else "NOT_STARTED"
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    record_audit(db, "PROJECT_DELETED", project_id=project.id, user=current_user, details=f"Project '{project.title}' deleted")
    db.delete(project)
    db.commit()
    return None

@router.post("/seed-demo", response_model=ProjectOut)
def seed_demo(
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    """
    Initializes the standard reference project 'College Event Management System'
    with 5 comprehensive documents, extracts knowledge, detects conflicts, and readies the workspace.
    """
    demo_proj = seed_demo_project(db, current_user)
    doc_count = db.query(Document).filter(Document.project_id == demo_proj.id).count()
    claim_count = db.query(ExtractedClaim).filter(ExtractedClaim.project_id == demo_proj.id).count()

    return ProjectOut(
        id=demo_proj.id,
        title=demo_proj.title,
        description=demo_proj.description,
        status=demo_proj.status,
        lead_id=demo_proj.lead_id,
        created_at=demo_proj.created_at,
        updated_at=demo_proj.updated_at,
        document_count=doc_count,
        claim_count=claim_count,
        handover_status="NOT_STARTED"
    )
