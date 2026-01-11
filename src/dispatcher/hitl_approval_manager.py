"""
Human-in-the-Loop (HITL) Approval Manager

Manages approval requests for high-risk skill executions.
Provides file-based approval workflow with timeout handling.

Features:
- Approval request creation and persistence
- File-based approval/rejection workflow
- Timeout handling with configurable auto-approval
- Risk assessment and impact analysis
- Automatic cleanup of processed requests
- User identity tracking
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional


class ApprovalTimeoutError(Exception):
    """Raised when approval request times out"""
    pass


class ApprovalRejectedError(Exception):
    """Raised when approval request is rejected by user"""
    pass


class HITLApprovalRequest:
    """
    Represents a human approval request for high-risk skill execution.

    Attributes:
        request_id: Unique identifier for this request
        timestamp: When the request was created
        expires_at: When the request expires (timeout)
        trigger_event: Event that triggered this request
        skill_to_invoke: Name of the skill requiring approval
        risk_level: Risk classification (low, medium, high)
        risk_assessment: Detailed risk analysis
        recommended_action: Suggested decision (approve/reject)
        reasoning: Explanation for recommendation
        status: Current status (pending, approved, rejected, timeout)
        auto_approve_on_timeout: Whether to auto-approve on timeout
        approved_by: User who approved (if applicable)
        approval_timestamp: When approval was granted
        user_comment: Optional comment from user
    """

    def __init__(
        self,
        trigger_event: Dict,
        skill_to_invoke: str,
        risk_level: str,
        risk_assessment: Dict,
        recommended_action: str = "approve",
        reasoning: str = "",
        timeout_seconds: int = 300,
        auto_approve_on_timeout: bool = False
    ):
        """
        Initialize an approval request.

        Args:
            trigger_event: Event details that triggered this request
            skill_to_invoke: Name of skill requiring approval
            risk_level: Risk classification (low, medium, high)
            risk_assessment: Detailed risk analysis dict
            recommended_action: Suggested decision (approve/reject)
            reasoning: Explanation for recommendation
            timeout_seconds: Seconds before request expires
            auto_approve_on_timeout: Auto-approve if no response
        """
        self.request_id = f"req-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        self.timestamp = datetime.now().isoformat()
        self.expires_at = (datetime.now() + timedelta(seconds=timeout_seconds)).isoformat()
        self.trigger_event = trigger_event
        self.skill_to_invoke = skill_to_invoke
        self.risk_level = risk_level
        self.risk_assessment = risk_assessment
        self.recommended_action = recommended_action
        self.reasoning = reasoning
        self.status = "pending"
        self.auto_approve_on_timeout = auto_approve_on_timeout
        self.approved_by: Optional[str] = None
        self.approval_timestamp: Optional[str] = None
        self.user_comment: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert request to dictionary for JSON serialization."""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "expires_at": self.expires_at,
            "trigger_event": self.trigger_event,
            "skill_to_invoke": self.skill_to_invoke,
            "risk_level": self.risk_level,
            "risk_assessment": self.risk_assessment,
            "recommended_action": self.recommended_action,
            "reasoning": self.reasoning,
            "status": self.status,
            "auto_approve_on_timeout": self.auto_approve_on_timeout,
            "approved_by": self.approved_by,
            "approval_timestamp": self.approval_timestamp,
            "user_comment": self.user_comment
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'HITLApprovalRequest':
        """Create request from dictionary."""
        request = cls(
            trigger_event=data["trigger_event"],
            skill_to_invoke=data["skill_to_invoke"],
            risk_level=data["risk_level"],
            risk_assessment=data["risk_assessment"],
            recommended_action=data.get("recommended_action", "approve"),
            reasoning=data.get("reasoning", ""),
            timeout_seconds=300,  # Will be recalculated from expires_at
            auto_approve_on_timeout=data.get("auto_approve_on_timeout", False)
        )
        # Override with saved values
        request.request_id = data["request_id"]
        request.timestamp = data["timestamp"]
        request.expires_at = data["expires_at"]
        request.status = data.get("status", "pending")
        request.approved_by = data.get("approved_by")
        request.approval_timestamp = data.get("approval_timestamp")
        request.user_comment = data.get("user_comment")
        return request


class HITLApprovalManager:
    """
    Manages human approval requests for high-risk skill executions.

    Provides file-based approval workflow with timeout handling.
    """

    def __init__(self, approvals_dir: str = ".approvals"):
        """
        Initialize the approval manager.

        Args:
            approvals_dir: Directory for storing approval request files
        """
        self.approvals_dir = Path(approvals_dir)
        self.approvals_dir.mkdir(parents=True, exist_ok=True)

    def create_approval_request(
        self,
        trigger_event: Dict,
        skill_to_invoke: str,
        risk_level: str,
        risk_assessment: Dict,
        recommended_action: str = "approve",
        reasoning: str = "",
        timeout_seconds: int = 300,
        auto_approve_on_timeout: bool = False
    ) -> HITLApprovalRequest:
        """
        Create and persist an approval request.

        Args:
            trigger_event: Event details that triggered this request
            skill_to_invoke: Name of skill requiring approval
            risk_level: Risk classification (low, medium, high)
            risk_assessment: Detailed risk analysis
            recommended_action: Suggested decision
            reasoning: Explanation for recommendation
            timeout_seconds: Seconds before timeout
            auto_approve_on_timeout: Auto-approve on timeout

        Returns:
            Created HITLApprovalRequest instance
        """
        request = HITLApprovalRequest(
            trigger_event=trigger_event,
            skill_to_invoke=skill_to_invoke,
            risk_level=risk_level,
            risk_assessment=risk_assessment,
            recommended_action=recommended_action,
            reasoning=reasoning,
            timeout_seconds=timeout_seconds,
            auto_approve_on_timeout=auto_approve_on_timeout
        )

        # Persist to file
        self._save_request(request)

        return request

    def _save_request(self, request: HITLApprovalRequest):
        """Save approval request to file."""
        file_path = self.approvals_dir / f"pending_{request.request_id}.json"
        with open(file_path, 'w') as f:
            json.dump(request.to_dict(), f, indent=2)

    def _load_request(self, request_id: str) -> Optional[HITLApprovalRequest]:
        """Load approval request from file."""
        file_path = self.approvals_dir / f"pending_{request_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return HITLApprovalRequest.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def wait_for_approval(
        self,
        request: HITLApprovalRequest,
        poll_interval: float = 1.0
    ) -> bool:
        """
        Wait for user approval/rejection.

        Polls the approval file for status updates until timeout.

        Args:
            request: Approval request to wait for
            poll_interval: Seconds between status checks

        Returns:
            True if approved, False if rejected

        Raises:
            ApprovalTimeoutError: If request times out
            ApprovalRejectedError: If user rejects request
        """
        expires_at = datetime.fromisoformat(request.expires_at)

        while datetime.now() < expires_at:
            # Reload request to check for updates
            current_request = self._load_request(request.request_id)

            if current_request is None:
                raise ApprovalRejectedError("Approval request file was deleted")

            if current_request.status == "approved":
                return True

            if current_request.status == "rejected":
                raise ApprovalRejectedError(
                    f"Request rejected by {current_request.approved_by}: "
                    f"{current_request.user_comment or 'No reason provided'}"
                )

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout reached
        if request.auto_approve_on_timeout:
            self._update_request_status(
                request.request_id,
                status="approved",
                approved_by="system",
                user_comment="Auto-approved on timeout"
            )
            return True
        else:
            self._update_request_status(
                request.request_id,
                status="timeout"
            )
            raise ApprovalTimeoutError(
                f"Approval request {request.request_id} timed out"
            )

    def _update_request_status(
        self,
        request_id: str,
        status: str,
        approved_by: Optional[str] = None,
        user_comment: Optional[str] = None
    ):
        """Update approval request status."""
        request = self._load_request(request_id)
        if request is None:
            return

        request.status = status
        if approved_by:
            request.approved_by = approved_by
            request.approval_timestamp = datetime.now().isoformat()
        if user_comment:
            request.user_comment = user_comment

        self._save_request(request)

    def approve_request(
        self,
        request_id: str,
        user: str,
        comment: Optional[str] = None
    ):
        """
        Approve a pending request.

        Args:
            request_id: ID of request to approve
            user: User identity (username, email, etc.)
            comment: Optional approval comment
        """
        self._update_request_status(
            request_id,
            status="approved",
            approved_by=user,
            user_comment=comment or "Approved via CLI"
        )

    def reject_request(
        self,
        request_id: str,
        user: str,
        reason: Optional[str] = None
    ):
        """
        Reject a pending request.

        Args:
            request_id: ID of request to reject
            user: User identity
            reason: Rejection reason
        """
        self._update_request_status(
            request_id,
            status="rejected",
            approved_by=user,
            user_comment=reason or "Rejected via CLI"
        )

    def list_pending_requests(self) -> list:
        """
        List all pending approval requests.

        Returns:
            List of pending HITLApprovalRequest instances
        """
        pending_requests = []

        for file_path in self.approvals_dir.glob("pending_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                request = HITLApprovalRequest.from_dict(data)

                if request.status == "pending":
                    pending_requests.append(request)
            except (json.JSONDecodeError, KeyError):
                continue

        return pending_requests

    def cleanup_old_requests(self, max_age_hours: int = 24):
        """
        Clean up processed approval requests older than max_age.

        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        for file_path in self.approvals_dir.glob("pending_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                timestamp = datetime.fromisoformat(data["timestamp"])
                status = data.get("status", "pending")

                # Remove if processed and old
                if status in ["approved", "rejected", "timeout"] and timestamp < cutoff_time:
                    file_path.unlink()

            except (json.JSONDecodeError, KeyError, ValueError):
                continue


# Singleton instance for global use
_hitl_manager_instance: Optional[HITLApprovalManager] = None


def get_hitl_approval_manager() -> HITLApprovalManager:
    """
    Get the global HITLApprovalManager singleton instance.

    Returns:
        Shared HITLApprovalManager instance
    """
    global _hitl_manager_instance
    if _hitl_manager_instance is None:
        _hitl_manager_instance = HITLApprovalManager()
    return _hitl_manager_instance
