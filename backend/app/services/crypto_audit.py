import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import (
    Document, Handover, HandoverItem, HandoverSnapshot, HandoverAcknowledgment,
    AuditLog, User, Project
)

def utc_now():
    return datetime.now(timezone.utc)

class CryptoAuditService:
    """
    Cryptographic auditing, SHA-256 content hashing, version snapshotting,
    diff comparison, and incoming member acknowledgment receipts.
    """

    @staticmethod
    def calculate_file_sha256(file_path: str) -> str:
        """Calculates SHA-256 hash of a file on disk."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def calculate_bytes_sha256(data: bytes) -> str:
        """Calculates SHA-256 hash of raw bytes."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def serialize_handover_canonical(handover: Handover) -> Tuple[str, str]:
        """
        Creates a deterministic, canonical JSON representation of a handover
        and calculates its SHA-256 snapshot hash.
        """
        # Sort items deterministically by section, display_order, and title
        sorted_items = sorted(
            handover.items,
            key=lambda x: (x.section, x.display_order, x.title)
        )

        items_payload = []
        for it in sorted_items:
            items_payload.append({
                "claim_id": it.claim_id,
                "section": it.section,
                "title": it.title.strip(),
                "content": it.content.strip(),
                "source_filename": it.source_filename,
                "source_page": it.source_page,
                "evidence_excerpt": (it.evidence_excerpt or "").strip(),
                "verification_status": it.verification_status,
                "is_accepted": it.is_accepted,
                "is_rejected": it.is_rejected,
                "is_redacted": it.is_redacted
            })

        canonical_dict = {
            "handover_id": handover.id,
            "project_id": handover.project_id,
            "version": handover.version,
            "title": handover.title.strip(),
            "executive_summary": (handover.executive_summary or "").strip(),
            "current_status": (handover.current_status or "").strip(),
            "recommended_actions": (handover.recommended_actions or "").strip(),
            "missing_information": (handover.missing_information or "").strip(),
            "conflicting_information": (handover.conflicting_information or "").strip(),
            "items": items_payload
        }

        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        return canonical_json, snapshot_hash

    @classmethod
    def create_approved_snapshot(
        cls,
        db: Session,
        handover: Handover,
        lead_user: User,
        approval_notes: Optional[str] = None
    ) -> HandoverSnapshot:
        """
        Creates an immutable HandoverSnapshot record with a verified SHA-256 hash.
        Preserves historical versions so they can never be silently overwritten.
        """
        canonical_json, snapshot_hash = cls.serialize_handover_canonical(handover)

        # Update handover hash and approval fields
        handover.status = "APPROVED"
        handover.snapshot_hash = snapshot_hash
        handover.approved_by_id = lead_user.id
        handover.approved_at = utc_now()
        handover.approval_notes = approval_notes

        snapshot = HandoverSnapshot(
            handover_id=handover.id,
            project_id=handover.project_id,
            version=handover.version,
            snapshot_hash=snapshot_hash,
            title=handover.title,
            executive_summary=handover.executive_summary,
            current_status=handover.current_status,
            recommended_actions=handover.recommended_actions,
            missing_information=handover.missing_information,
            conflicting_information=handover.conflicting_information,
            items_json=canonical_json,
            approved_by_id=lead_user.id,
            approved_at=handover.approved_at,
            approval_notes=approval_notes
        )
        db.add(snapshot)

        # Log audit entry with hash
        audit = AuditLog(
            project_id=handover.project_id,
            user_id=lead_user.id,
            user_name=lead_user.full_name,
            action="HANDOVER_APPROVED",
            details=f"Approved Handover v{handover.version} (SHA-256: {snapshot_hash[:16]}...). Notes: {approval_notes or 'Signed off'}",
            sha256_hash=snapshot_hash
        )
        db.add(audit)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @classmethod
    def verify_handover_integrity(cls, handover: Handover) -> Dict[str, Any]:
        """
        Recalculates the SHA-256 hash of the handover and verifies it against the recorded hash.
        Detects any unauthorized modification or bit-level tampering.
        """
        if not handover.snapshot_hash:
            return {
                "handover_id": handover.id,
                "version": handover.version,
                "has_snapshot": False,
                "is_verified": False,
                "message": "Handover has not been officially approved and hashed."
            }

        _, current_hash = cls.serialize_handover_canonical(handover)
        is_match = (current_hash == handover.snapshot_hash)

        return {
            "handover_id": handover.id,
            "version": handover.version,
            "recorded_hash": handover.snapshot_hash,
            "recalculated_hash": current_hash,
            "is_verified": is_match,
            "is_tampered": not is_match,
            "algorithm": "SHA-256",
            "message": "Content integrity verified. Zero unauthorized modifications detected." if is_match else "Integrity Warning: Current handover content does not match the approved cryptographic hash!"
        }

    @classmethod
    def compare_snapshots(
        cls,
        snapshot_v1: HandoverSnapshot,
        snapshot_v2: HandoverSnapshot
    ) -> Dict[str, Any]:
        """
        Performs a semantic diff between two approved handover versions (e.g. v1.0 vs v2.0).
        Identifies added, removed, and modified claims and sections.
        """
        data1 = json.loads(snapshot_v1.items_json)
        data2 = json.loads(snapshot_v2.items_json)

        items1 = data1.get("items", [])
        items2 = data2.get("items", [])

        # Index items by (section, title)
        map1 = {(it["section"], it["title"]): it for it in items1}
        map2 = {(it["section"], it["title"]): it for it in items2}

        all_keys = list(set(list(map1.keys()) + list(map2.keys())))
        all_keys.sort()

        diff_items = []
        added_count = 0
        removed_count = 0
        modified_count = 0
        unchanged_count = 0

        for key in all_keys:
            section, title = key
            in_v1 = key in map1
            in_v2 = key in map2

            if in_v2 and not in_v1:
                it = map2[key]
                added_count += 1
                diff_items.append({
                    "change_type": "ADDED",
                    "section": section,
                    "title": title,
                    "old_content": None,
                    "new_content": it.get("content"),
                    "verification_status": it.get("verification_status", "VERIFIED"),
                    "source_filename": it.get("source_filename")
                })
            elif in_v1 and not in_v2:
                it = map1[key]
                removed_count += 1
                diff_items.append({
                    "change_type": "REMOVED",
                    "section": section,
                    "title": title,
                    "old_content": it.get("content"),
                    "new_content": None,
                    "verification_status": it.get("verification_status", "VERIFIED"),
                    "source_filename": it.get("source_filename")
                })
            else:
                it1 = map1[key]
                it2 = map2[key]
                if (it1.get("content") != it2.get("content") or
                    it1.get("verification_status") != it2.get("verification_status") or
                    it1.get("is_redacted") != it2.get("is_redacted")):
                    modified_count += 1
                    diff_items.append({
                        "change_type": "MODIFIED",
                        "section": section,
                        "title": title,
                        "old_content": it1.get("content"),
                        "new_content": it2.get("content"),
                        "verification_status": it2.get("verification_status", "VERIFIED"),
                        "source_filename": it2.get("source_filename")
                    })
                else:
                    unchanged_count += 1
                    diff_items.append({
                        "change_type": "UNCHANGED",
                        "section": section,
                        "title": title,
                        "old_content": it1.get("content"),
                        "new_content": it2.get("content"),
                        "verification_status": it1.get("verification_status", "VERIFIED"),
                        "source_filename": it1.get("source_filename")
                    })

        summary = (
            f"Comparing Handover v{snapshot_v1.version} against v{snapshot_v2.version}: "
            f"{added_count} items added, {modified_count} items updated, "
            f"{removed_count} items removed, and {unchanged_count} items unchanged."
        )

        return {
            "project_id": snapshot_v1.project_id,
            "v1_version": snapshot_v1.version,
            "v2_version": snapshot_v2.version,
            "v1_hash": snapshot_v1.snapshot_hash,
            "v2_hash": snapshot_v2.snapshot_hash,
            "v1_approved_at": snapshot_v1.approved_at,
            "v2_approved_at": snapshot_v2.approved_at,
            "added_count": added_count,
            "removed_count": removed_count,
            "modified_count": modified_count,
            "unchanged_count": unchanged_count,
            "diff_items": diff_items,
            "summary": summary
        }

    @classmethod
    def record_acknowledgment(
        cls,
        db: Session,
        handover: Handover,
        user: User,
        signature_notes: Optional[str] = None
    ) -> HandoverAcknowledgment:
        """
        Records an incoming member's formal acknowledgment of an approved handover.
        Generates a cryptographic receipt token linking user, handover, version, hash, and timestamp.
        """
        if handover.status != "APPROVED":
            raise ValueError("Only officially APPROVED handovers can be acknowledged.")

        now_dt = utc_now()
        iso_ts = now_dt.isoformat()
        snapshot_hash = handover.snapshot_hash or "unhashed-snapshot"

        # Cryptographic receipt token
        token_src = f"{user.id}:{handover.id}:{handover.version}:{snapshot_hash}:{iso_ts}"
        receipt_token = hashlib.sha256(token_src.encode('utf-8')).hexdigest()

        # Find latest snapshot for this handover
        latest_snapshot = db.query(HandoverSnapshot).filter(
            HandoverSnapshot.handover_id == handover.id,
            HandoverSnapshot.version == handover.version
        ).first()

        ack = HandoverAcknowledgment(
            handover_id=handover.id,
            snapshot_id=latest_snapshot.id if latest_snapshot else None,
            project_id=handover.project_id,
            user_id=user.id,
            version=handover.version,
            snapshot_hash=snapshot_hash,
            receipt_token=receipt_token,
            signature_notes=signature_notes or "Acknowledged and accepted project responsibilities.",
            acknowledged_at=now_dt
        )
        db.add(ack)

        # Audit entry
        audit = AuditLog(
            project_id=handover.project_id,
            user_id=user.id,
            user_name=user.full_name,
            action="HANDOVER_ACKNOWLEDGED",
            details=f"Incoming Member {user.full_name} acknowledged Handover v{handover.version} (Receipt: {receipt_token[:16]}...).",
            sha256_hash=receipt_token
        )
        db.add(audit)
        db.commit()
        db.refresh(ack)
        return ack
