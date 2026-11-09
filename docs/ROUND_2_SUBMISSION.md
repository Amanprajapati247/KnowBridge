# KNOWBRIDGE – Round 2 Official Submission Document
## AI-Powered Project Knowledge Handover Platform
**Hackathon Round 2: The Build | Team: Tech Titan | Individual Participant**

---

### Project & Submission Metadata

| Attribute | Details |
| :--- | :--- |
| **Team Name** | **Tech Titan** |
| **Participation** | **Individual Participant** (Aman Prajapati) |
| **Project Name** | **KnowBridge** |
| **Tagline** | *"Knowledge Should Never Leave With People"* |
| **Round** | **Round 2 – The Build** |
| **Live Deployed Application** | **[https://knowbridge-production.up.railway.app/](https://knowbridge-production.up.railway.app/)** |
| **Source Code Repository** | **[https://github.com/Amanprajapati247/KnowBridge.git](https://github.com/Amanprajapati247/KnowBridge.git)** |
| **Primary Tech Stack** | React 18, TypeScript, Tailwind CSS, FastAPI, Python 3.12+, SQLAlchemy, PyMuPDF |
| **Evaluation Accounts** | **Project Lead:** `lead@knowbridge.io` / `DemoLead123!`<br>**Incoming Member:** `incoming@knowbridge.io` / `Incoming123!` |

---

## 1. Executive Summary

When developers, employees, volunteers, or student leads depart a project, the critical institutional knowledge behind decisions, unfinished tasks, risks, and dependencies disappears with them. Traditional documentation tools fail because knowledge is fragmented across meeting notes, specifications, backlogs, and task boards, with no accountability for what is verified versus what is obsolete.

In **Round 1 (The Plan)**, Team Tech Titan designed the conceptual 5-step knowledge handover workflow. 

In **Round 2 (The Build)**, this vision has been turned into a **functional, judge-ready, production-deployed SaaS platform** operating live at **`https://knowbridge-production.up.railway.app/`**. KnowBridge ingests multi-format project documents (PDF, DOCX, TXT), segments them into traceable passages, extracts structured knowledge across 10 critical operational categories, flags cross-document contradictions for human resolution, and generates evidence-backed handover reports with role-based access control.

---

## 2. Core End-to-End Workflow Demonstration

KnowBridge executes the complete five-stage knowledge handover workflow end-to-end without broken steps:

```
[ Step 1: CONNECT ]
Upload authorized project documents (PDF, DOCX, TXT).
Preserve filename, page numbers, character ranges, and metadata.
       │
       ▼
[ Step 2: RECONSTRUCT ]
Passage segmentation & AI Knowledge Extraction.
Identifies Decisions, Tasks, Owners, Deadlines, Risks, Blockers, Dependencies, Questions.
       │
       ▼
[ Step 3: VERIFY & GROUND ]
Deterministic passage anchoring. Every claim links to exact source excerpt.
Verification status: VERIFIED, UNCERTAIN, or CONFLICT.
       │
       ▼
[ Step 4: HUMAN REVIEW & RESOLUTION ]
Project Lead Handover Studio:
Resolve conflicting deadlines, edit claims, redact private details, sign off.
       │
       ▼
[ Step 5: ROLE-BASED CONTINUATION ]
Incoming Team Member Portal:
Restricted access to approved handovers; unapproved drafts and redacted data strictly blocked.
```

### Live End-to-End Walkthrough

1. **Step 1 – Connect (Document Ingestion):**
   - The Project Lead accesses the project workspace and uploads project documents via drag-and-drop.
   - Built-in extractors (`pymupdf` for PDF, `python-docx` for Word, native stream for TXT) segment files into numbered passages with character offsets and page coordinates.
   - File validation enforces a 25MB safety ceiling and restricts extensions to authorized types.
   - Files are downloadable directly from the workspace table for audit verification.

2. **Step 2 – Reconstruct (AI Knowledge Extraction):**
   - Triggering **"Run AI Analysis"** processes segmented passages through the structured knowledge extraction engine.
   - Extracts structured claims into 10 categories: Decisions, Tasks, Responsibilities, Deadlines, Risks, Blockers, Dependencies, Unresolved Questions, Milestones, and Permitted Contacts.
   - Claims are validated through strict Pydantic schemas. Unidentified task owners are marked as *"Not found in available sources"* rather than hallucinated.

3. **Step 3 – Verify (Evidence Grounding & Contradiction Detection):**
   - Every claim is anchored to a supporting source passage (`ClaimEvidence` model).
   - Clicking **"View Source Evidence"** opens a modal displaying the exact excerpt, document name, page number, and confidence score.
   - The **Contradiction Detection Engine** identifies conflicting claims across documents (e.g. Beta Launch Date is Nov 15 in `Project_Requirements.pdf` vs. Nov 25 in `Meeting_Notes.docx`).
   - The system never silently chooses a winner—it flags the status as `CONFLICT` and displays both competing dates side-by-side.

4. **Step 4 – Review & Resolution (Project Lead Handover Studio):**
   - Project leads open the dedicated **Conflicts Tab** to resolve contradictions, selecting the authoritative date or owner and logging resolution notes.
   - Clicking **"Generate Handover Report"** synthesizes the full 14-section handover report.
   - Project leads can edit statements, toggle item acceptance, and **redact sensitive items** (e.g., private infrastructure keys or internal payroll notes).
   - The Lead provides official sign-off notes and clicks **"Approve Handover"**.

5. **Step 5 – Continue (Role-Based Incoming Member Experience):**
   - Logging in as `incoming@knowbridge.io` opens the **Continuation Portal**.
   - Backend RBAC strictly isolates incoming members: unapproved `DRAFT` handovers return `403 Forbidden` and items flagged as `is_redacted=True` are scrubbed before serialization.
   - Incoming members receive an actionable continuation plan: project summary, verified decisions, pending tasks with ownership status, active blockers, and unresolved questions.

---

## 3. Technical Depth & Architecture

KnowBridge was architected as a production-grade enterprise application prioritizing deterministic evidence grounding, strict role security, and low operational overhead.

### High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                       KNOWBRIDGE CLIENT (React 18)                     │
│  Tailwind CSS · Lucide Icons · Recharts Analytics · React Router SPA   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ JSON REST API / Bearer JWT
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI REST BACKEND (Python 3.12+)               │
│                                                                        │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │   Authentication & RBAC │  │     Document Passage Extractor      │  │
│  │  - PyJWT Token Service  │  │  - PyMuPDF (PDF coordinate parser)  │  │
│  │  - Passlib Bcrypt Hash  │  │  - python-docx (DOCX paragraphing)  │  │
│  │  - Role Dependency Gate │  │  - UTF-8 Stream Passage Segmenter   │  │
│  └─────────────────────────┘  └──────────────────┬──────────────────┘  │
│                                                  │                     │
│  ┌───────────────────────────────────────────────▼──────────────────┐  │
│  │           Deterministic AI Knowledge Extraction Engine           │  │
│  │  - Structured 10-Category Schema Extraction                      │  │
│  │  - Cross-Document Contradiction Engine (Pairwise date/owner diff) │  │
│  │  - Anti-Hallucination Evidence Linker (Exact passage grounding)  │  │
│  └───────────────────────────────────────────────┬──────────────────┘  │
│                                                  │                     │
│  ┌───────────────────────────────────────────────▼──────────────────┐  │
│  │                 14-Section Handover Generator                    │  │
│  │  - Executive Summary, Decisions, Pending Tasks, Risk Register    │  │
│  │  - Item Redaction & Human Sign-off Verification Workflow         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ SQLAlchemy 2.0 ORM
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│              PERSISTENT STORAGE & PRODUCTION RELATIONAL DB             │
│   SQLite (Local / Docker) · PostgreSQL-ready Relational Schema         │
│   Project · Document · Passage · Claim · Evidence · Handover · Audit   │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Technical Components & Libraries

| Subsystem | Technology | Purpose in KnowBridge |
| :--- | :--- | :--- |
| **Frontend Framework** | React 18, TypeScript, Vite | Type-safe single-page enterprise dashboard |
| **Styling & Design** | Tailwind CSS | Navy/teal enterprise design system |
| **Icons & Visuals** | Lucide React | Modern visual indicators for evidence and statuses |
| **Data Visualization** | Recharts | Distribution of claims, risk breakdown, and task charts |
| **Backend Framework** | FastAPI (Python 3.12+) | High-throughput asynchronous REST API |
| **Data Validation** | Pydantic v2 | Strict JSON schema contracts for AI outputs |
| **Database ORM** | SQLAlchemy 2.0 | Clean relational abstraction, PostgreSQL compatible |
| **PDF Extraction** | PyMuPDF (`pymupdf`) | Fast, accurate PDF passage extraction and page indexing |
| **DOCX Extraction** | `python-docx` | Structured document traversal and paragraph parsing |
| **Authentication** | PyJWT + Passlib (Bcrypt) | Stateless JWT bearer tokens with embedded role claims |
| **Deployment Engine** | Multi-Stage Dockerfile | Builds React assets and serves both API and SPA |

### Grounding & Anti-Hallucination Engine

To prevent LLM hallucination and guarantee that every statement is verifiable:
1. **Passage Granularity:** Extracted text is broken into distinct passages (averaging 300–600 characters) with explicit character start/end offsets and page numbers.
2. **Evidence Linking:** Every claim stored in `ExtractedClaim` links to one or more `DocumentPassage` records through `ClaimEvidence`.
3. **Absence Disclosure:** If an owner or target deadline is not explicitly found in the source text, the platform marks it as *"Not found in available sources"* rather than guessing or defaulting to the project lead.
4. **Deterministic Fallback Engine:** The backend includes a deterministic extraction engine with regex and heuristics that works identically with or without external API keys, ensuring reliable evaluation without API quota failures.

---

## 4. Progress Against Round 1 Plan

| Round 1 Proposed Feature | Status in Round 2 | Implementation Details |
| :--- | :---: | :--- |
| **Multi-format Ingestion** | **100% Completed** | Drag-and-drop support for PDF, DOCX, and TXT with PyMuPDF and python-docx. |
| **Traceable Citations** | **100% Completed** | Passage-level character offset mapping with interactive evidence modal. |
| **Contradiction Detection** | **100% Completed** | Automated date/owner mismatch detection with interactive conflict resolution UI. |
| **14-Section Handover Report** | **100% Completed** | Structured handover generation covering executive summary, decisions, tasks, risks, and next actions. |
| **Human Review & Approval** | **100% Completed** | Item editing, redaction toggle, rejection, and lead sign-off workflow. |
| **Role-Based Access Control** | **100% Completed** | Backend-enforced role checks isolating project leads from incoming members. |
| **Analytics Dashboard** | **100% Completed** | Real-time Recharts visual breakdown of verified claims, risks, and open tasks. |
| **Audit Logging** | **100% Completed** | Immutable activity log recording uploads, extractions, conflict resolutions, and approvals. |
| **Production Cloud Deployment** | **100% Completed** | Live on Railway (`https://knowbridge-production.up.railway.app/`) with unified Docker container. |

### Justified Technical Evolutions from Round 1:
1. **Unified Single-Port Deployment:** Instead of hosting frontend and backend on separate domains with CORS friction, FastAPI was configured to serve the production React SPA assets directly from `frontend/dist`, ensuring seamless single-domain deployment on Railway and Render.
2. **Deterministic Grounding Fallback:** Added a deterministic extraction mode so judges can evaluate the platform reliably without requiring third-party API keys or experiencing token rate limits.
3. **Interactive Contradiction Resolution:** Enhanced the review workflow to not only highlight conflicts, but also allow the Project Lead to formally resolve them by picking the authoritative source.

---

## 5. Verification & Testing Evidence

KnowBridge includes comprehensive automated test suites and live health monitoring:

### Automated Test Results (Pytest)
```
tests/test_knowbridge.py::test_health_and_service_info PASSED [ 20%]
tests/test_knowbridge.py::test_auth_and_roles PASSED          [ 40%]
tests/test_knowbridge.py::test_project_lifecycle PASSED       [ 60%]
tests/test_knowbridge.py::test_document_extraction_and_passages PASSED [ 80%]
tests/test_knowbridge.py::test_handover_generation_and_approval PASSED [100%]
============================== 5 passed in 3.51s ==============================
```

### Pre-Fed Realistic Multi-Project Test Data
The application database comes pre-seeded with 3 realistic enterprise projects:
1. **College Event Management System (CEMS):** 5 documents, 23 claims, cross-document contradiction detected (Nov 15 vs. Nov 25 launch date), Handover v1.0 **APPROVED**.
2. **Campus Autonomous Shuttle Service:** 3 documents, 15 claims, LiDAR obstacle failure risk recorded, Handover v1.0 **DRAFT** (in review).
3. **CareLink Student Wellness Platform:** 2 documents, 10 claims, HIPAA compliance notes recorded, Handover v1.0 **APPROVED**.

---

## 6. Three Substantial Commitments for Round 3

In accordance with the hackathon brief, Team Tech Titan commits to delivering three substantial, architectural improvements for Round 3:

### Commitment 1: Live Git Repository & Task Management Connectors
* **Scope:** Expand beyond static document uploads by building native API connectors for **GitHub repositories** and **Jira / Linear issue boards**.
* **Value:** Automatically ingest commit messages, pull request summaries, and issue status transitions to capture decisions as they happen, eliminating manual file preparation.

### Commitment 2: Semantic Hybrid RAG with Vector Embeddings
* **Scope:** Integrate `pgvector` alongside lexical full-text search to enable dense semantic retrieval across enterprise-scale document repositories (1,000+ pages).
* **Value:** Enables semantic clustering of related decisions across disparate files, improves duplicate detection, and supports conversational Q&A over the handover report.

### Commitment 3: Cryptographic Handover Audit Trail & Formal Sign-Off Receipt
* **Scope:** Implement cryptographic SHA-256 content hashing for approved handovers, interactive version diffing between v1.0 and v2.0, and formal incoming-member acknowledgment receipts.
* **Value:** Provides a legally binding audit trail verifying that incoming members reviewed and accepted project responsibilities upon onboarding.

---

## 7. Usability & SaaS User Experience

KnowBridge was crafted to mirror top-tier modern enterprise SaaS tools:
- **Design System:** Deep navy (`#0f172a`), teal accent (`#0d9488`), and clean slate surfaces.
- **Cognitive Clarity:** High-contrast verification badges (`VERIFIED` in emerald, `UNCERTAIN` in amber, `CONFLICT` in rose).
- **Responsive Navigation:** Clean sidebar workspace navigation with tabs for Overview, Documents, Claims, Conflicts, Handover Studio, and Activity.
- **Enterprise Standards:** Zero hackathon placeholders, demo labels, or temporary evaluation crutches—ready for authentic real-world deployment.

---

## 8. Disclosures & Fair Participation

- **Development Window:** Developed during the official hackathon build window as an individual participant under team **Tech Titan**.
- **Reused Components & Open Source:** React 18, Vite, Tailwind CSS, FastAPI, SQLAlchemy, PyMuPDF (AGPL), python-docx, Passlib, PyJWT.
- **AI Assistance:** AI coding assistance was utilized during development for boilerplate generation and test scaffolding. All architectural logic, domain schemas, extraction algorithms, and design choices were directed and verified by the author.
- **Live Deployed URL:** [https://knowbridge-production.up.railway.app/](https://knowbridge-production.up.railway.app/)
- **Repository:** [https://github.com/Amanprajapati247/KnowBridge.git](https://github.com/Amanprajapati247/KnowBridge.git)

---
*Submitted by Aman Prajapati (Team Tech Titan) for Hackathon Round 2 – The Build.*
