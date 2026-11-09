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
