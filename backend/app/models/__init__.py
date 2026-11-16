from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Table
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="PROJECT_LEAD", nullable=False)  # "PROJECT_LEAD" or "INCOMING_MEMBER"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    projects = relationship("Project", back_populates="lead", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploader")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, IN_REVIEW, COMPLETED, ARCHIVED
    lead_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    lead = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    claims = relationship("ExtractedClaim", back_populates="project", cascade="all, delete-orphan")
    handovers = relationship("Handover", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project", cascade="all, delete-orphan")
    connectors = relationship("ExternalConnector", back_populates="project", cascade="all, delete-orphan")
    snapshots = relationship("HandoverSnapshot", back_populates="project", cascade="all, delete-orphan")
    acknowledgments = relationship("HandoverAcknowledgment", back_populates="project", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=utc_now)
    extracted_text = Column(Text, nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    is_processed = Column(Boolean, default=False)

    project = relationship("Project", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
    passages = relationship("DocumentPassage", back_populates="document", cascade="all, delete-orphan")

class DocumentPassage(Base):
    __tablename__ = "document_passages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    passage_number = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    char_start = Column(Integer, default=0)
    char_end = Column(Integer, default=0)

    document = relationship("Document", back_populates="passages")
    evidences = relationship("ClaimEvidence", back_populates="passage", cascade="all, delete-orphan")

class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String(50), nullable=False)  # DECISION, TASK, RESPONSIBILITY, DEADLINE, RISK, BLOCKER, DEPENDENCY, UNRESOLVED_QUESTION, MILESTONE, CONTACT
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    owner = Column(String(255), nullable=True)
    date_reference = Column(String(100), nullable=True)
    confidence = Column(Float, default=1.0)
    verification_status = Column(String(50), default="VERIFIED")  # VERIFIED, UNCERTAIN, CONFLICT
    conflict_details = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="claims")
    evidences = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")

class ClaimEvidence(Base):
    __tablename__ = "claim_evidences"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("extracted_claims.id"), nullable=False)
    passage_id = Column(Integer, ForeignKey("document_passages.id"), nullable=False)
    excerpt = Column(Text, nullable=False)
    relevance_note = Column(String(255), nullable=True)

    claim = relationship("ExtractedClaim", back_populates="evidences")
    passage = relationship("DocumentPassage", back_populates="evidences")

class Handover(Base):
    __tablename__ = "handovers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(String(50), default="1.0")
    status = Column(String(50), default="DRAFT")  # DRAFT, APPROVED, ARCHIVED
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=True)
    current_status = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    conflicting_information = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    snapshot_hash = Column(String(64), nullable=True)

    project = relationship("Project", back_populates="handovers")
    items = relationship("HandoverItem", back_populates="handover", cascade="all, delete-orphan")
    snapshots = relationship("HandoverSnapshot", back_populates="handover", cascade="all, delete-orphan")
    acknowledgments = relationship("HandoverAcknowledgment", back_populates="handover", cascade="all, delete-orphan")

class HandoverItem(Base):
    __tablename__ = "handover_items"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("handovers.id"), nullable=False)
    claim_id = Column(Integer, ForeignKey("extracted_claims.id"), nullable=True)
    section = Column(String(100), nullable=False)  # DECISIONS, COMPLETED_TASKS, PENDING_TASKS, RESPONSIBILITIES, RISKS_BLOCKERS, DEPENDENCIES, UNRESOLVED_QUESTIONS, NEXT_ACTIONS, SOURCE_REFERENCES, MISSING_INFO, CONFLICT_INFO
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_filename = Column(String(255), nullable=True)
    source_page = Column(Integer, nullable=True)
    evidence_excerpt = Column(Text, nullable=True)
    verification_status = Column(String(50), default="VERIFIED")  # VERIFIED, UNCERTAIN, CONFLICT
    is_accepted = Column(Boolean, default=True)
    is_rejected = Column(Boolean, default=False)
    is_redacted = Column(Boolean, default=False)
    reviewer_notes = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)

    handover = relationship("Handover", back_populates="items")
    claim = relationship("ExtractedClaim")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="audit_logs")

class ExternalConnector(Base):
    __tablename__ = "external_connectors"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # "GITHUB", "JIRA", "LINEAR"
    name = Column(String(255), nullable=False)      # e.g. "Amanprajapati247/KnowBridge"
    repo_url = Column(String(500), nullable=True)
    branch = Column(String(100), default="main")
    status = Column(String(50), default="CONNECTED")  # "CONNECTED", "SYNCED", "ERROR", "DISCONNECTED"
    last_synced_at = Column(DateTime, nullable=True)
    sync_cursor = Column(String(255), nullable=True)   # latest commit SHA or last sync marker
    sync_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="connectors")
    records = relationship("ExternalRecord", back_populates="connector", cascade="all, delete-orphan")

class ExternalRecord(Base):
    __tablename__ = "external_records"

    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("external_connectors.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    external_id = Column(String(255), nullable=False)  # Commit SHA, PR #, or Issue Key
    record_type = Column(String(50), nullable=False)   # "COMMIT", "PULL_REQUEST", "ISSUE", "REVIEW"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    author_url = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    created_at_external = Column(DateTime, nullable=True)
    raw_data_json = Column(Text, nullable=True)
    is_imported_to_claims = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    connector = relationship("ExternalConnector", back_populates="records")

class HandoverSnapshot(Base):
    __tablename__ = "handover_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("handovers.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(String(50), nullable=False)
    snapshot_hash = Column(String(64), nullable=False)  # Cryptographic SHA-256
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=True)
    current_status = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    conflicting_information = Column(Text, nullable=True)
    items_json = Column(Text, nullable=False)  # Canonical JSON snapshot of all approved items
    created_at = Column(DateTime, default=utc_now)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    handover = relationship("Handover", back_populates="snapshots")
    project = relationship("Project", back_populates="snapshots")
    acknowledgments = relationship("HandoverAcknowledgment", back_populates="snapshot", cascade="all, delete-orphan")

class HandoverAcknowledgment(Base):
    __tablename__ = "handover_acknowledgments"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("handovers.id"), nullable=False)
    snapshot_id = Column(Integer, ForeignKey("handover_snapshots.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(String(50), nullable=False)
    snapshot_hash = Column(String(64), nullable=False)
    receipt_token = Column(String(64), nullable=False)  # SHA-256(user_id:handover_id:version:snapshot_hash:timestamp)
    signature_notes = Column(Text, nullable=True)
    acknowledged_at = Column(DateTime, default=utc_now)

    user = relationship("User")
    handover = relationship("Handover", back_populates="acknowledgments")
    snapshot = relationship("HandoverSnapshot", back_populates="acknowledgments")
    project = relationship("Project", back_populates="acknowledgments")
