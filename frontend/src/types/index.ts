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
  items: HandoverItem[];
}

export interface AuditLog {
  id: number;
  project_id?: number;
  user_id?: number;
  user_name?: string;
  action: string;
  details?: string;
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
