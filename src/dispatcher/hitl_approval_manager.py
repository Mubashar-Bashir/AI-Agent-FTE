"""
Human-in-the-Loop (HITL) Approval Manager for high-risk skills
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from .models import HITLApprovalRequest
from .exceptions import ApprovalTimeoutError


class HITLApprovalManager:
    """
    Manages approval requests for high-risk skill executions
    
    Creates approval request files, monitors for responses, handles timeouts
    """
    
    def __init__(
        self,
        approval_dir: str = ".approvals",
        default_timeout_seconds: int = 300,  # 5 minutes
        logger: Optional[logging.Logger] = None
    ):
        self.approval_dir = Path(approval_dir)
        self.default_timeout_seconds = default_timeout_seconds
        self.logger = logger or logging.getLogger(__name__)
        
        # Ensure approval directory exists
        self.approval_dir.mkdir(parents=True, exist_ok=True)
    
    def create_approval_request(
        self,
        skill_name: str,
        trigger_event: Dict[str, Any],
        risk_level: str = "high",
        timeout_seconds: Optional[int] = None,
        auto_approve_on_timeout: bool = False
    ) -> HITLApprovalRequest:
        """
        Create a new approval request for a high-risk skill
        
        Args:
            skill_name: Name of the skill requiring approval
            trigger_event: Event that triggered this skill
            risk_level: Risk level of the skill
            timeout_seconds: How long to wait for approval
            auto_approve_on_timeout: Whether to proceed if no response
            
        Returns:
            HITLApprovalRequest object
        """
        timeout = timeout_seconds or self.default_timeout_seconds
        expires_at = datetime.now() + timedelta(seconds=timeout)
        
        # Create approval request
        request = HITLApprovalRequest(
            trigger_event=trigger_event,
            skill_to_invoke=skill_name,
            risk_level=risk_level,
            expires_at=expires_at,
            auto_approve_on_timeout=auto_approve_on_timeout
        )
        
        # Generate risk assessment
        request.risk_assessment = self._generate_risk_assessment(
            skill_name=skill_name,
            trigger_event=trigger_event,
            risk_level=risk_level
        )
        
        # Generate recommendation
        request.recommended_action = "approve"
        request.reasoning = (
            f"Skill '{skill_name}' is needed to address the detected issue. "
            f"All changes will be version-controlled and reviewable."
        )
        
        # Save request to file
        self._save_request(request)
        
        self.logger.info(
            f"Created approval request: {request.request_id} for skill '{skill_name}'"
        )
        
        # Display to user
        self._display_approval_request(request)
        
        return request
    
    def _generate_risk_assessment(
        self,
        skill_name: str,
        trigger_event: Dict[str, Any],
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate risk assessment based on skill and context"""
        
        # Base risk assessment
        assessment = {
            "description": f"This skill may make changes to your codebase.",
            "potential_impact": [],
            "affected_files": [],
            "reversible": True
        }
        
        # Skill-specific risk assessments
        if "test" in skill_name.lower():
            assessment["potential_impact"] = [
                "Test file creation",
                "Test file modifications",
                "Test assertions updates"
            ]
            assessment["description"] = (
                "This skill will create or modify test files to address the detected failure."
            )
        
        elif "debug" in skill_name.lower():
            assessment["potential_impact"] = [
                "Code analysis",
                "Potential code modifications",
                "Logging additions"
            ]
            assessment["description"] = (
                "This skill will analyze the error and may propose code fixes."
            )
        
        # Extract affected files from trigger event
        source_file = trigger_event.get("source_file", "")
        if source_file:
            assessment["affected_files"].append(source_file)
        
        return assessment
    
    def _save_request(self, request: HITLApprovalRequest):
        """Save approval request to file"""
        filepath = self.approval_dir / f"pending_{request.request_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(request.to_dict(), f, indent=2)
    
    def _display_approval_request(self, request: HITLApprovalRequest):
        """Display approval request to user"""
        print("\n" + "=" * 70)
        print("🔔 APPROVAL REQUIRED - High-Risk Skill Detected")
        print("=" * 70)
        print(f"\nRequest ID: {request.request_id}")
        print(f"Skill: {request.skill_to_invoke}")
        print(f"Risk Level: {request.risk_level.upper()}")
        print(f"\nTriggered by:")
        print(f"  {request.trigger_event.get('matched_line', 'N/A')}")
        print(f"\nRisk Assessment:")
        print(f"  {request.risk_assessment.get('description', 'N/A')}")
        print(f"\nPotential Impact:")
        for impact in request.risk_assessment.get("potential_impact", []):
            print(f"  - {impact}")
        print(f"\nRecommendation: {request.recommended_action.upper()}")
        print(f"Reasoning: {request.reasoning}")
        print(f"\nExpires at: {request.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Auto-approve on timeout: {request.auto_approve_on_timeout}")
        
        print("\n" + "-" * 70)
        print("To approve this request, run:")
        print(f"  python scripts/dispatcher_cli.py approve {request.request_id}")
        print("\nTo reject this request, run:")
        print(f"  python scripts/dispatcher_cli.py reject {request.request_id}")
        print("=" * 70 + "\n")
    
    def check_approval_status(self, request_id: str) -> Optional[str]:
        """
        Check the status of an approval request
        
        Args:
            request_id: The approval request ID
            
        Returns:
            Status string: "approved", "rejected", "pending", "timeout", or None if not found
        """
        filepath = self.approval_dir / f"pending_{request_id}.json"
        
        if not filepath.exists():
            # Check if it was processed
            processed_path = self.approval_dir / f"processed_{request_id}.json"
            if processed_path.exists():
                with open(processed_path, 'r') as f:
                    data = json.load(f)
                    return data.get("status", "unknown")
            return None
        
        # Load request
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        status = data.get("status", "pending")
        
        # Check for timeout
        if status == "pending":
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                # Request has timed out
                auto_approve = data.get("auto_approve_on_timeout", False)
                new_status = "approved" if auto_approve else "timeout"
                
                # Update status
                data["status"] = new_status
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.info(
                    f"Approval request {request_id} timed out -> {new_status}"
                )
                
                return new_status
        
        return status
    
    def approve_request(
        self,
        request_id: str,
        user_identity: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Approve an approval request
        
        Args:
            request_id: The approval request ID
            user_identity: User who is approving
            comment: Optional comment
            
        Returns:
            True if approval successful, False otherwise
        """
        filepath = self.approval_dir / f"pending_{request_id}.json"
        
        if not filepath.exists():
            self.logger.error(f"Approval request not found: {request_id}")
            return False
        
        # Load and update request
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        data["status"] = "approved"
        data["approved_by"] = user_identity
        data["approval_timestamp"] = datetime.now().isoformat()
        data["user_comment"] = comment
        
        # Save updated request
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(
            f"Approval request {request_id} approved by {user_identity}"
        )
        
        return True
    
    def reject_request(
        self,
        request_id: str,
        user_identity: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Reject an approval request
        
        Args:
            request_id: The approval request ID
            user_identity: User who is rejecting
            reason: Optional reason for rejection
            
        Returns:
            True if rejection successful, False otherwise
        """
        filepath = self.approval_dir / f"pending_{request_id}.json"
        
        if not filepath.exists():
            self.logger.error(f"Approval request not found: {request_id}")
            return False
        
        # Load and update request
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        data["status"] = "rejected"
        data["approved_by"] = user_identity
        data["approval_timestamp"] = datetime.now().isoformat()
        data["user_comment"] = reason
        
        # Save updated request
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(
            f"Approval request {request_id} rejected by {user_identity}: {reason}"
        )
        
        return True
    
    def cleanup_processed_requests(self, age_hours: int = 24):
        """
        Clean up processed approval requests older than specified age
        
        Args:
            age_hours: Age threshold in hours
        """
        threshold = datetime.now() - timedelta(hours=age_hours)
        
        for filepath in self.approval_dir.glob("pending_*.json"):
            try:
                # Load request
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Check if processed
                status = data.get("status", "pending")
                if status in ("approved", "rejected", "timeout"):
                    # Check age
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    if timestamp < threshold:
                        # Move to processed
                        processed_path = filepath.parent / f"processed_{filepath.name[8:]}"
                        filepath.rename(processed_path)
                        self.logger.info(f"Archived processed request: {filepath.name}")
                        
            except Exception as e:
                self.logger.error(f"Failed to process {filepath.name}: {e}")
    
    def list_pending_requests(self) -> List[Dict[str, Any]]:
        """
        Get list of all pending approval requests
        
        Returns:
            List of pending request dictionaries
        """
        pending_requests = []
        
        for filepath in self.approval_dir.glob("pending_*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if data.get("status") == "pending":
                    pending_requests.append(data)
                    
            except Exception as e:
                self.logger.error(f"Failed to read {filepath.name}: {e}")
        
        return pending_requests
