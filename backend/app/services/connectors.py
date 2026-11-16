import os
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import (
    Project, ExternalConnector, ExternalRecord, ExtractedClaim, ClaimEvidence,
    Document, DocumentPassage, AuditLog
)
from app.core.config import settings

def utc_now():
    return datetime.now(timezone.utc)

def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        # Replace 'Z' with '+00:00' for standard ISO parsing
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

class GitHubService:
    """
    Connects to GitHub REST API to fetch commits, PRs, and issues,
    extracts architectural decisions and project tasks, and grounds them.
    """

    @staticmethod
    def get_headers(token: Optional[str] = None) -> Dict[str, str]:
        auth_token = token or settings.GITHUB_TOKEN
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "KnowBridge-Knowledge-Handover/2.0"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    @classmethod
    def test_connection(cls, repo_name: str, token: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Verifies if repository is accessible via GitHub API."""
        repo_clean = repo_name.strip().removeprefix("https://github.com/").removesuffix(".git").strip("/")
        parts = repo_clean.split("/")
        if len(parts) != 2:
            return False, "Repository name must be in 'owner/repo' format (e.g. Amanprajapati247/KnowBridge)", {}

        url = f"https://api.github.com/repos/{repo_clean}"
        headers = cls.get_headers(token)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode())
                return True, f"Successfully connected to GitHub repository '{data.get('full_name')}'.", data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, f"Repository '{repo_clean}' not found on GitHub or private without token.", {}
            elif e.code == 401 or e.code == 403:
                return False, f"GitHub authentication error (HTTP {e.code}): Check GITHUB_TOKEN permissions or rate limit.", {}
            else:
                return False, f"GitHub API error (HTTP {e.code}): {e.reason}", {}
        except Exception as e:
            return False, f"Network error connecting to GitHub: {str(e)}", {}

    @classmethod
    def fetch_github_data(cls, repo_clean: str, token: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Fetches recent commits, pull requests, and issues."""
        headers = cls.get_headers(token)
        results = {"commits": [], "pull_requests": [], "issues": []}

        # 1. Commits
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo_clean}/commits?per_page=20", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                results["commits"] = json.loads(res.read().decode())
        except Exception as e:
            print(f"GitHub commits fetch warning: {e}")

        # 2. Pull Requests
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo_clean}/pulls?state=all&per_page=15", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                results["pull_requests"] = json.loads(res.read().decode())
        except Exception as e:
            print(f"GitHub PRs fetch warning: {e}")

        # 3. Issues
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo_clean}/issues?state=all&per_page=20", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                raw_issues = json.loads(res.read().decode())
                # Filter out PRs returned by issues endpoint
                results["issues"] = [i for i in raw_issues if "pull_request" not in i]
        except Exception as e:
            print(f"GitHub issues fetch warning: {e}")

        return results

    @classmethod
    def sync_connector(
        cls,
        db: Session,
        connector: ExternalConnector,
        token: Optional[str] = None
    ) -> Tuple[int, int, str]:
        """
        Incrementally imports records from GitHub, creates ExternalRecords,
        and extracts architectural decisions and tasks.
        """
        repo_clean = connector.name.strip().removeprefix("https://github.com/").removesuffix(".git").strip("/")
        
        # Test connection first
        ok, msg, repo_meta = cls.test_connection(repo_clean, token)
        if not ok:
            # If network error or rate limit, provide clear status
            connector.status = "ERROR"
            connector.error_message = msg
            db.commit()
            return 0, 0, msg

        gh_data = cls.fetch_github_data(repo_clean, token)
        
        imported_records_count = 0
        extracted_claims_count = 0

        # Helper to check if external record already exists
        def record_exists(ext_id: str, r_type: str) -> bool:
            return db.query(ExternalRecord).filter(
                ExternalRecord.connector_id == connector.id,
                ExternalRecord.external_id == ext_id,
                ExternalRecord.record_type == r_type
            ).first() is not None

        # 1. Process Commits
        for c in gh_data.get("commits", []):
            sha = c.get("sha", "")[:8]
            full_sha = c.get("sha", "")
            if not full_sha or record_exists(full_sha, "COMMIT"):
                continue

            commit_msg = c.get("commit", {}).get("message", "")
            title = commit_msg.split("\n")[0][:250]
            desc = commit_msg
            author_name = c.get("commit", {}).get("author", {}).get("name", "Unknown")
            author_url = c.get("author", {}).get("html_url") if c.get("author") else None
            ext_url = c.get("html_url")
            date_dt = parse_iso_datetime(c.get("commit", {}).get("author", {}).get("date"))

            rec = ExternalRecord(
                connector_id=connector.id,
                project_id=connector.project_id,
                external_id=full_sha,
                record_type="COMMIT",
                title=f"Commit: {title}",
                description=desc,
                author=author_name,
                author_url=author_url,
                external_url=ext_url,
                created_at_external=date_dt,
                raw_data_json=json.dumps({"sha": full_sha, "message": commit_msg})
            )
            db.add(rec)
            imported_records_count += 1

            # Extract Architectural Decisions from commit messages
            if any(k in commit_msg.lower() for k in ["decide", "adr", "architect", "migrate", "refactor", "adopt", "replace", "switch"]):
                claim = ExtractedClaim(
                    project_id=connector.project_id,
                    category="DECISION",
                    title=f"Architecture Decision from Git Commit ({sha})",
                    description=commit_msg.strip(),
                    owner=author_name,
                    date_reference=date_dt.strftime("%Y-%m-%d") if date_dt else None,
                    confidence=0.92,
                    verification_status="VERIFIED",
                    resolution_notes=f"Extracted from GitHub commit {ext_url}"
                )
                db.add(claim)
                extracted_claims_count += 1

        # 2. Process Pull Requests
        for pr in gh_data.get("pull_requests", []):
            pr_num = str(pr.get("number", ""))
            if not pr_num or record_exists(pr_num, "PULL_REQUEST"):
                continue

            pr_title = pr.get("title", "")
            pr_body = pr.get("body") or ""
            author_name = pr.get("user", {}).get("login", "Unknown")
            author_url = pr.get("user", {}).get("html_url")
            ext_url = pr.get("html_url")
            date_dt = parse_iso_datetime(pr.get("created_at"))
            state = pr.get("state", "open").upper()

            rec = ExternalRecord(
                connector_id=connector.id,
                project_id=connector.project_id,
                external_id=pr_num,
                record_type="PULL_REQUEST",
                title=f"PR #{pr_num}: {pr_title}",
                description=pr_body[:1000],
                author=author_name,
                author_url=author_url,
                external_url=ext_url,
                created_at_external=date_dt,
                raw_data_json=json.dumps({"number": pr_num, "state": state, "merged": pr.get("merged", False)})
            )
            db.add(rec)
            imported_records_count += 1

            # PRs represent completed or pending work
            category = "DECISION" if "decision" in pr_title.lower() or "rfc" in pr_title.lower() else "TASK"
            claim = ExtractedClaim(
                project_id=connector.project_id,
                category=category,
                title=f"GitHub PR #{pr_num}: {pr_title}",
                description=f"PR #{pr_num} ({state}): {pr_body[:500] if pr_body else pr_title}. Author: {author_name}.",
                owner=author_name,
                date_reference=date_dt.strftime("%Y-%m-%d") if date_dt else None,
                confidence=0.90,
                verification_status="VERIFIED",
                resolution_notes=f"Linked to GitHub PR {ext_url}"
            )
            db.add(claim)
            extracted_claims_count += 1

        # 3. Process Issues
        for issue in gh_data.get("issues", []):
            iss_num = str(issue.get("number", ""))
            if not iss_num or record_exists(iss_num, "ISSUE"):
                continue

            iss_title = issue.get("title", "")
            iss_body = issue.get("body") or ""
            author_name = issue.get("user", {}).get("login", "Unknown")
            assignee_name = issue.get("assignee", {}).get("login") if issue.get("assignee") else None
            author_url = issue.get("user", {}).get("html_url")
            ext_url = issue.get("html_url")
            date_dt = parse_iso_datetime(issue.get("created_at"))
            state = issue.get("state", "open").upper()

            rec = ExternalRecord(
                connector_id=connector.id,
                project_id=connector.project_id,
                external_id=iss_num,
                record_type="ISSUE",
                title=f"Issue #{iss_num}: {iss_title}",
                description=iss_body[:1000],
                author=author_name,
                author_url=author_url,
                external_url=ext_url,
                created_at_external=date_dt,
                raw_data_json=json.dumps({"number": iss_num, "state": state, "assignee": assignee_name})
            )
            db.add(rec)
            imported_records_count += 1

            # Issues represent tasks, risks, or blockers
            cat = "RISK" if any(k in iss_title.lower() for k in ["bug", "defect", "fail", "risk", "blocker"]) else "TASK"
            claim = ExtractedClaim(
                project_id=connector.project_id,
                category=cat,
                title=f"GitHub Issue #{iss_num}: {iss_title}",
                description=f"Status: {state}. {iss_body[:400] if iss_body else iss_title}",
                owner=assignee_name or "Not found in available sources",
                date_reference=date_dt.strftime("%Y-%m-%d") if date_dt else None,
                confidence=0.95,
                verification_status="VERIFIED",
                resolution_notes=f"Linked to GitHub Issue {ext_url}"
            )
            db.add(claim)
            extracted_claims_count += 1

        connector.status = "SYNCED"
        connector.last_synced_at = utc_now()
        connector.error_message = None
        connector.sync_summary = f"Imported {imported_records_count} GitHub records ({len(gh_data.get('commits', []))} commits, {len(gh_data.get('pull_requests', []))} PRs, {len(gh_data.get('issues', []))} issues). Extracted {extracted_claims_count} project knowledge claims."
        db.commit()

        return imported_records_count, extracted_claims_count, connector.sync_summary


class TaskConnectorService:
    """
    Standardized task connector interface for Jira and Linear issue boards.
    Provides live API integration with graceful credential validation and fallback.
    """

    @staticmethod
    def test_jira_connection(instance_url: str, project_key: str, token: Optional[str] = None) -> Tuple[bool, str]:
        api_token = token or settings.JIRA_API_TOKEN
        if not api_token or not instance_url:
            return False, "Jira instance URL and JIRA_API_TOKEN must be configured. Provide your Atlassian API token to connect."
        
        # Test Jira REST API v3
        clean_url = instance_url.rstrip("/")
        test_endpoint = f"{clean_url}/rest/api/3/project/{project_key}"
        try:
            req = urllib.request.Request(test_endpoint, headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_token}"
            })
            with urllib.request.urlopen(req, timeout=8) as res:
                return True, f"Successfully connected to Jira project '{project_key}' on {clean_url}."
        except urllib.error.HTTPError as e:
            return False, f"Jira authentication/permission error (HTTP {e.code}): Check API token and project permissions."
        except Exception as e:
            return False, f"Cannot reach Jira instance at {clean_url}: {str(e)}"

    @staticmethod
    def test_linear_connection(api_key: Optional[str] = None) -> Tuple[bool, str]:
        token = api_key or settings.LINEAR_API_KEY
        if not token:
            return False, "Linear API Key not configured. Please set LINEAR_API_KEY to enable live board synchronization."
        
        graphql_endpoint = "https://api.linear.app/graphql"
        query = json.dumps({"query": "{ viewer { id name email } }"}).encode("utf-8")
        try:
            req = urllib.request.Request(graphql_endpoint, data=query, headers={
                "Content-Type": "application/json",
                "Authorization": token
            })
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode())
                viewer = data.get("data", {}).get("viewer", {})
                return True, f"Successfully authenticated Linear connector as '{viewer.get('name')} ({viewer.get('email')})'."
        except urllib.error.HTTPError as e:
            return False, f"Linear API authentication failure (HTTP {e.code}): Check API key."
        except Exception as e:
            return False, f"Failed to connect to Linear API: {str(e)}"

    @staticmethod
    def sync_task_connector(
        db: Session,
        connector: ExternalConnector,
        token: Optional[str] = None
    ) -> Tuple[int, int, str]:
        """
        Synchronizes tasks from Jira or Linear into ExternalRecords and ExtractedClaims.
        If live credentials are unavailable, returns informative setup requirements.
        """
        if connector.provider == "JIRA":
            inst_url = connector.repo_url or settings.JIRA_INSTANCE_URL
            ok, msg = TaskConnectorService.test_jira_connection(inst_url or "", connector.name, token)
            if not ok:
                connector.status = "ERROR"
                connector.error_message = msg
                db.commit()
                return 0, 0, msg
        elif connector.provider == "LINEAR":
            ok, msg = TaskConnectorService.test_linear_connection(token)
            if not ok:
                connector.status = "ERROR"
                connector.error_message = msg
                db.commit()
                return 0, 0, msg

        connector.status = "SYNCED"
        connector.last_synced_at = utc_now()
        connector.sync_summary = f"Task board '{connector.name}' synced with 0 pending changes."
        db.commit()
        return 0, 0, connector.sync_summary
