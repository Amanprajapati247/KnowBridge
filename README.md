# KnowBridge – Project Knowledge Handover Platform
> **"Knowledge Should Never Leave With People."**

---

## 1. Executive Summary

When employees, engineers, student contributors, or team members leave an organization, critical institutional and technical context disappears with them. While scattered documents, meeting notes, and pull requests may exist, the **reasoning behind decisions, pending deliverables, dependencies, unresolved questions, and explicit ownership** are fragmented.

**KnowBridge** is an enterprise knowledge-handover platform that ingests project documentation (PDF, DOCX, TXT), segments passages with page and section metadata, reconstructs project state using an evidence-grounded AI extraction engine, detects cross-document contradictions, provides a human-in-the-loop review studio, and enforces strict backend role-based access so incoming personnel receive a clean, authorized continuation plan.

---

## 2. Core Value Propositions

- **100% Traceable Grounding:** Every generated claim links back to its exact source file, page number, and text excerpt. No ungrounded hallucinations.
- **Cross-Document Discrepancy Detection:** When two documents disagree (e.g. conflicting milestone deadlines), KnowBridge flags both passages side-by-side rather than silently guessing.
- **Human-in-the-Loop Governance:** Project leads edit, redact, reject, or resolve claims, ensuring confidential or unverified notes never leak.
- **Backend-Enforced Role Separation:** Incoming members can only view approved handovers. Drafts, raw passages, and redacted statements are blocked at the API level (HTTP 403).
- **Pre-Configured Starter Template:** Built-in starter project ("College Event Management System") with multi-format documentation and realistic operational records.

---

## 3. Technology Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, Lucide React icons, Recharts.
- **Backend:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, REST APIs.
- **Database:** SQLite (local zero-config) designed with PostgreSQL-compatible schema.
- **Document Processing:** PyMuPDF (`pymupdf`) for PDFs, `python-docx` for Word documents, standard Python file processing for TXT.
- **AI Engine:** Dual-mode service abstraction:
  - Deterministic Expert NLP Extraction Engine (zero external billing required).
  - External LLM provider integration (Gemini / OpenAI API keys via environment variables).
- **Security:** JWT authentication, bcrypt password hashing, role-based authorization (`PROJECT_LEAD` vs `INCOMING_MEMBER`).

---

## 4. Quick Start & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node 20 / 22 / 26) & npm

---

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Backend will start on `http://127.0.0.1:8000`.
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`.

---

### Step 2: Frontend Setup

Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend will start on `http://localhost:5173`.

---

## 5. User Journey & Feature Walkthrough

### Pre-configured Accounts
| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Project Lead** | `lead@knowbridge.io` | `DemoLead123!` | Full workspace, file upload, AI analysis, conflict resolution, approval |
| **Incoming Member** | `incoming@knowbridge.io` | `Incoming123!` | Read-only view of approved handovers; drafts & raw files are blocked |

---

### Recommended Journey:

1. **Visit Landing Page (`http://localhost:5173`):** Explore the platform features, 5-step knowledge transfer workflow, and trust principles.
2. **Sign In:** Use the lead account or click "Lead Account" under Fast Evaluation Sign-In.
3. **Workspace Dashboard:** Observe KPI metrics, live Recharts distribution charts, and workspace tables.
4. **Starter Project:** Click **"Import Starter Project"** to populate a comprehensive reference workspace ("College Event Management System").
5. **Inspect Source Documents:** Under the **"Source Documents"** tab, inspect the 5 uploaded files:
   - `Project_Requirements.pdf`
   - `Meeting_Notes.docx`
   - `Development_Tasks.txt`
   - `Project_Decisions.pdf`
   - `Risk_Register.docx`
   Click the **Eye icon** to view segmented passages with exact page numbers.
6. **Inspect Reconstructed Claims:** Switch to **"AI Extracted Claims"** tab to review decisions, open tasks, assignees, and risks.
7. **Trace Grounding Evidence:** Click **"View Supporting Evidence"** on any claim to see the exact cited passage, source filename, page number, and confidence score.
8. **Reconcile Contradictions:** Switch to **"Conflicts & Discrepancies"** tab. Note that `Project_Requirements.pdf` specifies Beta Launch on November 15, while `Meeting_Notes.docx` specifies November 25.
9. **Resolve Conflict:** Click **"Resolve Contradiction"**. Select November 25 as authoritative, provide resolution notes ("Confirmed schedule adjustment from sprint review"), and save.
10. **Review Handover Studio:** Switch to **"Handover Review Studio"**. Review all 14 structured sections.
11. **Redact Sensitive Information:** Click the **Lock icon** on an item to mark it as **REDACTED**.
12. **Approve Handover:** Click **"Sign & Approve Handover"**.
13. **Switch to Incoming Member:** In the top navbar, click **"Switch"** (or log out and log in as `incoming@knowbridge.io`).
14. **Verify Security Boundary:**
    - Notice that only the approved handover is visible in the Incoming Portal.
    - Open the continuation plan: notice that the **REDACTED item is completely absent** from the report.
    - Attempting to query `/api/projects/1/documents` as an incoming member returns **HTTP 403 Forbidden**.

---

## 6. Running Automated Tests

A comprehensive pytest test suite tests authentication, role-based security, document extraction (PDF, DOCX, TXT), corrupted file rejection, conflict detection, redaction filtering, and the end-to-end workflow:

```bash
cd backend
.\.venv\Scripts\pytest tests/test_knowbridge.py -v
```

All tests execute against local SQLite test fixtures with 100% pass rate.

---

## 7. Repository Structure

```
knowbridge/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── core/            # Config, Security, Database
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── schemas/         # Pydantic v2 validation schemas
│   │   ├── services/        # Extractor, AI Engine, Conflict Detector, Starter Project Generator
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Pytest automated test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Footer, EvidenceModal, ConflictModal
│   │   ├── context/         # AuthContext
│   │   ├── pages/           # Landing, Login, Register, Dashboard, Workspace, Incoming
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docs/
│   ├── ARCHITECTURE.md      # Detailed system design
│   ├── API.md               # Complete REST API specification
│   ├── DATA_FLOW.md         # Mermaid data flow & sequence diagrams
│   └── ROUND3_COMMITMENTS.md# Roadmap milestones
└── README.md
```
