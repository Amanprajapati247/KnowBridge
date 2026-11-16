export type UserRole = 'PROJECT_LEAD' | 'INCOMING_MEMBER';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  full_name: string;
  email: string;
  user_id: number;
}

export interface Project {
  id: number;
  title: string;
  description?: string;
  status: 'ACTIVE' | 'IN_REVIEW' | 'COMPLETED' | 'ARCHIVED';
  lead_id: number;
  created_at: string;
  updated_at: string;
  document_count: number;
  claim_count: number;
  handover_status?: 'NOT_STARTED' | 'DRAFT' | 'APPROVED' | 'ARCHIVED';
}

export interface DocumentItem {
  id: number;
  project_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  sha256_hash?: string;
  uploaded_at: string;
  is_processed: boolean;
  passage_count: number;
}

export interface DocumentPassage {
  id: number;
  document_id: number;
  passage_number: number;
  page_number?: number;
  section_title?: string;
  content: string;
  char_start: number;
  char_end: number;
}

export interface ClaimEvidence {
  id: number;
  passage_id: number;
  excerpt: string;
  page_number?: number;
  filename?: string;
  relevance_note?: string;
}

export type VerificationStatus = 'VERIFIED' | 'UNCERTAIN' | 'CONFLICT';

export interface ExtractedClaim {
  id: number;
  project_id: number;
  category: 'DECISION' | 'TASK' | 'RESPONSIBILITY' | 'DEADLINE' | 'RISK' | 'BLOCKER' | 'DEPENDENCY' | 'UNRESOLVED_QUESTION' | 'MILESTONE' | 'CONTACT';
  title: string;
  description: string;
  owner?: string;
  date_reference?: string;
  confidence: number;
  verification_status: VerificationStatus;
  conflict_details?: string;
  is_resolved: boolean;
  resolution_notes?: string;
  created_at: string;
  evidences: ClaimEvidence[];
}

export interface HandoverItem {
  id: number;
  handover_id: number;
  claim_id?: number;
  section: string;
  title: string;
  content: string;
  source_filename?: string;
  source_page?: number;
  evidence_excerpt?: string;
  verification_status: VerificationStatus;
  is_accepted: boolean;
  is_rejected: boolean;
  is_redacted: boolean;
  reviewer_notes?: string;
  display_order: number;
}

export interface Handover {
  id: number;
  project_id: number;
  version: string;
  status: 'DRAFT' | 'APPROVED' | 'ARCHIVED';
  title: string;
  executive_summary?: string;
  current_status?: string;
  recommended_actions?: string;
  missing_information?: string;
  conflicting_information?: string;
  created_by_id: number;
  created_at: string;
  approved_by_id?: number;
  approved_at?: string;
  approval_notes?: string;
  snapshot_hash?: string;
  items: HandoverItem[];
}

export interface AuditLog {
  id: number;
  project_id?: number;
  user_id?: number;
  user_name?: string;
  action: string;
  details?: string;
  sha256_hash?: string;
  timestamp: string;
}

export interface DashboardStats {
  total_projects: number;
  total_documents: number;
  generated_handovers: number;
  pending_reviews: number;
  open_tasks: number;
  identified_risks: number;
  conflicts_count: number;
}

// --- ROUND 3 TYPES ---

export interface ExternalRecord {
  id: number;
  connector_id: number;
  project_id: number;
  external_id: string;
  record_type: 'COMMIT' | 'PULL_REQUEST' | 'ISSUE' | 'REVIEW';
  title: string;
  description?: string;
  author?: string;
  author_url?: string;
  external_url?: string;
  created_at_external?: string;
  is_imported_to_claims: boolean;
  created_at: string;
}

export interface ExternalConnector {
  id: number;
  project_id: number;
  provider: 'GITHUB' | 'JIRA' | 'LINEAR';
  name: string;
  repo_url?: string;
  branch: string;
  status: 'CONNECTED' | 'SYNCED' | 'ERROR' | 'DISCONNECTED';
  last_synced_at?: string;
  sync_summary?: string;
  error_message?: string;
  created_at: string;
  records_count: number;
}

export interface ConnectorSyncResult {
  connector_id: number;
  provider: string;
  status: string;
  synced_records: number;
  new_claims_extracted: number;
  sync_summary: string;
  error_message?: string;
}

export interface RAGCitation {
  document_id?: number;
  filename: string;
  page_number?: number;
  passage_id?: number;
  excerpt: string;
  relevance_score: number;
  source_type: 'DOCUMENT' | 'GITHUB' | 'TASK' | 'HANDOVER_REPORT' | 'HANDOVER_ITEM';
  external_url?: string;
}

export interface RAGQueryResponse {
  question: string;
  answer: string;
  confidence: number;
  evidence_status: 'VERIFIED' | 'UNCERTAIN' | 'CONFLICT';
  citations: RAGCitation[];
  conflicts_detected: string[];
  missing_information?: string;
  retrieval_mode: string;
}

export interface HandoverSnapshot {
  id: number;
  handover_id: number;
  project_id: number;
  version: string;
  snapshot_hash: string;
  title: string;
  executive_summary?: string;
  current_status?: string;
  created_at: string;
  approved_by_id?: number;
  approved_at?: string;
  approval_notes?: string;
}

export interface VersionDiffItem {
  change_type: 'ADDED' | 'REMOVED' | 'MODIFIED' | 'UNCHANGED';
  section: string;
  title: string;
  old_content?: string;
  new_content?: string;
  verification_status: VerificationStatus;
  source_filename?: string;
}

export interface HandoverVersionCompare {
  project_id: number;
  v1_version: string;
  v2_version: string;
  v1_hash: string;
  v2_hash: string;
  v1_approved_at?: string;
  v2_approved_at?: string;
  added_count: number;
  removed_count: number;
  modified_count: number;
  unchanged_count: number;
  diff_items: VersionDiffItem[];
  summary: string;
}

export interface HandoverAcknowledgment {
  id: number;
  handover_id: number;
  snapshot_id?: number;
  project_id: number;
  user_id: number;
  version: string;
  snapshot_hash: string;
  receipt_token: string;
  signature_notes?: string;
  acknowledged_at: string;
  user_name?: string;
}

export interface AcknowledgmentReceipt {
  receipt_token: string;
  handover_id: number;
  handover_title: string;
  version: string;
  snapshot_hash: string;
  project_id: number;
  project_title: string;
  user_id: number;
  user_name: string;
  user_email: string;
  acknowledged_at: string;
  signature_notes?: string;
  cryptographic_algorithm: string;
  verification_statement: string;
  is_valid: boolean;
}
