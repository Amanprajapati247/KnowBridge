import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.models import Project, Document, DocumentPassage, User
from app.schemas import DocumentOut, PassageOut
from app.api.deps import require_project_lead, record_audit
from app.services.extractor import extract_document, DocumentExtractionError

router = APIRouter(prefix="", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB limit

@router.post("/projects/{id}/documents", response_model=List[DocumentOut], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    uploaded_records = []
    proj_upload_dir = os.path.join(settings.UPLOAD_DIR, f"project_{project.id}")
    os.makedirs(proj_upload_dir, exist_ok=True)

    for file in files:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{ext}' for file '{filename}'. Only PDF, DOCX, and TXT are permitted."
            )

        saved_path = os.path.join(proj_upload_dir, filename)
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise HTTPException(status_code=400, detail=f"File '{filename}' is empty")
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File '{filename}' exceeds maximum size of 25MB")

        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # Create Document record
        doc_record = Document(
            project_id=project.id,
            filename=filename,
            file_type=ext.lstrip("."),
            file_size=file_size,
            file_path=saved_path,
            uploader_id=current_user.id,
            is_processed=False
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # Extract passages
        try:
            passages = extract_document(saved_path, filename)
            for p in passages:
                passage_rec = DocumentPassage(
                    document_id=doc_record.id,
                    passage_number=p["passage_number"],
                    page_number=p.get("page_number", 1),
                    section_title=p.get("section_title"),
                    content=p["content"],
                    char_start=p["char_start"],
                    char_end=p["char_end"]
                )
                db.add(passage_rec)

            doc_record.is_processed = True
            db.commit()
            record_audit(db, "DOCUMENT_UPLOADED", project_id=project.id, user=current_user, details=f"Uploaded '{filename}' ({len(passages)} passages extracted)")
        except DocumentExtractionError as e:
            db.delete(doc_record)
            db.commit()
            if os.path.exists(saved_path):
                os.remove(saved_path)
            raise HTTPException(status_code=400, detail=f"Error extracting content from '{filename}': {str(e)}")

        passage_count = db.query(DocumentPassage).filter(DocumentPassage.document_id == doc_record.id).count()
        uploaded_records.append(DocumentOut(
            id=doc_record.id,
            project_id=doc_record.project_id,
            filename=doc_record.filename,
            file_type=doc_record.file_type,
            file_size=doc_record.file_size,
            uploaded_at=doc_record.uploaded_at,
            is_processed=doc_record.is_processed,
            passage_count=passage_count
        ))

    return uploaded_records

@router.get("/projects/{id}/documents", response_model=List[DocumentOut])
def list_documents(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    docs = db.query(Document).filter(Document.project_id == id).all()
    results = []
    for d in docs:
        p_count = db.query(DocumentPassage).filter(DocumentPassage.document_id == d.id).count()
        results.append(DocumentOut(
            id=d.id,
            project_id=d.project_id,
            filename=d.filename,
            file_type=d.file_type,
            file_size=d.file_size,
            uploaded_at=d.uploaded_at,
            is_processed=d.is_processed,
            passage_count=p_count
        ))
    return results

@router.get("/documents/{id}/passages", response_model=List[PassageOut])
def get_passages(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    passages = db.query(DocumentPassage).filter(DocumentPassage.document_id == id).order_by(DocumentPassage.passage_number).all()
    return passages

@router.get("/documents/{id}/download")
def download_document(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    project = db.query(Project).filter(Project.id == doc.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized to access this document")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File content not found on server")

    return FileResponse(doc.file_path, filename=doc.filename)

@router.delete("/documents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    project = db.query(Project).filter(Project.id == doc.project_id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this document")

    record_audit(db, "DOCUMENT_DELETED", project_id=project.id, user=current_user, details=f"Deleted document '{doc.filename}'")
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    db.delete(doc)
    db.commit()
    return None
