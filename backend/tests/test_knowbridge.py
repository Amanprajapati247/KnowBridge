import pytest
import os
import pymupdf
from docx import Document as DocxDocument
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models import User, Project, Document, Handover, AuditLog
from app.services.extractor import extract_document, DocumentExtractionError

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "knowbridge-backend"

def test_auth_and_roles():
    import uuid
    uid = uuid.uuid4().hex[:6]
    lead_email = f"lead_{uid}@knowbridge.org"
    inc_email = f"inc_{uid}@knowbridge.org"

    # 1. Register Lead
    res = client.post("/api/auth/register", json={
        "email": lead_email,
        "password": "Password123!",
        "full_name": "Fresh Lead",
        "role": "PROJECT_LEAD"
    })
    assert res.status_code == 201
    lead_token = res.json()["access_token"]
    assert res.json()["role"] == "PROJECT_LEAD"

    # 2. Register Incoming
    res_inc = client.post("/api/auth/register", json={
        "email": inc_email,
        "password": "Password123!",
        "full_name": "Fresh Incoming",
        "role": "INCOMING_MEMBER"
    })
    assert res_inc.status_code == 201
    inc_token = res_inc.json()["access_token"]
    assert res_inc.json()["role"] == "INCOMING_MEMBER"

    # 3. Test Me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {lead_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == lead_email

def test_document_extraction_and_failure_cases(tmp_path):
    # 1. Valid TXT
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Meeting decisions:\nDecided to use PostgreSQL.\n\nTask: Setup server by Friday.", encoding="utf-8")
    passages = extract_document(str(txt_file), "sample.txt")
    assert len(passages) >= 2
    assert "PostgreSQL" in passages[0]["content"]

    # 2. Empty file failure
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(DocumentExtractionError):
        extract_document(str(empty_file), "empty.txt")

    # 3. Unsupported extension failure
    unsupported = tmp_path / "image.png"
    unsupported.write_text("dummy", encoding="utf-8")
    with pytest.raises(DocumentExtractionError):
        extract_document(str(unsupported), "image.png")

    # 4. Corrupted PDF failure
    corrupt_pdf = tmp_path / "bad.pdf"
    corrupt_pdf.write_bytes(b"%PDF-invalid-bytes-garbage-header-and-body")
    with pytest.raises(DocumentExtractionError):
        extract_document(str(corrupt_pdf), "bad.pdf")

def test_incoming_member_role_restrictions():
    # Login as incoming member
    login_res = client.post("/api/auth/login", json={
        "email": "incoming@knowbridge.demo",
        "password": "Incoming123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create project (Must be forbidden)
    create_proj = client.post("/api/projects", headers=headers, json={"title": "Unauthorized Project"})
    assert create_proj.status_code == 403

    # Attempt to upload document (Must be forbidden)
    upload_doc = client.post("/api/projects/1/documents", headers=headers)
    assert upload_doc.status_code == 403

    # Attempt to trigger AI analysis (Must be forbidden)
    analyze = client.post("/api/projects/1/analyze", headers=headers)
    assert analyze.status_code == 403

def test_end_to_end_demo_workflow():
    # 1. Login as Project Lead
    login_res = client.post("/api/auth/login", json={
        "email": "lead@knowbridge.demo",
        "password": "DemoLead123!"
    })
    assert login_res.status_code == 200
    lead_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {lead_token}"}

    # 2. Seed Demo Project
    seed_res = client.post("/api/projects/seed-demo", headers=headers)
    assert seed_res.status_code == 200
    proj_data = seed_res.json()
    proj_id = proj_data["id"]
    assert proj_data["document_count"] == 5
    assert proj_data["claim_count"] > 0

    # 3. Fetch Claims and Verify Evidence & Conflicts
    claims_res = client.get(f"/api/projects/{proj_id}/claims", headers=headers)
    assert claims_res.status_code == 200
    claims = claims_res.json()
    assert len(claims) > 0

    # Verify at least one conflict is detected between documents
    conflicts = [c for c in claims if c["verification_status"] == "CONFLICT"]
    assert len(conflicts) > 0, "Intentional Beta Launch deadline conflict should be flagged!"
    assert "CONTRADICTION DETECTED" in conflicts[0]["conflict_details"]

    # 4. Resolve the Conflict
    conf_id = conflicts[0]["id"]
    resolve_res = client.put(f"/api/claims/{conf_id}/resolve", headers=headers, json={
        "resolution_notes": "Authoritatively confirmed Beta Launch date is November 25, 2026 as agreed in Sprint Review.",
        "chosen_date": "November 25, 2026"
    })
    assert resolve_res.status_code == 200
    assert resolve_res.json()["verification_status"] == "VERIFIED"
    assert resolve_res.json()["is_resolved"] is True

    # 5. Generate Handover Report
    gen_res = client.post(f"/api/projects/{proj_id}/handovers/generate", headers=headers)
    assert gen_res.status_code == 201
    handover = gen_res.json()
    handover_id = handover["id"]
    assert handover["status"] == "DRAFT"
    assert len(handover["items"]) > 0

    # 6. Incoming Member Cannot Access DRAFT Handover
    inc_login = client.post("/api/auth/login", json={
        "email": "incoming@knowbridge.demo",
        "password": "Incoming123!"
    })
    assert inc_login.status_code == 200
    inc_token = inc_login.json()["access_token"]
    inc_headers = {"Authorization": f"Bearer {inc_token}"}

    unapproved_view = client.get(f"/api/incoming/handovers/{handover_id}", headers=inc_headers)
    assert unapproved_view.status_code == 403, "Incoming member must not access unapproved handover!"

    # 7. Lead Redacts a Sensitive Item and Approves Handover
    item_to_redact = handover["items"][0]
    redact_res = client.put(f"/api/handovers/{handover_id}/items/{item_to_redact['id']}", headers=headers, json={
        "is_redacted": True,
        "reviewer_notes": "Redacted private vendor negotiation details."
    })
    assert redact_res.status_code == 200
    assert redact_res.json()["is_redacted"] is True

    approve_res = client.post(f"/api/handovers/{handover_id}/approve", headers=headers, json={
        "approval_notes": "Handover verified and signed off for incoming team members."
    })
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 8. Incoming Member CAN Now Access Approved Handover (and Redacted Item is Scrubbed)
    approved_view = client.get(f"/api/incoming/handovers/{handover_id}", headers=inc_headers)
    assert approved_view.status_code == 200
    incoming_handover = approved_view.json()
    assert incoming_handover["status"] == "APPROVED"
    item_ids_received = [it["id"] for it in incoming_handover["items"]]
    assert item_to_redact["id"] not in item_ids_received, "Redacted item must be completely filtered out for incoming member!"

    # 9. Verify Activity Trail Log
    act_res = client.get(f"/api/projects/{proj_id}/activity", headers=headers)
    assert act_res.status_code == 200
    logs = act_res.json()
    actions = [l["action"] for l in logs]
    assert "HANDOVER_APPROVED" in actions
    assert "CONFLICT_RESOLVED" in actions
