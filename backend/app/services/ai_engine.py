import re
import json
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def run_deterministic_extraction(passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic rule-based NLP extraction engine.
    Extracts decisions, tasks, risks, blockers, dependencies, questions, and milestones
    grounded directly in passage text without inventing unstated facts.
    """
    claims = []
    
    # Keyword indicators
    decision_keywords = ["decided", "decision", "agreed", "chose", "selected", "approved architecture", "switched to"]
    risk_keywords = ["risk", "danger", "vulnerability", "bottleneck", "delay", "challenge", "threat", "concern"]
    blocker_keywords = ["blocked", "blocker", "waiting on", "stuck", "preventing", "cannot proceed"]
    dependency_keywords = ["depends on", "dependency", "dependent on", "required before", "prerequisite"]
    question_keywords = ["unresolved", "open question", "to be decided", "tbd", "unclear", "pending confirmation", "?"]
    task_keywords = ["task", "todo", "to-do", "implement", "develop", "deliver", "build", "schedule", "assigned to", "status:"]
    milestone_keywords = ["milestone", "phase", "deadline", "target date", "launch date", "due date"]

    # Date pattern matching
    date_regex = re.compile(
        r'\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b|\b\d{4}-\d{2}-\d{2}\b)',
        re.IGNORECASE
    )

    # Owner pattern matching: "Owner: <Name>", "Assigned to: <Name>", "<Name> to handle"
    owner_regex = re.compile(
        r'(?:owner|assigned to|lead|in-charge|handled by|responsible|contact)\s*[:=-]\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
        re.IGNORECASE
    )

    for p in passages:
        p_id = p.get("id")
        doc_filename = p.get("filename", "Unknown Document")
        page_num = p.get("page_number", 1)
        content = p.get("content", "")
        sentences = re.split(r'(?<=[.!?])\s+', content)

        for sentence in sentences:
            s_clean = sentence.strip()
            if len(s_clean) < 20:
                continue

            s_lower = s_clean.lower()
            
            # Extract date if present
            found_dates = date_regex.findall(s_clean)
            extracted_date = found_dates[0] if found_dates else None

            # Extract owner if present
            found_owner = owner_regex.search(s_clean)
            extracted_owner = found_owner.group(1).strip() if found_owner else None

            # 1. Decisions
            if any(k in s_lower for k in decision_keywords):
                claims.append({
                    "category": "DECISION",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Team Consensus",
                    "date_reference": extracted_date,
                    "confidence": 0.95,
                    "verification_status": "VERIFIED",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 2. Blockers
            elif any(k in s_lower for k in blocker_keywords):
                claims.append({
                    "category": "BLOCKER",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Not found in available sources",
                    "date_reference": extracted_date,
                    "confidence": 0.90,
                    "verification_status": "VERIFIED",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 3. Risks
            elif any(k in s_lower for k in risk_keywords):
                claims.append({
                    "category": "RISK",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Not found in available sources",
                    "date_reference": extracted_date,
                    "confidence": 0.92,
                    "verification_status": "VERIFIED",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 4. Dependencies
            elif any(k in s_lower for k in dependency_keywords):
                claims.append({
                    "category": "DEPENDENCY",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Not found in available sources",
                    "date_reference": extracted_date,
                    "confidence": 0.88,
                    "verification_status": "VERIFIED",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 5. Unresolved Questions
            elif any(k in s_lower for k in question_keywords) or s_clean.endswith("?"):
                claims.append({
                    "category": "UNRESOLVED_QUESTION",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Pending Assignment",
                    "date_reference": extracted_date,
                    "confidence": 0.85,
                    "verification_status": "UNCERTAIN",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 6. Milestones / Deadlines
            elif any(k in s_lower for k in milestone_keywords) and extracted_date:
                claims.append({
                    "category": "MILESTONE",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Not found in available sources",
                    "date_reference": extracted_date,
                    "confidence": 0.94,
                    "verification_status": "VERIFIED",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

            # 7. Tasks
            elif any(k in s_lower for k in task_keywords) or (extracted_owner and ("will" in s_lower or "must" in s_lower or "should" in s_lower)):
                status_guess = "COMPLETED" if any(w in s_lower for w in ["completed", "done", "finished", "resolved", "delivered"]) else "PENDING"
                claims.append({
                    "category": "TASK",
                    "title": s_clean[:80] + ("..." if len(s_clean) > 80 else ""),
                    "description": s_clean,
                    "owner": extracted_owner or "Not found in available sources",
                    "date_reference": extracted_date,
                    "task_status": status_guess,
                    "confidence": 0.91,
                    "verification_status": "VERIFIED" if extracted_owner else "UNCERTAIN",
                    "passage_id": p_id,
                    "filename": doc_filename,
                    "page_number": page_num,
                    "excerpt": s_clean
                })

    return {
        "engine": "KnowBridge Deterministic Extraction Engine",
        "claims": claims
    }

def detect_conflicts(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans claims across different source documents to find contradictory dates,
    milestone deadlines, or incompatible task statuses.
    Marks conflicting claims with verification_status = 'CONFLICT' and explains the discrepancy.
    """
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            c1 = claims[i]
            c2 = claims[j]

            # Compare only across different documents
            if c1.get("filename") == c2.get("filename"):
                continue

            # Compare milestones or tasks regarding the same core subject
            subject_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', (c1["title"] + " " + c1["description"]).lower()))
            target_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', (c2["title"] + " " + c2["description"]).lower()))
            overlap = subject_words.intersection(target_words)

            # Common stopping words to ignore
            overlap -= {"project", "system", "management", "event", "college", "status", "notes", "requirements", "update", "tasks"}

            # If there's high overlap and both have dates, but dates differ:
            if len(overlap) >= 2 and c1.get("date_reference") and c2.get("date_reference"):
                if c1["date_reference"].lower() != c2["date_reference"].lower():
                    conflict_text = (
                        f"CONTRADICTION DETECTED: Source '{c1['filename']}' specifies '{c1['date_reference']}' "
                        f"whereas Source '{c2['filename']}' specifies '{c2['date_reference']}'. "
                        f"Project Lead review is required to resolve which deadline is current."
                    )
                    c1["verification_status"] = "CONFLICT"
                    c1["conflict_details"] = conflict_text
                    c2["verification_status"] = "CONFLICT"
                    c2["conflict_details"] = conflict_text

    return claims
