"""
Updated execution logger using the enhanced audit logger
"""

import logging
from typing import Optional
import json
from datetime import datetime

from .audit_logger import AuditLogger


class ExecutionLogger:
    """
    Updated execution logger that uses enhanced audit logging capabilities
    """
    
    def __init__(
        self,
        log_dir: str = "logs/dispatcher",
        retention_days: int = 90,
        critical_retention_days: int = 365,
        max_file_size_mb: int = 100
    ):
        # Initialize the enhanced audit logger
        self.audit_logger = AuditLogger(
            log_dir=log_dir,
            retention_days=retention_days,
            critical_retention_days=critical_retention_days,
            max_file_size_mb=max_file_size_mb
        )
        
        # Keep reference to underlying logger for direct access
        self.logger = self.audit_logger.logger
    
    def log_dispatch(
        self,
        trigger_event: str,
        skill_name: str,
        result_status: str,
        execution_time: float,
        user_identity: Optional[str] = None,
        **kwargs
    ):
        """
        Log a skill dispatch event
        
        Args:
            trigger_event: Description of the triggering event
            skill_name: Name of the skill that was dispatched
            result_status: Status of the execution (success, failure, pending)
            execution_time: Time taken in seconds
            user_identity: User who triggered/approved (if applicable)
            **kwargs: Additional fields to log
        """
        self.audit_logger.log_skill_dispatch(
            trigger_event=trigger_event,
            skill_name=skill_name,
            result_status=result_status,
            execution_time=execution_time,
            user_identity=user_identity,
            **kwargs
        )
    
    def log_approval(
        self,
        request_id: str,
        skill_name: str,
        decision: str,
        user_identity: str,
        reason: Optional[str] = None
    ):
        """
        Log a HITL approval decision (critical event - 365-day retention)
        
        Args:
            request_id: Unique approval request ID
            skill_name: Name of the skill requiring approval
            decision: approved or rejected
            user_identity: User who made the decision
            reason: Optional reason for the decision
        """
        self.audit_logger.log_approval(
            request_id=request_id,
            skill_name=skill_name,
            decision=decision,
            user_identity=user_identity,
            reason=reason
        )
    
    def log_kill_switch(
        self,
        action: str,
        user_identity: str,
        reason: Optional[str] = None
    ):
        """
        Log a kill-switch event (critical event - 365-day retention)
        
        Args:
            action: activate or deactivate
            user_identity: User who triggered the kill-switch
            reason: Optional reason for activation
        """
        self.audit_logger.log_kill_switch(
            action=action,
            user_identity=user_identity,
            reason=reason
        )
    
    def log_depth_limit(
        self,
        skill_name: str,
        current_depth: int,
        max_depth: int,
        execution_chain: list
    ):
        """
        Log a depth limit violation
        
        Args:
            skill_name: Name of the skill that was rejected
            current_depth: Current execution depth
            max_depth: Maximum allowed depth
            execution_chain: List of parent skills in the chain
        """
        self.audit_logger.log_depth_limit(
            skill_name=skill_name,
            current_depth=current_depth,
            max_depth=max_depth,
            execution_chain=execution_chain
        )
    
    def log_unauthorized(
        self,
        skill_name: str,
        reason: str,
        user_identity: Optional[str] = None
    ):
        """
        Log an unauthorized skill execution attempt
        
        Args:
            skill_name: Name of the skill that was attempted
            reason: Reason for rejection (not in allowlist, etc.)
            user_identity: User who attempted (if known)
        """
        self.audit_logger.log_unauthorized(
            skill_name=skill_name,
            reason=reason,
            user_identity=user_identity
        )
    
    def compress_old_logs(self, days_threshold: int = 7):
        """
        Compress log files older than the threshold
        
        Args:
            days_threshold: Age in days after which to compress logs
        """
        self.audit_logger.compress_old_logs(days_threshold)
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        self.audit_logger.cleanup_old_logs()
    
    def get_log_statistics(self):
        """Get statistics about the log files"""
        return self.audit_logger.get_log_statistics()
    
    def rotate_logs_immediately(self):
        """Force immediate rotation of the current log file"""
        self.audit_logger.rotate_logs_immediately()
