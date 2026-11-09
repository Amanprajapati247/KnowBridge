# KnowBridge REST API Specification
**Tech Titan | Individual Participant | Hackathon Round 2**

All API endpoints are prefixed with `/api` and return standard JSON responses.
Protected endpoints require an `Authorization: Bearer <token>` header.

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/register`
Creates a new user account with role selection.
- **Request Body:**
  ```json
  {
    "email": "user@college.edu",
    "password": "Password123!",
    "full_name": "Alex Chen",
    "role": "PROJECT_LEAD"  // or "INCOMING_MEMBER"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "role": "PROJECT_LEAD",
    "full_name": "Alex Chen",
    "email": "user@college.edu",
    "user_id": 1
  }
  ```

### `POST /api/auth/login`
Authenticates user credentials and issues a JWT token.
- **Request Body:**
  ```json
  {
    "email": "lead@knowbridge.demo",
    "password": "DemoLead123!"
  }
  ```
- **Response (200 OK):** JWT bearer token object.

### `GET /api/auth/me`
Returns current user profile. Requires Bearer Token.

---

## 2. Projects (`/api/projects`)

### `GET /api/projects`
Lists projects visible to current user. Project Leads see their owned projects; Incoming Members see projects with approved handovers.

### `POST /api/projects`
Creates a new workspace. (Restricted to `PROJECT_LEAD`).
- **Request Body:** `{"title": "...", "description": "..."}`

### `GET /api/projects/{id}`
Retrieves project details, document counts, claim counts, and handover status.

### `PUT /api/projects/{id}`
Updates project title, description, or lifecycle status (`ACTIVE`, `IN_REVIEW`, `COMPLETED`).

### `DELETE /api/projects/{id}`
Cascades deletion of project, attached files, extracted claims, and handovers.

### `POST /api/projects/seed-demo`
One-click seeder for judges: creates/resets the synthetic demonstration project `"College Event Management System [DEMO]"` with 5 sample files and extracts initial knowledge.

### `GET /api/projects/stats/dashboard`
Returns high-level KPI counts for projects, documents, handovers, open tasks, risks, and conflicts.

---

## 3. Documents (`/api/projects/{id}/documents` & `/api/documents/{id}`)

### `POST /api/projects/{id}/documents`
Multipart file upload supporting `.pdf`, `.docx`, `.txt`. Validates size, extracts text passages, records character offsets and page numbers. (Restricted to `PROJECT_LEAD`).

### `GET /api/projects/{id}/documents`
Lists documents with file size, upload timestamp, and passage count.

### `GET /api/documents/{id}/passages`
Returns segmented passages with page numbers and section headers.

### `DELETE /api/documents/{id}`
Deletes document record and physical file from disk.

---

## 4. AI Analysis & Evidence Grounding (`/api/projects/{id}/...`)

### `POST /api/projects/{id}/analyze`
Triggers the extraction pipeline across all project documents. Identifies decisions, tasks, assignees, dates, risks, blockers, dependencies, and questions. Executes cross-document conflict detection.

### `GET /api/projects/{id}/claims`
Retrieves all extracted claims with confidence scores, verification status (`VERIFIED`, `UNCERTAIN`, `CONFLICT`), and exact passage citations.

### `PUT /api/claims/{claim_id}/resolve`
Enables Project Lead to resolve a contradiction by recording authoritative resolution notes and choosing the confirmed date or owner.
- **Request Body:**
  ```json
  {
    "resolution_notes": "Confirmed with student council that Beta Launch is moved to November 25 due to exam week.",
    "chosen_date": "November 25, 2026"
  }
  ```

---

## 5. Handover Review & Approval (`/api/handovers` & `/api/projects/{id}/handovers`)

### `POST /api/projects/{id}/handovers/generate`
Generates a structured 14-section handover report in `DRAFT` status.

### `GET /api/handovers/{id}`
Fetches full handover report and all statement items. (Restricted to `PROJECT_LEAD`).

### `PUT /api/handovers/{id}/items/{item_id}`
Inline editing, redaction, or acceptance of individual handover statements:
- **Request Body:**
  ```json
  {
    "title": "Updated Title",
    "content": "Updated Content",
    "is_accepted": true,
    "is_redacted": true,
    "reviewer_notes": "Redacted internal vendor budget discussions"
  }
  ```

### `POST /api/handovers/{id}/approve`
Signs off and approves the handover. Updates status to `APPROVED`, publishing it to the Incoming Member portal.

---

## 6. Incoming Member Portal (`/api/incoming/...`)

### `GET /api/incoming/handovers`
Lists only `APPROVED` handovers. Unapproved drafts and archived handovers return nothing.

### `GET /api/incoming/handovers/{id}`
Returns the approved handover. Automatically scrubs redacted (`is_redacted: true`) and rejected items. Returns `403 Forbidden` if the requested handover is still in `DRAFT` status!

---

## 7. Activity & Audit Trail (`/api/projects/{id}/activity`)
Returns chronological event log for compliance tracking (project creations, file uploads, analyses, conflict resolutions, item redactions, and approvals).
