# KnowBridge Architecture & System Design
**Tech Titan | Hackathon Round 2 | Individual Participant**
**Tagline:** *Knowledge Should Never Leave With People.*

---

## 1. Executive Summary

KnowBridge is an intelligent, evidence-backed project knowledge-handover platform designed to prevent critical institutional and technical context from disappearing when employees, students, developers, or volunteers depart.

Unlike generic LLM summarizers that suffer from hallucination and lack accountability, KnowBridge enforces:
1. **Strict Evidence Traceability:** Every factual statement links back to source files and exact passages/pages.
2. **Explicit Verification States:** Items are classified as `VERIFIED`, `UNCERTAIN`, or `CONFLICT`.
3. **Deterministic Conflict Resolution:** Conflicting facts across documents are surfaced side-by-side rather than arbitrarily picked.
4. **Human-in-the-Loop Governance:** Project leads edit, redact, and approve reports.
5. **Backend-Enforced Role Separation:** Incoming members can only view approved handovers, protecting sensitive source materials.

---

## 2. System Architecture

```
+---------------------------------------------------------------------------------+
|                                 FRONTEND                                        |
|  React 18+ / TypeScript / Vite / Tailwind CSS / Lucide Icons / Recharts          |
|  - Landing Page & Value Proposition                                             |
|  - Auth & Role Switching (Project Lead vs Incoming Member)                      |
|  - Main Dashboard (KPI Metrics, Project Directory, Demo Seeder)                |
|  - Workspace: Overview, Document Hub, AI Extraction, Evidence & Conflicts      |
|  - Handover Review Studio (Edit, Accept, Reject, Redact, Versioning, Approve)   |
|  - Incoming Member Continuation Portal (Strictly read-only approved views)      |
+---------------------------------------------------------------------------------+
                                      |  REST APIs (JWT Bearer Auth)
                                      v
+---------------------------------------------------------------------------------+
|                                 BACKEND                                         |
|  FastAPI (Python 3.13) / Pydantic v2 / SQLAlchemy 2.0                            |
|                                                                                 |
|  [API Router Layer]                                                             |
|   ├── /api/auth             (Register, Login, Me, Token refresh)                |
|   ├── /api/projects         (CRUD, stats, members)                              |
|   ├── /api/documents        (Upload PDF/DOCX/TXT, metadata, delete)             |
|   ├── /api/analysis         (Extract claims, passages, run extraction)          |
|   ├── /api/conflicts        (Detect & resolve cross-document discrepancies)     |
|   ├── /api/handovers        (Draft generation, review, edit, approve, versions) |
|   ├── /api/incoming         (Permitted views for incoming onboarders)           |
|   └── /api/activity         (Audit log & compliance trail)                      |
|                                                                                 |
|  [Core Services Layer]                                                          |
|   ├── Document Extractor    (PyMuPDF for PDF, python-docx, TXT chunker)         |
|   ├── AI Engine Abstraction (LLM API provider + Deterministic Demo Engine)      |
|   ├── Conflict Detector     (Cross-source date/owner/scope reconciliation)      |
|   ├── Handover Assembler    (14 standard sections + evidence mapping)           |
|   └── Demo Seeder           (College Event Management System generator)         |
|                                                                                 |
|  [Persistence Layer]                                                            |
|   SQLite (Local dev) / PostgreSQL (Production ready)                            |
+---------------------------------------------------------------------------------+
```

---

## 3. Database Schema Entity Relationship

```
+---------------+        1:N        +------------------+
|     User      |-------------------|     Project      |
|---------------|                   |------------------|
| id (PK)       |                   | id (PK)          |
| email         |                   | title            |
| password_hash |                   | description      |
| full_name     |                   | status           |
| role          |                   | lead_id (FK)     |
+---------------+                   +------------------+
        |                                     |
        | 1:N                                 | 1:N
        v                                     v
+---------------+                   +------------------+        1:N        +-------------------+
|  Audit Log    |                   |    Document      |-------------------| Document Passage  |
|---------------|                   |------------------|                   |-------------------|
| id (PK)       |                   | id (PK)          |                   | id (PK)           |
| project_id    |                   | project_id (FK)  |                   | document_id (FK)  |
| user_id (FK)  |                   | filename         |                   | passage_text      |
| action        |                   | file_type        |                   | page_number       |
| details       |                   | file_size        |                   | section_title     |
| timestamp     |                   | file_path        |                   | char_offset       |
+---------------+                   +------------------+                   +-------------------+
                                              |                                      |
                                              | 1:N                                  | 1:N
                                              v                                      v
                                    +------------------+                   +-------------------+
                                    | Extracted Claim  |<------------------|  Evidence Link    |
                                    |------------------|                   +-------------------+
                                    | id (PK)          |
                                    | project_id (FK)  |
                                    | category         | (decision, task, risk, blocker, dep, question, milestone)
                                    | title            |
                                    | description      |
                                    | owner            |
                                    | date_reference   |
                                    | confidence       |
                                    | verification_stat| (VERIFIED, UNCERTAIN, CONFLICT)
                                    | conflict_details |
                                    +------------------+
                                              |
                                              | 1:N
                                              v
                                    +------------------+        1:N        +-------------------+
                                    |    Handover      |-------------------|   Handover Item   |
                                    |------------------|                   |-------------------|
                                    | id (PK)          |                   | id (PK)           |
                                    | project_id (FK)  |                   | handover_id (FK)  |
                                    | version          |                   | section           |
                                    | status           |                   | claim_id (FK)     |
                                    | approved_by (FK) |                   | content           |
                                    | approved_at      |                   | is_accepted       |
                                    | executive_summary|                   | is_redacted       |
                                    | next_actions     |                   | reviewer_notes    |
                                    +------------------+                   +-------------------+
```

---

## 4. Five-Step Core Workflow

1. **Step 1 - Connect (Ingestion & Chunking):**
   - User uploads authorized project documents (PDF, DOCX, TXT).
   - Extractor preserves page numbers, sections, character offsets, and produces deterministic text passages.

2. **Step 2 - Reconstruct (Knowledge Extraction):**
   - AI Engine parses passages into structured claims across 10 categories.
   - Extracts explicit owners, dates, dependencies, and unresolved questions.

3. **Step 3 - Verify (Evidence Mapping & Conflict Detection):**
   - Every claim is anchored to one or more supporting passages.
   - If conflicting claims exist (e.g. conflicting deadlines or differing owners across meeting notes vs requirements), system flags them as `CONFLICT` and exposes both passages.
   - Ambiguous or partial facts are flagged as `UNCERTAIN`.

4. **Step 4 - Review (Human-in-the-Loop Studio):**
   - Project Lead reviews all 14 handover sections.
   - Can edit text, accept/reject claims, resolve conflicts, redact private notes, or manually add missing details.
   - Generates a finalized, signed version.

5. **Step 5 - Handover (Role-Based Onboarding):**
   - Incoming members log in and see the clean, approved continuation plan.
   - Unapproved drafts and unredacted raw source documents remain inaccessible.

---

## 5. Security & Trust Principles

- **Zero Hallucination Tolerance:** Claims must be grounded in source text.
- **Backend-Enforced Authorization:** Incoming members receiving 403 Forbidden on lead endpoints.
- **Auditable History:** Every document mutation, analysis run, item edit, and approval is logged in `AuditLog`.
