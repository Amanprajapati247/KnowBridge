import os
import pymupdf
from docx import Document as DocxDocument
from sqlalchemy.orm import Session
from app.models import (
    User, Project, Document, DocumentPassage, ExtractedClaim, ClaimEvidence,
    AuditLog
)
from app.services.extractor import extract_document
from app.services.ai_engine import run_deterministic_extraction, detect_conflicts
from app.core.config import settings

STARTER_PROJECT_TITLE = "College Event Management System"
SAMPLE_DIR = os.path.join(settings.UPLOAD_DIR, "starter_files")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_sample_files():
    """Generates 5 realistic project files for the starter workspace."""
    files_created = {}

    # 1. Project Requirements.pdf
    pdf1_path = os.path.join(SAMPLE_DIR, "Project_Requirements.pdf")
    doc1 = pymupdf.open()
    page1 = doc1.new_page()
    req_text = """COLLEGE EVENT MANAGEMENT SYSTEM - PRODUCT SPECIFICATION DOCUMENT
CONFIDENTIAL & PROPRIETARY · VERSION 1.2

1. Overview and Core Objectives
The College Event Management System (CEMS) automates student fest registrations, ticketing, and badge issuance.
Current project status is in Phase 2 Development.

2. Architecture Decisions
- Decided to use FastAPI for the backend API service to handle asynchronous ticket booking spikes.
- Decided to adopt PostgreSQL as the primary relational database for ACID transaction safety.
- Decided to adopt Tailwind CSS with a navy and teal theme for rapid dashboard consistency.

3. Project Milestones & Critical Deadlines
- Core Database Schema Delivery: Due date October 20, 2026. Handled by Lead Architect.
- Beta Launch Deadline: Target date November 15, 2026 for initial campus testing.
- Final Campus Fest Rollout: Due date December 05, 2026.

4. Known Dependencies
- QR Ticket Scanning Module depends on the student registration database being finalized.
- Payment gateway integration requires college treasury merchant credentials."""
    page1.insert_text(pymupdf.Point(40, 50), req_text, fontsize=10, fontname="helv")
    doc1.save(pdf1_path)
    doc1.close()
    files_created["Project_Requirements.pdf"] = pdf1_path

    # 2. Meeting Notes.docx (Contains the postponed Beta Launch date schedule adjustment)
    docx1_path = os.path.join(SAMPLE_DIR, "Meeting_Notes.docx")
    d1 = DocxDocument()
    d1.add_heading("Sprint Planning & Architecture Sync - Core Operations", level=1)
    d1.add_paragraph("Attendees: Alex Chen (Project Lead), Priya Sharma (Frontend Dev), Marcus Vance (Backend Dev), Sarah Jenkins (QA).")
    
    d1.add_heading("Schedule Adjustments & Milestone Updates", level=2)
    d1.add_paragraph("Due to student council mid-semester exam week, the team decided to postpone the deployment schedule.")
    d1.add_paragraph("Beta Launch Deadline: Target date November 25, 2026 agreed during sprint review to accommodate testing.")

    d1.add_heading("Task Assignments & Ownership", level=2)
    d1.add_paragraph("Assigned to: Priya Sharma to implement attendee registration form and validation by November 10, 2026.")
    d1.add_paragraph("Assigned to: Marcus Vance to build JWT authentication and RBAC endpoints by November 08, 2026.")
    d1.add_paragraph("Assigned to: Alex Chen to coordinate college server hosting and SSL certificate provisioning.")
    d1.save(docx1_path)
    files_created["Meeting_Notes.docx"] = docx1_path

    # 3. Development Tasks.txt
    txt_path = os.path.join(SAMPLE_DIR, "Development_Tasks.txt")
    txt_content = """# CEMS ENGINEERING SPRINT BACKLOG & TASK STATUS

Task: Database Schema & Migrations
Status: Completed
Owner: Marcus Vance
Description: Designed User, Event, Ticket, and AuditLog tables. PostgreSQL scripts verified.

Task: Attendee Registration UI
Status: In Progress
Owner: Priya Sharma
Target Date: November 10, 2026
Description: Building responsive form components in React and TypeScript.

Task: Automated Email Confirmation Dispatcher
Status: Pending
Owner: Not found in available sources
Description: Build worker service to send confirmation QR codes to registered participants. Target completion pending.

Task: Campus Payment Gateway Webhook
Status: Blocked
Owner: Marcus Vance
Description: Blocked waiting on college account office to issue staging API keys.
"""
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    files_created["Development_Tasks.txt"] = txt_path

    # 4. Project Decisions.pdf
    pdf2_path = os.path.join(SAMPLE_DIR, "Project_Decisions.pdf")
    doc2 = pymupdf.open()
    page2 = doc2.new_page()
    dec_text = """CEMS ARCHITECTURAL DECISION RECORDS (ADR)
SYSTEM DESIGN BOARD REVIEW

ADR-001: Offline-Capable QR Code Scanner
- Decision: Decided to generate cryptographically signed offline-verifiable QR tokens.
- Rationale: College auditorium has unreliable Wi-Fi cellular coverage during large fests.
- Owner: Marcus Vance

ADR-002: Cloud Storage Provider
- Decision: Decided to store attendee photo ID proofs in secure S3-compatible bucket with 30-day retention policy.
- Rationale: Compliance with campus data protection rules.
- Owner: Alex Chen
"""
    page2.insert_text(pymupdf.Point(40, 50), dec_text, fontsize=10, fontname="helv")
    doc2.save(pdf2_path)
    doc2.close()
    files_created["Project_Decisions.pdf"] = pdf2_path

    # 5. Risk Register.docx
    docx2_path = os.path.join(SAMPLE_DIR, "Risk_Register.docx")
    d2 = DocxDocument()
    d2.add_heading("Risk Register, Security Considerations & Open Technical Inquiries", level=1)
    
    d2.add_heading("Active Operational & Technical Risks", level=2)
    d2.add_paragraph("Risk: High concurrent traffic spike during morning ticket drop may exhaust connection pool.")
    d2.add_paragraph("Risk: Delay in merchant account verification by bank could postpone payment checkout testing.")
    
    d2.add_heading("Unresolved Questions & Missing Information", level=2)
    d2.add_paragraph("Open question: Will student council cover the SMS OTP gateway transaction costs or should we switch to email magic links?")
    d2.add_paragraph("Open question: Who will be the primary on-call contact person for physical auditorium gate troubleshooting during the fest?")
    d2.save(docx2_path)
    files_created["Risk_Register.docx"] = docx2_path

    return files_created

def seed_demo_project(db: Session, lead_user: User) -> Project:
    """
    Initializes a full reference project with standard documentation,
    reconstructed knowledge state, and cross-document discrepancy detection.
    """
    existing_project = db.query(Project).filter(
        Project.lead_id == lead_user.id,
        Project.title == STARTER_PROJECT_TITLE
    ).first()

    if existing_project:
        db.delete(existing_project)
        db.commit()

    # 1. Create Reference Project
    demo_project = Project(
        title=STARTER_PROJECT_TITLE,
        description="Event management and digital ticketing platform automating student festival registrations, ticketing, and badge issuance. Demonstrates multi-document knowledge reconstruction, contradiction detection, and handover sign-off.",
        status="ACTIVE",
        lead_id=lead_user.id
    )
    db.add(demo_project)
    db.commit()
    db.refresh(demo_project)

    # 2. Ingest and attach project files
    file_paths = generate_sample_files()
    raw_passages = []

    for filename, filepath in file_paths.items():
        filesize = os.path.getsize(filepath)
        ext = os.path.splitext(filename)[1].lstrip(".").lower()
        
        doc_record = Document(
            project_id=demo_project.id,
            filename=filename,
            file_type=ext,
            file_size=filesize,
            file_path=filepath,
            uploader_id=lead_user.id,
            is_processed=True
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # Extract passages
        extracted = extract_document(filepath, filename)
        for p in extracted:
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
            db.commit()
            db.refresh(passage_rec)

            raw_passages.append({
                "id": passage_rec.id,
                "document_id": doc_record.id,
                "filename": filename,
                "page_number": passage_rec.page_number,
                "content": passage_rec.content
            })

    # 3. Run AI Knowledge Extraction
    extraction_result = run_deterministic_extraction(raw_passages)
    claims_data = extraction_result["claims"]

    # 4. Detect cross-document contradictions (e.g. Beta Launch schedule adjustments)
    claims_data = detect_conflicts(claims_data)

    # 5. Persist Claims & Evidence in Database
    for c in claims_data:
        claim_rec = ExtractedClaim(
            project_id=demo_project.id,
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

    # Log in audit trail
    log = AuditLog(
        project_id=demo_project.id,
        user_id=lead_user.id,
        user_name=lead_user.full_name,
        action="STARTER_PROJECT_INITIALIZED",
        details="Reference project 'College Event Management System' initialized with standard engineering documentation."
    )
    db.add(log)
    db.commit()

    return demo_project
