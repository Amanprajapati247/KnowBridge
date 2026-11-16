from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.models import Project, ExternalConnector, ExternalRecord, User
from app.schemas import (
    ConnectorConnect, ConnectorOut, ExternalRecordOut, ConnectorSyncResult
)
from app.api.deps import require_project_lead, record_audit
from app.services.connectors import GitHubService, TaskConnectorService

router = APIRouter(prefix="", tags=["Connectors"])

@router.get("/projects/{id}/connectors", response_model=List[ConnectorOut])
def list_connectors(
    id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    connectors = db.query(ExternalConnector).filter(ExternalConnector.project_id == id).all()
    out = []
    for c in connectors:
        rec_count = db.query(ExternalRecord).filter(ExternalRecord.connector_id == c.id).count()
        out.append(ConnectorOut(
            id=c.id,
            project_id=c.project_id,
            provider=c.provider,
            name=c.name,
            repo_url=c.repo_url,
            branch=c.branch,
            status=c.status,
            last_synced_at=c.last_synced_at,
            sync_summary=c.sync_summary,
            error_message=c.error_message,
            created_at=c.created_at,
            records_count=rec_count
        ))
    return out

@router.post("/projects/{id}/connectors/github", response_model=ConnectorOut, status_code=status.HTTP_201_CREATED)
def connect_github_repo(
    id: int,
    payload: ConnectorConnect,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    repo_name = payload.repo_name_or_key.strip().removeprefix("https://github.com/").removesuffix(".git").strip("/")
    parts = repo_name.split("/")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Repository must be specified as 'owner/repo' (e.g. Amanprajapati247/KnowBridge)"
        )

    # Check for duplicate connector on this project
    existing = db.query(ExternalConnector).filter(
        ExternalConnector.project_id == id,
        ExternalConnector.provider == "GITHUB",
        ExternalConnector.name == repo_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"GitHub repository '{repo_name}' is already connected to this project.")

    # Test connection
    ok, msg, repo_meta = GitHubService.test_connection(repo_name, payload.access_token)
    repo_url = repo_meta.get("html_url") or f"https://github.com/{repo_name}"

    connector = ExternalConnector(
        project_id=project.id,
        provider="GITHUB",
        name=repo_name,
        repo_url=repo_url,
        branch=payload.branch or "main",
        status="CONNECTED" if ok else "ERROR",
        error_message=None if ok else msg,
        sync_summary="Repository connected. Run Sync to import commits and issues." if ok else msg
    )
    db.add(connector)
    db.commit()
    db.refresh(connector)

    # If connection was successful, trigger initial sync
    if ok:
        try:
            GitHubService.sync_connector(db, connector, payload.access_token)
            db.refresh(connector)
        except Exception as e:
            connector.status = "ERROR"
            connector.error_message = f"Sync failed: {str(e)}"
            db.commit()

    record_audit(
        db,
        "CONNECTOR_CONNECTED",
        project_id=project.id,
        user=current_user,
        details=f"Connected GitHub repository '{repo_name}'"
    )

    rec_count = db.query(ExternalRecord).filter(ExternalRecord.connector_id == connector.id).count()
    return ConnectorOut(
        id=connector.id,
        project_id=connector.project_id,
        provider=connector.provider,
        name=connector.name,
        repo_url=connector.repo_url,
        branch=connector.branch,
        status=connector.status,
        last_synced_at=connector.last_synced_at,
        sync_summary=connector.sync_summary,
        error_message=connector.error_message,
        created_at=connector.created_at,
        records_count=rec_count
    )

@router.post("/projects/{id}/connectors/{connector_id}/sync", response_model=ConnectorSyncResult)
def sync_connector_records(
    id: int,
    connector_id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    connector = db.query(ExternalConnector).filter(
        ExternalConnector.id == connector_id,
        ExternalConnector.project_id == id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    if connector.provider == "GITHUB":
        imported_recs, extracted_claims, summary = GitHubService.sync_connector(db, connector)
    elif connector.provider in ("JIRA", "LINEAR"):
        imported_recs, extracted_claims, summary = TaskConnectorService.sync_task_connector(db, connector)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider '{connector.provider}'")

    record_audit(
        db,
        "CONNECTOR_SYNCED",
        project_id=project.id,
        user=current_user,
        details=f"Synchronized {connector.provider} connector '{connector.name}': {imported_recs} records imported."
    )

    return ConnectorSyncResult(
        connector_id=connector.id,
        provider=connector.provider,
        status=connector.status,
        synced_records=imported_recs,
        new_claims_extracted=extracted_claims,
        sync_summary=summary,
        error_message=connector.error_message
    )

@router.get("/projects/{id}/connectors/{connector_id}/records", response_model=List[ExternalRecordOut])
def list_connector_records(
    id: int,
    connector_id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    records = db.query(ExternalRecord).filter(
        ExternalRecord.connector_id == connector_id,
        ExternalRecord.project_id == id
    ).order_by(ExternalRecord.id.desc()).all()
    return records

@router.delete("/projects/{id}/connectors/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connector(
    id: int,
    connector_id: int,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    connector = db.query(ExternalConnector).filter(
        ExternalConnector.id == connector_id,
        ExternalConnector.project_id == id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    record_audit(
        db,
        "CONNECTOR_DISCONNECTED",
        project_id=project.id,
        user=current_user,
        details=f"Disconnected {connector.provider} connector '{connector.name}'"
    )
    db.delete(connector)
    db.commit()
    return None

@router.post("/projects/{id}/connectors/task-board", response_model=ConnectorOut, status_code=status.HTTP_201_CREATED)
def connect_task_board(
    id: int,
    payload: ConnectorConnect,
    current_user: User = Depends(require_project_lead),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == id, Project.lead_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    provider = payload.provider.upper()
    if provider not in ("JIRA", "LINEAR"):
        raise HTTPException(status_code=400, detail="Task board provider must be 'JIRA' or 'LINEAR'")

    name = payload.repo_name_or_key.strip()
    connector = ExternalConnector(
        project_id=project.id,
        provider=provider,
        name=name,
        repo_url=payload.instance_url or payload.repo_url,
        branch="main",
        status="CONNECTED",
        sync_summary=f"{provider} board '{name}' registered. Ready for live sync when API keys are configured."
    )
    db.add(connector)
    db.commit()
    db.refresh(connector)

    record_audit(
        db,
        "CONNECTOR_CONNECTED",
        project_id=project.id,
        user=current_user,
        details=f"Connected {provider} board '{name}'"
    )

    return ConnectorOut(
        id=connector.id,
        project_id=connector.project_id,
        provider=connector.provider,
        name=connector.name,
        repo_url=connector.repo_url,
        branch=connector.branch,
        status=connector.status,
        last_synced_at=connector.last_synced_at,
        sync_summary=connector.sync_summary,
        error_message=connector.error_message,
        created_at=connector.created_at,
        records_count=0
    )
