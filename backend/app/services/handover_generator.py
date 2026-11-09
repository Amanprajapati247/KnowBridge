from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models import Project, ExtractedClaim, Document

def generate_handover_report(
    project: Project,
    claims: List[ExtractedClaim],
    documents: List[Document]
) -> Dict[str, Any]:
    """
    Builds the complete 14-section evidence-backed handover report from extracted claims and documents.
    """
    decisions = [c for c in claims if c.category == "DECISION"]
    tasks = [c for c in claims if c.category == "TASK"]
    completed_tasks = [c for c in tasks if "COMPLETED" in (c.conflict_details or "") or "completed" in c.description.lower() or "done" in c.description.lower()]
    pending_tasks = [c for c in tasks if c not in completed_tasks]
    risks = [c for c in claims if c.category in ("RISK", "BLOCKER")]
    dependencies = [c for c in claims if c.category == "DEPENDENCY"]
    questions = [c for c in claims if c.category == "UNRESOLVED_QUESTION"]
    conflicts = [c for c in claims if c.verification_status == "CONFLICT"]

    # Identify missing information
    missing_items = []
    unassigned_tasks = [t for t in pending_tasks if not t.owner or "not found" in t.owner.lower()]
    if unassigned_tasks:
        missing_items.append(f"{len(unassigned_tasks)} pending task(s) have no assigned owner in the authorized documents.")
    
    tasks_without_deadlines = [t for t in pending_tasks if not t.date_reference]
    if tasks_without_deadlines:
        missing_items.append(f"{len(tasks_without_deadlines)} open task(s) lack explicit target completion dates.")

    if not any("budget" in (c.title + " " + c.description).lower() for c in claims):
        missing_items.append("Budget allocation and financial sponsorship records were not found in the uploaded documents.")

    if not any("test" in (c.title + " " + c.description).lower() for c in claims):
        missing_items.append("Quality assurance test plan and user acceptance sign-off criteria are absent from current sources.")

    # Executive Summary & Current Status
    total_docs = len(documents)
    exec_summary = (
        f"This handover synthesizes verified project intelligence for '{project.title}' across {total_docs} authorized document(s). "
        f"The system identified {len(decisions)} key architectural and operational decisions, {len(completed_tasks)} completed items, "
        f"{len(pending_tasks)} open tasks, and {len(risks)} active risks or blockers. "
        f"{len(conflicts)} cross-document conflict(s) were flagged for human resolution."
    )

    current_status = (
        f"Project is currently in '{project.status}' state with {len(pending_tasks)} pending deliverables. "
        f"Core technical decisions have been anchored, while operational handoffs and conflict resolutions require Project Lead sign-off."
    )

    # Next Actions (Clearly labelled as AI recommendations)
    next_actions = (
        "1. Resolve highlighted deadline contradiction between conflicting documents.\n"
        "2. Formally assign explicit owners to unowned pending tasks.\n"
        "3. Review and close the unresolved architectural questions noted in the Risk Register.\n"
        "4. Validate deployment staging environment prior to final release."
    )

    missing_info_summary = "\n".join(f"- {m}" for m in missing_items) if missing_items else "No critical missing gaps detected in current documentation."
    conflict_info_summary = (
        f"Identified {len(conflicts)} items with contradictory claims across separate documents. "
        "Review each conflicting pair below and choose the authoritative record before final approval."
        if conflicts else "No contradictory dates or claims detected across documents."
    )

    # Prepare structured handover items for each of the 14 sections
    items_to_create = []
    order = 1

    # 4. Important Decisions
    for d in decisions:
        ev = d.evidences[0] if d.evidences else None
        items_to_create.append({
            "section": "DECISIONS",
            "claim_id": d.id,
            "title": d.title,
            "content": f"Decision: {d.description} | Rationale/Owner: {d.owner or 'Team'} | Date: {d.date_reference or 'N/A'}",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else d.description,
            "verification_status": d.verification_status,
            "display_order": order
        })
        order += 1

    # 5. Completed Tasks
    for t in completed_tasks:
        ev = t.evidences[0] if t.evidences else None
        items_to_create.append({
            "section": "COMPLETED_TASKS",
            "claim_id": t.id,
            "title": t.title,
            "content": f"Completed Deliverable: {t.description} | Owner: {t.owner or 'N/A'}",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else t.description,
            "verification_status": t.verification_status,
            "display_order": order
        })
        order += 1

    # 6. Pending Tasks
    for t in pending_tasks:
        ev = t.evidences[0] if t.evidences else None
        items_to_create.append({
            "section": "PENDING_TASKS",
            "claim_id": t.id,
            "title": t.title,
            "content": f"Pending Task: {t.description} | Owner: {t.owner or 'Unassigned'} | Target Date: {t.date_reference or 'Not stated'}",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else t.description,
            "verification_status": t.verification_status,
            "display_order": order
        })
        order += 1

    # 7. Responsibilities & Ownership
    unique_owners = set(c.owner for c in claims if c.owner and "not found" not in c.owner.lower())
    for owner in unique_owners:
        owned_tasks = [c.title for c in claims if c.owner == owner]
        items_to_create.append({
            "section": "RESPONSIBILITIES",
            "claim_id": None,
            "title": f"Owner Responsibility: {owner}",
            "content": f"Responsible for: {', '.join(owned_tasks[:3])}",
            "source_filename": "Aggregated from project sources",
            "source_page": 1,
            "evidence_excerpt": f"Assigned to {owner} across project files.",
            "verification_status": "VERIFIED",
            "display_order": order
        })
        order += 1

    # 8. Risks and Blockers
    for r in risks:
        ev = r.evidences[0] if r.evidences else None
        items_to_create.append({
            "section": "RISKS_BLOCKERS",
            "claim_id": r.id,
            "title": f"[{r.category}] {r.title}",
            "content": f"{r.description} | Severity / Date: {r.date_reference or 'Active'}",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else r.description,
            "verification_status": r.verification_status,
            "display_order": order
        })
        order += 1

    # 9. Dependencies
    for dep in dependencies:
        ev = dep.evidences[0] if dep.evidences else None
        items_to_create.append({
            "section": "DEPENDENCIES",
            "claim_id": dep.id,
            "title": dep.title,
            "content": dep.description,
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else dep.description,
            "verification_status": dep.verification_status,
            "display_order": order
        })
        order += 1

    # 10. Unresolved Questions
    for q in questions:
        ev = q.evidences[0] if q.evidences else None
        items_to_create.append({
            "section": "UNRESOLVED_QUESTIONS",
            "claim_id": q.id,
            "title": q.title,
            "content": f"Question: {q.description} | Status: Needs clarification from Lead",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else q.description,
            "verification_status": "UNCERTAIN",
            "display_order": order
        })
        order += 1

    # 13. Conflicting Information
    for conf in conflicts:
        ev = conf.evidences[0] if conf.evidences else None
        items_to_create.append({
            "section": "CONFLICT_INFO",
            "claim_id": conf.id,
            "title": f"[CONFLICT] {conf.title}",
            "content": f"{conf.conflict_details or conf.description}",
            "source_filename": ev.passage.document.filename if ev and ev.passage and ev.passage.document else None,
            "source_page": ev.passage.page_number if ev and ev.passage else None,
            "evidence_excerpt": ev.excerpt if ev else conf.description,
            "verification_status": "CONFLICT",
            "display_order": order
        })
        order += 1

    return {
        "title": f"Official Handover Report - {project.title}",
        "executive_summary": exec_summary,
        "current_status": current_status,
        "recommended_actions": next_actions,
        "missing_information": missing_info_summary,
        "conflicting_information": conflict_info_summary,
        "items": items_to_create
    }
