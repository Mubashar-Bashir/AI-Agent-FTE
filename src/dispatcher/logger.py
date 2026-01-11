"""
Execution logger with 90-day retention, daily rotation, and compression
"""

import logging
import logging.handlers
import gzip
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import json


class ExecutionLogger:
    """
    Manages logging for all dispatcher activities with configurable retention
    """
    
    def __init__(
        self,
        log_dir: str = "logs/dispatcher",
        retention_days: int = 90,
        critical_retention_days: int = 365,
        max_file_size_mb: int = 100
    ):
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.critical_retention_days = critical_retention_days
        self.max_file_size_mb = max_file_size_mb
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("dispatcher")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add rotating file handler
        self._setup_file_handler()
        
        # Add console handler
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """Setup daily rotating file handler"""
        log_filename = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        
        # Create rotating file handler (rotates at midnight)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_filename,
            when='midnight',
            interval=1,
            backupCount=self.retention_days
        )
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def _setup_console_handler(self):
        """Setup console handler for immediate feedback"""
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
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
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "skill_dispatch",
            "trigger_event": trigger_event,
            "skill_name": skill_name,
            "result_status": result_status,
            "execution_time": execution_time,
            "user_identity": user_identity or "system",
            **kwargs
        }
        
        self.logger.info(f"DISPATCH: {json.dumps(log_entry)}")
    
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
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "hitl_approval",
            "request_id": request_id,
            "skill_name": skill_name,
            "decision": decision,
            "user_identity": user_identity,
            "reason": reason
        }
        
        # Log to regular log
        self.logger.critical(f"APPROVAL: {json.dumps(log_entry)}")
        
        # Also archive to critical log
        self._archive_critical_event(log_entry)
    
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
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "kill_switch",
            "action": action,
            "user_identity": user_identity,
            "reason": reason
        }
        
        # Log to regular log
        self.logger.critical(f"KILL_SWITCH: {json.dumps(log_entry)}")
        
        # Also archive to critical log
        self._archive_critical_event(log_entry)
    
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
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "depth_limit_violation",
            "skill_name": skill_name,
            "current_depth": current_depth,
            "max_depth": max_depth,
            "execution_chain": execution_chain
        }
        
        self.logger.warning(f"DEPTH_LIMIT: {json.dumps(log_entry)}")
    
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
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "unauthorized_attempt",
            "skill_name": skill_name,
            "reason": reason,
            "user_identity": user_identity or "unknown"
        }
        
        self.logger.warning(f"UNAUTHORIZED: {json.dumps(log_entry)}")
    
    def _archive_critical_event(self, log_entry: dict):
        """
        Archive a critical event to a separate file with extended retention
        
        Args:
            log_entry: Log entry dictionary
        """
        critical_log_file = self.log_dir / "critical_events.log"
        
        try:
            with open(critical_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to archive critical event: {e}")
    
    def compress_old_logs(self, days_threshold: int = 7):
        """
        Compress log files older than the threshold
        
        Args:
            days_threshold: Age in days after which to compress logs
        """
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        for log_file in self.log_dir.glob("*.log"):
            # Skip critical events log
            if log_file.name == "critical_events.log":
                continue
            
            # Check file age
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < threshold_date and not log_file.name.endswith('.gz'):
                try:
                    # Compress the file
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original file
                    log_file.unlink()
                    self.logger.info(f"Compressed old log: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to compress {log_file.name}: {e}")
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        standard_threshold = datetime.now() - timedelta(days=self.retention_days)
        critical_threshold = datetime.now() - timedelta(days=self.critical_retention_days)
        
        for log_file in self.log_dir.glob("*.log*"):
            # Handle critical events log separately
            if log_file.name == "critical_events.log":
                self._cleanup_critical_log(log_file, critical_threshold)
                continue
            
            # Check file age
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < standard_threshold:
                try:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete {log_file.name}: {e}")
    
    def _cleanup_critical_log(self, log_file: Path, threshold: datetime):
        """
        Clean up critical events log by removing entries older than threshold
        
        Args:
            log_file: Path to the critical events log file
            threshold: DateTime threshold for deletion
        """
        try:
            # Read all entries
            with open(log_file, 'r') as f:
                entries = [json.loads(line) for line in f if line.strip()]
            
            # Filter entries newer than threshold
            filtered_entries = [
                entry for entry in entries
                if datetime.fromisoformat(entry["timestamp"]) >= threshold
            ]
            
            # Write back filtered entries
            with open(log_file, 'w') as f:
                for entry in filtered_entries:
                    f.write(json.dumps(entry) + '\n')
            
            self.logger.info(
                f"Cleaned critical log: removed {len(entries) - len(filtered_entries)} old entries"
            )
        except Exception as e:
            self.logger.error(f"Failed to clean critical log: {e}")
