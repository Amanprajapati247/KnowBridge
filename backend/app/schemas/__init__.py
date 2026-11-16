from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    password: str = Field(min_length=6)
    full_name: str
    role: str = "PROJECT_LEAD"  # "PROJECT_LEAD" or "INCOMING_MEMBER"

class UserLogin(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    email: str
    user_id: int

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

# --- PROJECT SCHEMAS ---
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    status: str
    lead_id: int
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    claim_count: int = 0
    handover_status: Optional[str] = "NOT_STARTED"

# --- DOCUMENT SCHEMAS ---
class PassageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: int
    passage_number: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    content: str
    char_start: int
    char_end: int

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    filename: str
    file_type: str
    file_size: int
    sha256_hash: Optional[str] = None
    uploaded_at: datetime
    is_processed: bool
    passage_count: int = 0

# --- CLAIM & EVIDENCE SCHEMAS ---
class ClaimEvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    passage_id: int
    excerpt: str
    page_number: Optional[int] = None
    filename: Optional[str] = None
    relevance_note: Optional[str] = None

class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    category: str
    title: str
    description: str
    owner: Optional[str] = None
    date_reference: Optional[str] = None
    confidence: float
    verification_status: str
    conflict_details: Optional[str] = None
    is_resolved: bool
    resolution_notes: Optional[str] = None
    created_at: datetime
    evidences: List[ClaimEvidenceOut] = []

class ClaimResolve(BaseModel):
    resolution_notes: str
    chosen_date: Optional[str] = None
    chosen_owner: Optional[str] = None

# --- HANDOVER SCHEMAS ---
class HandoverItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    handover_id: int
    claim_id: Optional[int] = None
    section: str
    title: str
    content: str
    source_filename: Optional[str] = None
    source_page: Optional[int] = None
    evidence_excerpt: Optional[str] = None
    verification_status: str
    is_accepted: bool
    is_rejected: bool
    is_redacted: bool
    reviewer_notes: Optional[str] = None
    display_order: int

class HandoverItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_accepted: Optional[bool] = None
    is_rejected: Optional[bool] = None
    is_redacted: Optional[bool] = None
    reviewer_notes: Optional[str] = None

class HandoverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    version: str
    status: str
    title: str
    executive_summary: Optional[str] = None
    current_status: Optional[str] = None
    recommended_actions: Optional[str] = None
    missing_information: Optional[str] = None
    conflicting_information: Optional[str] = None
    created_by_id: int
    created_at: datetime
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    snapshot_hash: Optional[str] = None
    items: List[HandoverItemOut] = []

class HandoverApprove(BaseModel):
    approval_notes: Optional[str] = None

# --- AUDIT SCHEMAS ---
class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    details: Optional[str] = None
    sha256_hash: Optional[str] = None
    timestamp: datetime

# --- STATS SCHEMAS ---
class MainDashboardStats(BaseModel):
    total_projects: int
    total_documents: int
    generated_handovers: int
    pending_reviews: int
    open_tasks: int
    identified_risks: int
    conflicts_count: int

# --- CONNECTOR SCHEMAS ---
class ConnectorConnect(BaseModel):
    provider: str  # "GITHUB", "JIRA", "LINEAR"
    repo_name_or_key: str  # e.g. "Amanprajapati247/KnowBridge" or "PROJ"
    repo_url: Optional[str] = None
    branch: Optional[str] = "main"
    access_token: Optional[str] = None  # Handled securely, not stored directly in public fields
    instance_url: Optional[str] = None  # for Jira (e.g. "https://company.atlassian.net")

class ExternalRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    connector_id: int
    project_id: int
    external_id: str
    record_type: str  # "COMMIT", "PULL_REQUEST", "ISSUE", "REVIEW"
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None
    external_url: Optional[str] = None
    created_at_external: Optional[datetime] = None
    is_imported_to_claims: bool
    created_at: datetime

class ConnectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    provider: str
    name: str
    repo_url: Optional[str] = None
    branch: str
    status: str
    last_synced_at: Optional[datetime] = None
    sync_summary: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    records_count: int = 0

class ConnectorSyncResult(BaseModel):
    connector_id: int
    provider: str
    status: str
    synced_records: int
    new_claims_extracted: int
    sync_summary: str
    error_message: Optional[str] = None

# --- RAG & Q&A SCHEMAS ---
class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=2)
    top_k: int = 5

class RAGCitation(BaseModel):
    document_id: Optional[int] = None
    filename: str
    page_number: Optional[int] = None
    passage_id: Optional[int] = None
    excerpt: str
    relevance_score: float
    source_type: str = "DOCUMENT"  # "DOCUMENT", "GITHUB", "JIRA", "LINEAR"
    external_url: Optional[str] = None

class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    evidence_status: str  # "VERIFIED", "UNCERTAIN", "CONFLICT"
    citations: List[RAGCitation] = []
    conflicts_detected: List[str] = []
    missing_information: Optional[str] = None
    retrieval_mode: str = "HYBRID_BM25_DENSE"

# --- VERSION HISTORY & COMPARISON SCHEMAS ---
class HandoverSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    handover_id: int
    project_id: int
    version: str
    snapshot_hash: str
    title: str
    executive_summary: Optional[str] = None
    current_status: Optional[str] = None
    created_at: datetime
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None

class VersionDiffItem(BaseModel):
    change_type: str  # "ADDED", "REMOVED", "MODIFIED", "UNCHANGED"
    section: str
    title: str
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    verification_status: str
    source_filename: Optional[str] = None

class HandoverVersionCompareOut(BaseModel):
    project_id: int
    v1_version: str
    v2_version: str
    v1_hash: str
    v2_hash: str
    v1_approved_at: Optional[datetime] = None
    v2_approved_at: Optional[datetime] = None
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    diff_items: List[VersionDiffItem]
    summary: str

# --- ACKNOWLEDGMENT SCHEMAS ---
class AcknowledgmentCreate(BaseModel):
    signature_notes: Optional[str] = None

class HandoverAcknowledgmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    handover_id: int
    snapshot_id: Optional[int] = None
    project_id: int
    user_id: int
    version: str
    snapshot_hash: str
    receipt_token: str
    signature_notes: Optional[str] = None
    acknowledged_at: datetime
    user_name: Optional[str] = None

class AcknowledgmentReceiptOut(BaseModel):
    receipt_token: str
    handover_id: int
    handover_title: str
    version: str
    snapshot_hash: str
    project_id: int
    project_title: str
    user_id: int
    user_name: str
    user_email: str
    acknowledged_at: datetime
    signature_notes: Optional[str] = None
    cryptographic_algorithm: str = "SHA-256"
    verification_statement: str
    is_valid: bool = True
