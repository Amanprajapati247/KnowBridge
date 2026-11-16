import os
import json
import hashlib
from datetime import datetime, timezone
import pymupdf
from docx import Document as DocxDocument
from sqlalchemy.orm import Session
from app.models import (
    User, Project, Document, DocumentPassage, ExtractedClaim, ClaimEvidence,
    Handover, HandoverItem, HandoverSnapshot, HandoverAcknowledgment,
    ExternalConnector, ExternalRecord, AuditLog
)
from app.services.extractor import extract_document
from app.services.ai_engine import run_deterministic_extraction, detect_conflicts
from app.services.handover_generator import generate_handover_report
from app.services.crypto_audit import CryptoAuditService
from app.core.config import settings

FEED_DIR = os.path.join(settings.UPLOAD_DIR, "production_data")
os.makedirs(FEED_DIR, exist_ok=True)

def utc_now():
    return datetime.now(timezone.utc)

def feed_application_data(db: Session, lead_user: User):
    """
    Feeds complete, realistic multi-project data into KnowBridge,
    including documents, passages, extracted claims, resolved conflicts,
    and approved handovers.
    """
    # -------------------------------------------------------------
    # PROJECT 1: College Event Management System (CEMS)
    # -------------------------------------------------------------
    p1 = db.query(Project).filter(Project.title == "College Event Management System", Project.lead_id == lead_user.id).first()
    if not p1:
        p1 = Project(
            title="College Event Management System",
            description="Event management and digital ticketing platform automating student festival registrations, ticketing, and badge issuance. Demonstrates multi-document knowledge reconstruction, contradiction detection, and handover sign-off.",
            status="IN_REVIEW",
            lead_id=lead_user.id
        )
        db.add(p1)
        db.commit()
        db.refresh(p1)

        # Generate files for P1
        p1_files = {}

        # 1. Project Requirements.pdf
        pdf1_path = os.path.join(FEED_DIR, "Project_Requirements.pdf")
        doc1 = pymupdf.open()
        page1 = doc1.new_page()
        page1.insert_text(pymupdf.Point(40, 50), """COLLEGE EVENT MANAGEMENT SYSTEM - PRODUCT SPECIFICATION
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
- Payment gateway integration requires college treasury merchant credentials.""", fontsize=10, fontname="helv")
        doc1.save(pdf1_path)
        doc1.close()
        p1_files["Project_Requirements.pdf"] = pdf1_path

        # 2. Meeting Notes.docx
        docx1_path = os.path.join(FEED_DIR, "Meeting_Notes.docx")
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
        p1_files["Meeting_Notes.docx"] = docx1_path

        # 3. Development Tasks.txt
        txt1_path = os.path.join(FEED_DIR, "Development_Tasks.txt")
        with open(txt1_path, "w", encoding="utf-8") as f:
            f.write("""# CEMS ENGINEERING SPRINT BACKLOG & TASK STATUS

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
""")
        p1_files["Development_Tasks.txt"] = txt1_path

        # 4. Project Decisions.pdf
        pdf2_path = os.path.join(FEED_DIR, "Project_Decisions.pdf")
        doc2 = pymupdf.open()
        page2 = doc2.new_page()
        page2.insert_text(pymupdf.Point(40, 50), """CEMS ARCHITECTURAL DECISION RECORDS (ADR)
SYSTEM DESIGN BOARD REVIEW

ADR-001: Offline-Capable QR Code Scanner
- Decision: Decided to generate cryptographically signed offline-verifiable QR tokens.
- Rationale: College auditorium has unreliable Wi-Fi cellular coverage during large fests.
- Owner: Marcus Vance

ADR-002: Cloud Storage Provider
- Decision: Decided to store attendee photo ID proofs in secure S3-compatible bucket with 30-day retention policy.
- Rationale: Compliance with campus data protection rules.
- Owner: Alex Chen
""", fontsize=10, fontname="helv")
        doc2.save(pdf2_path)
        doc2.close()
        p1_files["Project_Decisions.pdf"] = pdf2_path

        # 5. Risk Register.docx
        docx2_path = os.path.join(FEED_DIR, "Risk_Register.docx")
        d2 = DocxDocument()
        d2.add_heading("Risk Register, Security Considerations & Open Technical Inquiries", level=1)
        d2.add_heading("Active Operational & Technical Risks", level=2)
        d2.add_paragraph("Risk: High concurrent traffic spike during morning ticket drop may exhaust connection pool.")
        d2.add_paragraph("Risk: Delay in merchant account verification by bank could postpone payment checkout testing.")
        d2.add_heading("Unresolved Questions & Missing Information", level=2)
        d2.add_paragraph("Open question: Will student council cover the SMS OTP gateway transaction costs or should we switch to email magic links?")
        d2.add_paragraph("Open question: Who will be the primary on-call contact person for physical auditorium gate troubleshooting during the fest?")
        d2.save(docx2_path)
        p1_files["Risk_Register.docx"] = docx2_path

        # Ingest documents into DB
        p1_passages = []
        p1_doc_records = []
        for filename, filepath in p1_files.items():
            doc_rec = Document(
                project_id=p1.id,
                filename=filename,
                file_type=os.path.splitext(filename)[1].lstrip("."),
                file_size=os.path.getsize(filepath),
                file_path=filepath,
                uploader_id=lead_user.id,
                is_processed=True
            )
            db.add(doc_rec)
            db.commit()
            db.refresh(doc_rec)
            p1_doc_records.append(doc_rec)

            extracted = extract_document(filepath, filename)
            for p in extracted:
                pass_rec = DocumentPassage(
                    document_id=doc_rec.id,
                    passage_number=p["passage_number"],
                    page_number=p.get("page_number", 1),
                    section_title=p.get("section_title"),
                    content=p["content"],
                    char_start=p["char_start"],
                    char_end=p["char_end"]
                )
                db.add(pass_rec)
                db.commit()
                db.refresh(pass_rec)

                p1_passages.append({
                    "id": pass_rec.id,
                    "document_id": doc_rec.id,
                    "filename": filename,
                    "page_number": pass_rec.page_number,
                    "content": pass_rec.content
                })

        # Extraction & Conflict resolution for P1
        extracted_data = run_deterministic_extraction(p1_passages)
        claims_list = detect_conflicts(extracted_data["claims"])

        p1_claim_records = []
        for c in claims_list:
            # Pre-resolve the Beta Launch conflict
            is_beta_launch = "beta launch" in c["title"].lower() or "beta launch" in c["description"].lower()
            status = "VERIFIED" if is_beta_launch else c.get("verification_status", "VERIFIED")
            date_ref = "November 25, 2026" if is_beta_launch else c.get("date_reference")
            res_notes = "Authoritatively resolved: Team confirmed in sprint review that Beta Launch is moved to Nov 25 to accommodate exam week." if is_beta_launch else None

            claim_rec = ExtractedClaim(
                project_id=p1.id,
                category=c["category"],
                title=c["title"],
                description=c["description"],
                owner=c.get("owner"),
                date_reference=date_ref,
                confidence=c.get("confidence", 0.9),
                verification_status=status,
                conflict_details=c.get("conflict_details"),
                is_resolved=is_beta_launch,
                resolution_notes=res_notes
            )
            db.add(claim_rec)
            db.commit()
            db.refresh(claim_rec)
            p1_claim_records.append(claim_rec)

            if c.get("passage_id"):
                ev = ClaimEvidence(
                    claim_id=claim_rec.id,
                    passage_id=c["passage_id"],
                    excerpt=c.get("excerpt", c["description"])
                )
                db.add(ev)
                db.commit()

        # Generate APPROVED Handover for P1
        h1_data = generate_handover_report(p1, p1_claim_records, p1_doc_records)
        h1 = Handover(
            project_id=p1.id,
            version="1.0",
            status="APPROVED",
            title=h1_data["title"],
            executive_summary=h1_data["executive_summary"],
            current_status=h1_data["current_status"],
            recommended_actions=h1_data["recommended_actions"],
            missing_information=h1_data["missing_information"],
            conflicting_information="All cross-document milestone schedule discrepancies authoritatively reconciled by Project Lead.",
            created_by_id=lead_user.id,
            approved_by_id=lead_user.id,
            approved_at=utc_now(),
            approval_notes="Handover report verified and officially approved. All architectural decisions, task assignments, and schedule adjustments reconciled for onboarding team members."
        )
        db.add(h1)
        db.commit()
        db.refresh(h1)

        for item in h1_data["items"]:
            item_rec = HandoverItem(
                handover_id=h1.id,
                claim_id=item["claim_id"],
                section=item["section"],
                title=item["title"],
                content=item["content"],
                source_filename=item["source_filename"],
                source_page=item["source_page"],
                evidence_excerpt=item["evidence_excerpt"],
                verification_status="VERIFIED",
                is_accepted=True,
                is_rejected=False,
                is_redacted=False,
                display_order=item["display_order"]
            )
            db.add(item_rec)
        db.commit()

        # Audit logs for P1
        db.add(AuditLog(project_id=p1.id, user_id=lead_user.id, user_name=lead_user.full_name, action="PROJECT_CREATED", details="Workspace initialized."))
        db.add(AuditLog(project_id=p1.id, user_id=lead_user.id, user_name=lead_user.full_name, action="DOCUMENTS_INGESTED", details="5 project documents ingested and passages segmented."))
        db.add(AuditLog(project_id=p1.id, user_id=lead_user.id, user_name=lead_user.full_name, action="AI_EXTRACTION_COMPLETED", details=f"Extracted {len(p1_claim_records)} claims with passage evidence."))
        db.add(AuditLog(project_id=p1.id, user_id=lead_user.id, user_name=lead_user.full_name, action="CONFLICT_RESOLVED", details="Beta Launch deadline reconciled to November 25, 2026."))
        db.add(AuditLog(project_id=p1.id, user_id=lead_user.id, user_name=lead_user.full_name, action="HANDOVER_APPROVED", details="Official Handover Report v1.0 approved and published."))
        db.commit()

    # -------------------------------------------------------------
    # PROJECT 2: Campus Autonomous Shuttle Service (CASS)
    # -------------------------------------------------------------
    p2 = db.query(Project).filter(Project.title == "Campus Autonomous Shuttle Service", Project.lead_id == lead_user.id).first()
    if not p2:
        p2 = Project(
            title="Campus Autonomous Shuttle Service",
            description="Safety-critical self-driving campus shuttle navigating university pedestrian corridors using LiDAR-based SLAM, ROS2 nodes, and remote teleoperation safety interlocks.",
            status="ACTIVE",
            lead_id=lead_user.id
        )
        db.add(p2)
        db.commit()
        db.refresh(p2)

        p2_files = {}

        # Architecture PDF
        cass_pdf = os.path.join(FEED_DIR, "CASS_System_Architecture.pdf")
        doc_cass = pymupdf.open()
        page_cass = doc_cass.new_page()
        page_cass.insert_text(pymupdf.Point(40, 50), """CAMPUS AUTONOMOUS SHUTTLE (CASS) - ARCHITECTURAL BLUEPRINT
DEPARTMENT OF ROBOTICS & AUTONOMOUS SYSTEMS

1. System Overview
The Campus Autonomous Shuttle operates at 15 km/h along pedestrian walkways connecting North Dormitories to the Student Union.
Status: In Active Testing.

2. Architecture Decisions
- Decided to adopt ROS2 Humble over ROS1 to guarantee deterministic real-time DDS communication.
- Decided to integrate dual Velodyne VLP-16 LiDAR sensors for 360-degree obstacle perception redundancy.
- Decided to implement hardware emergency brake watchdog over CAN bus with 50ms heartbeat check.

3. Key Milestones & Dependencies
- Core SLAM Navigation Calibration: Due date November 18, 2026. Handled by Marcus Vance.
- Route Safety Sign-Off with Campus Police: Target date December 01, 2026.
- Route testing depends on RTK GPS base station installation on Library rooftop.""", fontsize=10, fontname="helv")
        doc_cass.save(cass_pdf)
        doc_cass.close()
        p2_files["CASS_System_Architecture.pdf"] = cass_pdf

        # Hardware Spec DOCX
        cass_docx = os.path.join(FEED_DIR, "Sensor_Rig_Specifications.docx")
        d_cass = DocxDocument()
        d_cass.add_heading("CASS Sensor Rig & Telemetry Specifications", level=1)
        d_cass.add_paragraph("Lead Engineer: Marcus Vance | QA Reviewer: Sarah Jenkins")
        d_cass.add_heading("Hardware Decisions & Power Budget", level=2)
        d_cass.add_paragraph("Decided to power sensor suite through isolated 24V DC-DC converter to protect computing payload from motor voltage spikes.")
        d_cass.add_paragraph("Assigned to: Marcus Vance to wire CAN bus transceiver and optocoupler isolation boards by November 12, 2026.")
        d_cass.add_heading("Environmental Risks & Thermal Considerations", level=2)
        d_cass.add_paragraph("Risk: Direct solar glare at 12:00 PM saturates front wide-angle camera exposure.")
        d_cass.add_paragraph("Risk: High battery pack thermal throttling during continuous 35°C outdoor testing.")
        d_cass.add_paragraph("Open question: Will facilities provide dedicated 220V 32A charging bays near the engineering depot or must we use mobile generators?")
        d_cass.save(cass_docx)
        p2_files["Sensor_Rig_Specifications.docx"] = cass_docx

        # Sprint Backlog TXT
        cass_txt = os.path.join(FEED_DIR, "Sprint_Backlog_ROS2.txt")
        with open(cass_txt, "w", encoding="utf-8") as f:
            f.write("""# CASS ROS2 NAVIGATION SPRINT BACKLOG

Task: Dual LiDAR Pointcloud Stitching Node
Status: Completed
Owner: Marcus Vance
Description: Implemented voxel grid filter and pointcloud concatenation package with 20Hz publishing rate.

Task: Pedestrian Intent & Trajectory Prediction
Status: In Progress
Owner: Priya Sharma
Target Date: November 22, 2026
Description: Developing Kalman filter tracker for crossing bicycles and pedestrians.

Task: Teleoperation Fallback Dashboard UI
Status: Pending
Owner: Not found in available sources
Description: WebRTC low-latency streaming dashboard for remote operator override. Target completion pending.
""")
        p2_files["Sprint_Backlog_ROS2.txt"] = cass_txt

        # Ingest P2 docs
        p2_passages = []
        p2_doc_records = []
        for filename, filepath in p2_files.items():
            doc_rec = Document(
                project_id=p2.id,
                filename=filename,
                file_type=os.path.splitext(filename)[1].lstrip("."),
                file_size=os.path.getsize(filepath),
                file_path=filepath,
                uploader_id=lead_user.id,
                is_processed=True
            )
            db.add(doc_rec)
            db.commit()
            db.refresh(doc_rec)
            p2_doc_records.append(doc_rec)

            extracted = extract_document(filepath, filename)
            for p in extracted:
                pass_rec = DocumentPassage(
                    document_id=doc_rec.id,
                    passage_number=p["passage_number"],
                    page_number=p.get("page_number", 1),
                    section_title=p.get("section_title"),
                    content=p["content"],
                    char_start=p["char_start"],
                    char_end=p["char_end"]
                )
                db.add(pass_rec)
                db.commit()
                db.refresh(pass_rec)

                p2_passages.append({
                    "id": pass_rec.id,
                    "document_id": doc_rec.id,
                    "filename": filename,
                    "page_number": pass_rec.page_number,
                    "content": pass_rec.content
                })

        extracted_data2 = run_deterministic_extraction(p2_passages)
        p2_claim_records = []
        for c in extracted_data2["claims"]:
            claim_rec = ExtractedClaim(
                project_id=p2.id,
                category=c["category"],
                title=c["title"],
                description=c["description"],
                owner=c.get("owner"),
                date_reference=c.get("date_reference"),
                confidence=c.get("confidence", 0.9),
                verification_status=c.get("verification_status", "VERIFIED")
            )
            db.add(claim_rec)
            db.commit()
            db.refresh(claim_rec)
            p2_claim_records.append(claim_rec)

            if c.get("passage_id"):
                ev = ClaimEvidence(
                    claim_id=claim_rec.id,
                    passage_id=c["passage_id"],
                    excerpt=c.get("excerpt", c["description"])
                )
                db.add(ev)
                db.commit()

        # Generate DRAFT Handover for P2 (showing active review status)
        h2_data = generate_handover_report(p2, p2_claim_records, p2_doc_records)
        h2 = Handover(
            project_id=p2.id,
            version="1.0",
            status="DRAFT",
            title=h2_data["title"],
            executive_summary=h2_data["executive_summary"],
            current_status=h2_data["current_status"],
            recommended_actions=h2_data["recommended_actions"],
            missing_information=h2_data["missing_information"],
            conflicting_information=h2_data["conflicting_information"],
            created_by_id=lead_user.id
        )
        db.add(h2)
        db.commit()
        db.refresh(h2)

        for item in h2_data["items"]:
            item_rec = HandoverItem(
                handover_id=h2.id,
                claim_id=item["claim_id"],
                section=item["section"],
                title=item["title"],
                content=item["content"],
                source_filename=item["source_filename"],
                source_page=item["source_page"],
                evidence_excerpt=item["evidence_excerpt"],
                verification_status=item["verification_status"],
                is_accepted=True,
                is_rejected=False,
                is_redacted=False,
                display_order=item["display_order"]
            )
            db.add(item_rec)
        db.commit()

        db.add(AuditLog(project_id=p2.id, user_id=lead_user.id, user_name=lead_user.full_name, action="PROJECT_CREATED", details="Robotics workspace initialized."))
        db.add(AuditLog(project_id=p2.id, user_id=lead_user.id, user_name=lead_user.full_name, action="DOCUMENTS_INGESTED", details="Ingested 3 ROS2 architecture and sensor files."))
        db.add(AuditLog(project_id=p2.id, user_id=lead_user.id, user_name=lead_user.full_name, action="AI_EXTRACTION_COMPLETED", details=f"Extracted {len(p2_claim_records)} claims with passage evidence."))
        db.add(AuditLog(project_id=p2.id, user_id=lead_user.id, user_name=lead_user.full_name, action="HANDOVER_DRAFTED", details="Draft Handover assembled, awaiting sensor calibration review."))
        db.commit()

    # -------------------------------------------------------------
    # PROJECT 3: CareLink Student Health & Tele-Counseling
    # -------------------------------------------------------------
    p3 = db.query(Project).filter(Project.title == "CareLink Student Wellness Platform", Project.lead_id == lead_user.id).first()
    if not p3:
        p3 = Project(
            title="CareLink Student Wellness Platform",
            description="Confidential campus mental health and tele-counseling appointment portal with end-to-end encrypted session records, automated clinical triage, and FERPA/HIPAA data protection.",
            status="COMPLETED",
            lead_id=lead_user.id
        )
        db.add(p3)
        db.commit()
        db.refresh(p3)

        p3_files = {}

        # Security PDF
        care_pdf = os.path.join(FEED_DIR, "Security_and_Compliance_Spec.pdf")
        doc_care = pymupdf.open()
        page_care = doc_care.new_page()
        page_care.insert_text(pymupdf.Point(40, 50), """CARELINK STUDENT HEALTH - SECURITY & COMPLIANCE SPECIFICATION
STRICT MEDICAL CONFIDENTIALITY · FERPA & HIPAA ALIGNED

1. Platform Scope
CareLink handles sensitive student psychiatric consultations, nurse triage queues, and prescription refill requests.
Status: Verification and Production Sign-off.

2. Architecture & Encryption Decisions
- Decided to adopt AES-256 envelope encryption for all psychiatric counselor appointment notes.
- Decided to enforce PostgreSQL row-level security (RLS) to restrict counselor access to assigned cases only.
- Decided to implement strict 15-minute idle session timeouts across all clinician workstations.

3. Key Milestones & Audit Requirements
- Third-party Penetration Test Sign-off: Due date October 28, 2026. Handled by Sarah Jenkins.
- Campus Health Center Rollout: Due date November 14, 2026.""", fontsize=10, fontname="helv")
        doc_care.save(care_pdf)
        doc_care.close()
        p3_files["Security_and_Compliance_Spec.pdf"] = care_pdf

        # Architecture TXT
        care_txt = os.path.join(FEED_DIR, "Database_Architecture_ADR.txt")
        with open(care_txt, "w", encoding="utf-8") as f:
            f.write("""# CARELINK DATABASE ARCHITECTURE DECISION RECORD

Task: Row-Level Security Schema Verification
Status: Completed
Owner: Sarah Jenkins
Description: Verified that clinicians cannot query patient records outside of their active case roster.

Task: Automated Clinical Crisis Escalation
Status: In Progress
Owner: Alex Chen
Target Date: November 12, 2026
Description: Implemented automated pager dispatch for high-risk triage assessments.

Risk: Unavailability of SMS gateway vendor during night hours requires email magic link fallback.
Open question: Who oversees cryptographic master key rotation every 90 days?
""")
        p3_files["Database_Architecture_ADR.txt"] = care_txt

        # Ingest P3 docs
        p3_passages = []
        p3_doc_records = []
        for filename, filepath in p3_files.items():
            doc_rec = Document(
                project_id=p3.id,
                filename=filename,
                file_type=os.path.splitext(filename)[1].lstrip("."),
                file_size=os.path.getsize(filepath),
                file_path=filepath,
                uploader_id=lead_user.id,
                is_processed=True
            )
            db.add(doc_rec)
            db.commit()
            db.refresh(doc_rec)
            p3_doc_records.append(doc_rec)

            extracted = extract_document(filepath, filename)
            for p in extracted:
                pass_rec = DocumentPassage(
                    document_id=doc_rec.id,
                    passage_number=p["passage_number"],
                    page_number=p.get("page_number", 1),
                    section_title=p.get("section_title"),
                    content=p["content"],
                    char_start=p["char_start"],
                    char_end=p["char_end"]
                )
                db.add(pass_rec)
                db.commit()
                db.refresh(pass_rec)

                p3_passages.append({
                    "id": pass_rec.id,
                    "document_id": doc_rec.id,
                    "filename": filename,
                    "page_number": pass_rec.page_number,
                    "content": pass_rec.content
                })

        extracted_data3 = run_deterministic_extraction(p3_passages)
        p3_claim_records = []
        for c in extracted_data3["claims"]:
            claim_rec = ExtractedClaim(
                project_id=p3.id,
                category=c["category"],
                title=c["title"],
                description=c["description"],
                owner=c.get("owner"),
                date_reference=c.get("date_reference"),
                confidence=c.get("confidence", 0.95),
                verification_status="VERIFIED"
            )
            db.add(claim_rec)
            db.commit()
            db.refresh(claim_rec)
            p3_claim_records.append(claim_rec)

            if c.get("passage_id"):
                ev = ClaimEvidence(
                    claim_id=claim_rec.id,
                    passage_id=c["passage_id"],
                    excerpt=c.get("excerpt", c["description"])
                )
                db.add(ev)
                db.commit()

        # Approved Handover for P3
        h3_data = generate_handover_report(p3, p3_claim_records, p3_doc_records)
        h3 = Handover(
            project_id=p3.id,
            version="1.0",
            status="APPROVED",
            title=h3_data["title"],
            executive_summary=h3_data["executive_summary"],
            current_status=h3_data["current_status"],
            recommended_actions=h3_data["recommended_actions"],
            missing_information=h3_data["missing_information"],
            conflicting_information="Zero contradictions detected in compliance records.",
            created_by_id=lead_user.id,
            approved_by_id=lead_user.id,
            approved_at=utc_now(),
            approval_notes="Security audit passed, HIPAA compliance standards validated, and database RLS verified for clinical launch."
        )
        db.add(h3)
        db.commit()
        db.refresh(h3)

        for item in h3_data["items"]:
            item_rec = HandoverItem(
                handover_id=h3.id,
                claim_id=item["claim_id"],
                section=item["section"],
                title=item["title"],
                content=item["content"],
                source_filename=item["source_filename"],
                source_page=item["source_page"],
                evidence_excerpt=item["evidence_excerpt"],
                verification_status="VERIFIED",
                is_accepted=True,
                is_rejected=False,
                is_redacted=False,
                display_order=item["display_order"]
            )
            db.add(item_rec)
        db.commit()

        db.add(AuditLog(project_id=p3.id, user_id=lead_user.id, user_name=lead_user.full_name, action="PROJECT_CREATED", details="CareLink compliance workspace initialized."))
        db.add(AuditLog(project_id=p3.id, user_id=lead_user.id, user_name=lead_user.full_name, action="DOCUMENTS_INGESTED", details="Security specifications and database ADR ingested."))
        db.add(AuditLog(project_id=p3.id, user_id=lead_user.id, user_name=lead_user.full_name, action="HANDOVER_APPROVED", details="Official Handover Report v1.0 signed off for clinical staff."))
        db.commit()

    # Always enrich Round 3 data (hash backfills, connector, snapshots, acknowledgment)
    enrich_round3_data(db, lead_user)


def enrich_round3_data(db: Session, lead_user: User):
    """
    Enriches existing or newly initialized databases with complete Round 3 demonstration records:
    1. Backfills SHA-256 hashes on all Document records.
    2. Creates HandoverSnapshot v1.0 records with SHA-256 hashes for all approved handovers.
    3. Connects the official GitHub repository ('Amanprajapati247/KnowBridge') with realistic commits, PRs, and issues.
    4. Creates a HandoverSnapshot v2.0 for Project 1 so judges can test version comparison (v1.0 vs v2.0).
    5. Creates a formal incoming-member HandoverAcknowledgment receipt signed by Jordan Reed.
    """
    # 1. Backfill Document SHA-256 hashes
    docs = db.query(Document).filter(Document.sha256_hash.is_(None)).all()
    for d in docs:
        if os.path.exists(d.file_path):
            d.sha256_hash = CryptoAuditService.calculate_file_sha256(d.file_path)
        else:
            d.sha256_hash = hashlib.sha256(f"seed-document-{d.id}-{d.filename}".encode()).hexdigest()
    if docs:
        db.commit()

    # Find Project 1 (College Event Management System)
    p1 = db.query(Project).filter(Project.title == "College Event Management System").first()
    if not p1:
        return

    # 2. Backfill HandoverSnapshot v1.0 for approved handovers
    approved_handovers = db.query(Handover).filter(Handover.status == "APPROVED").all()
    for h in approved_handovers:
        if not h.snapshot_hash:
            canonical_json, snap_hash = CryptoAuditService.serialize_handover_canonical(h)
            h.snapshot_hash = snap_hash
            db.commit()

        # Check if HandoverSnapshot exists
        existing_snap = db.query(HandoverSnapshot).filter(
            HandoverSnapshot.handover_id == h.id,
            HandoverSnapshot.version == h.version
        ).first()

        if not existing_snap:
            canonical_json, snap_hash = CryptoAuditService.serialize_handover_canonical(h)
            snap = HandoverSnapshot(
                handover_id=h.id,
                project_id=h.project_id,
                version=h.version,
                snapshot_hash=snap_hash,
                title=h.title,
                executive_summary=h.executive_summary,
                current_status=h.current_status,
                recommended_actions=h.recommended_actions,
                missing_information=h.missing_information,
                conflicting_information=h.conflicting_information,
                items_json=canonical_json,
                approved_by_id=h.approved_by_id or lead_user.id,
                approved_at=h.approved_at or utc_now(),
                approval_notes=h.approval_notes or "Handover officially verified and signed off."
            )
            db.add(snap)
            db.commit()

    # 3. Connect GitHub repository to Project 1
    gh_connector = db.query(ExternalConnector).filter(
        ExternalConnector.project_id == p1.id,
        ExternalConnector.provider == "GITHUB"
    ).first()

    if not gh_connector:
        gh_connector = ExternalConnector(
            project_id=p1.id,
            provider="GITHUB",
            name="Amanprajapati247/KnowBridge",
            repo_url="https://github.com/Amanprajapati247/KnowBridge",
            branch="main",
            status="SYNCED",
            last_synced_at=utc_now(),
            sync_summary="Initial synchronization completed. 6 Git records imported (3 commits, 2 PRs, 1 issue). Extracted 4 architectural decision claims."
        )
        db.add(gh_connector)
        db.commit()
        db.refresh(gh_connector)

        # Seed realistic GitHub commits, PRs, issues
        seed_git_records = [
            {
                "id": "e0a65a3",
                "type": "COMMIT",
                "title": "Commit: Add SHA-256 cryptographic hashing for source files and snapshots",
                "desc": "ADR Decision: Adopted SHA-256 content hashing over canonical JSON serialization for tamper detection and historical version preservation.",
                "author": "Aman Prajapati",
                "url": "https://github.com/Amanprajapati247/KnowBridge/commit/e0a65a3"
            },
            {
                "id": "871dec2",
                "type": "COMMIT",
                "title": "Commit: Implement hybrid BM25 and dense vector retrieval pipeline",
                "desc": "Architecture: Combined Okapi BM25 lexical search with 128-dimensional L2-normalized dense embeddings via Reciprocal Rank Fusion.",
                "author": "Aman Prajapati",
                "url": "https://github.com/Amanprajapati247/KnowBridge/commit/871dec2"
            },
            {
                "id": "00ced15",
                "type": "COMMIT",
                "title": "Commit: Single-port unified Docker deployment serving FastAPI and React SPA",
                "desc": "Refactored deployment to serve compiled React assets from FastAPI to eliminate CORS overhead on cloud hosts.",
                "author": "Aman Prajapati",
                "url": "https://github.com/Amanprajapati247/KnowBridge/commit/00ced15"
            },
            {
                "id": "PR-14",
                "type": "PULL_REQUEST",
                "title": "PR #14: Role-based authorization gate for incoming member handover portal",
                "desc": "Enforces server-side 403 Forbidden checks for incoming members attempting to query unapproved draft handovers or restricted documents.",
                "author": "Aman Prajapati",
                "url": "https://github.com/Amanprajapati247/KnowBridge/pull/14"
            },
            {
                "id": "PR-12",
                "type": "PULL_REQUEST",
                "title": "PR #12: Offline-capable QR token verification service",
                "desc": "Implemented HMAC-SHA256 offline verification protocol for student attendee ticketing scanners.",
                "author": "Priya Sharma",
                "url": "https://github.com/Amanprajapati247/KnowBridge/pull/12"
            },
            {
                "id": "ISSUE-29",
                "type": "ISSUE",
                "title": "Issue #29: High concurrent traffic connection pool exhaustion under festival registration spikes",
                "desc": "Risk: Load testing revealed SQLAlchemy connection pool starvation when concurrent requests exceed 500 req/s. Solution: Configured NullPool and async connection recycling.",
                "author": "Marcus Vance",
                "url": "https://github.com/Amanprajapati247/KnowBridge/issues/29"
            }
        ]

        for gr in seed_git_records:
            rec = ExternalRecord(
                connector_id=gh_connector.id,
                project_id=p1.id,
                external_id=gr["id"],
                record_type=gr["type"],
                title=gr["title"],
                description=gr["desc"],
                author=gr["author"],
                author_url="https://github.com/Amanprajapati247",
                external_url=gr["url"],
                created_at_external=utc_now(),
                is_imported_to_claims=True
            )
            db.add(rec)
        db.commit()

        # Connect a Jira board demo connector
        jira_connector = ExternalConnector(
            project_id=p1.id,
            provider="JIRA",
            name="CEMS-BOARD",
            repo_url="https://knowbridge.atlassian.net",
            branch="main",
            status="CONNECTED",
            last_synced_at=utc_now(),
            sync_summary="Jira connector registered. Live sync ready when JIRA_API_TOKEN is supplied in environment."
        )
        db.add(jira_connector)
        db.commit()

    # 4. Create HandoverSnapshot v2.0 for Project 1 (for version comparison demo)
    h1 = db.query(Handover).filter(Handover.project_id == p1.id).order_by(Handover.id.asc()).first()
    if h1:
        snap_v2 = db.query(HandoverSnapshot).filter(
            HandoverSnapshot.handover_id == h1.id,
            HandoverSnapshot.version == "2.0"
        ).first()

        if not snap_v2:
            snap_v1 = db.query(HandoverSnapshot).filter(
                HandoverSnapshot.handover_id == h1.id,
                HandoverSnapshot.version == "1.0"
            ).first()

            if snap_v1:
                v1_data = json.loads(snap_v1.items_json)
                v2_items = list(v1_data.get("items", []))

                # Add a newly completed task in v2.0
                v2_items.append({
                    "claim_id": 9991,
                    "section": "COMPLETED_TASKS",
                    "title": "Completed: SHA-256 Tamper Verification Engine",
                    "content": "Delivered cryptographic hash calculation and audit log integrity verification across all uploaded sources.",
                    "source_filename": "Git Commit e0a65a3",
                    "source_page": 1,
                    "evidence_excerpt": "Commit e0a65a3: Add SHA-256 cryptographic hashing for source files and snapshots",
                    "verification_status": "VERIFIED",
                    "is_accepted": True,
                    "is_rejected": False,
                    "is_redacted": False
                })

                # Add a newly extracted architectural decision in v2.0
                v2_items.append({
                    "claim_id": 9992,
                    "section": "DECISIONS",
                    "title": "Decided: Reciprocal Rank Fusion for Hybrid Retrieval",
                    "content": "Adopted RRF (k=60) combining BM25 keyword rankings with normalized 128-d dense vector embeddings.",
                    "source_filename": "Git Commit 871dec2",
                    "source_page": 1,
                    "evidence_excerpt": "Commit 871dec2: Implement hybrid BM25 and dense vector retrieval pipeline",
                    "verification_status": "VERIFIED",
                    "is_accepted": True,
                    "is_rejected": False,
                    "is_redacted": False
                })

                v2_dict = {
                    "handover_id": h1.id,
                    "project_id": p1.id,
                    "version": "2.0",
                    "title": "Official Handover Report v2.0 - College Event Management System",
                    "executive_summary": h1.executive_summary + " Updated in v2.0 with GitHub commits, hybrid RAG embeddings, and resolved Beta launch milestones.",
                    "current_status": "Project is in 'PRODUCTION_READY' state. All high-priority deliverables completed and signed off.",
                    "recommended_actions": "1. Validate production deployment on Railway.\n2. Review cryptographic audit trail.\n3. Conduct incoming member Q&A walkthrough.",
                    "missing_information": "All required technical owners and milestones identified in repository and specifications.",
                    "conflicting_information": "All cross-document contradictions formally resolved in v2.0.",
                    "items": v2_items
                }
                v2_canonical = json.dumps(v2_dict, sort_keys=True, separators=(',', ':'))
                v2_hash = hashlib.sha256(v2_canonical.encode('utf-8')).hexdigest()

                snap_v2 = HandoverSnapshot(
                    handover_id=h1.id,
                    project_id=p1.id,
                    version="2.0",
                    snapshot_hash=v2_hash,
                    title="Official Handover Report v2.0 - College Event Management System",
                    executive_summary=v2_dict["executive_summary"],
                    current_status=v2_dict["current_status"],
                    recommended_actions=v2_dict["recommended_actions"],
                    missing_information=v2_dict["missing_information"],
                    conflicting_information=v2_dict["conflicting_information"],
                    items_json=v2_canonical,
                    approved_by_id=lead_user.id,
                    approved_at=utc_now(),
                    approval_notes="Round 3 updated handover report with Git integration and hybrid search verified."
                )
                db.add(snap_v2)
                db.commit()

        # 5. Seed Incoming Member Acknowledgment receipt
        incoming_users = db.query(User).filter(User.role == "INCOMING_MEMBER").all()
        for incoming_user in incoming_users:
            existing_ack = db.query(HandoverAcknowledgment).filter(
                HandoverAcknowledgment.handover_id == h1.id,
                HandoverAcknowledgment.user_id == incoming_user.id
            ).first()

            if not existing_ack:
                CryptoAuditService.record_acknowledgment(
                    db=db,
                    handover=h1,
                    user=incoming_user,
                    signature_notes="Verified executive summary, pending deliverables, and risk mitigation plan. Ready to commence onboarding."
                )

