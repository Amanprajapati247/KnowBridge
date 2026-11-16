from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import User
from app.schemas import RAGQueryRequest, RAGQueryResponse
from app.api.deps import get_current_user, record_audit
from app.services.rag import HybridRAGService

router = APIRouter(prefix="/rag", tags=["Semantic Hybrid RAG"])

@router.post("/query", response_model=RAGQueryResponse)
def query_rag_engine(
    payload: RAGQueryRequest,
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes hybrid semantic (vector embeddings) and lexical (Okapi BM25) search.
    Strictly filters corpus by current user authorization:
    - PROJECT_LEAD: access all passages in projects they lead.
    - INCOMING_MEMBER: access ONLY approved handovers and verified non-redacted items.
    """
    result = HybridRAGService.answer_question(
        db=db,
        user=current_user,
        question=payload.question,
        project_id=project_id,
        top_k=payload.top_k
    )

    record_audit(
        db,
        "RAG_QUERY_EXECUTED",
        project_id=project_id,
        user=current_user,
        details=f"User asked: '{payload.question[:80]}...'. Status: {result.get('evidence_status')}, Citations: {len(result.get('citations', []))}"
    )

    return RAGQueryResponse(**result)

@router.get("/sample-questions", response_model=List[str])
def get_sample_questions():
    """Provides recommended questions for quick judge and incoming member evaluation."""
    return [
        "What are the pending tasks?",
        "Why was the launch date changed?",
        "Who is responsible for the database migration?",
        "What are the unresolved blockers?",
        "Which architectural decisions were made?",
        "What should the incoming developer work on first?"
    ]
