"""
Enhanced audit logger with 90-day retention, rotation, and comprehensive audit trails
"""

import logging
import logging.handlers
import gzip
import os
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import atexit
import threading
import queue
import time


class AuditLogger:
    """
    Comprehensive audit logger with 90-day retention, daily rotation, and audit trails
    """
    
    def __init__(
        self,
        log_dir: str = "logs/dispatcher",
        retention_days: int = 90,
        critical_retention_days: int = 365,
        max_file_size_mb: int = 100,
        compression_enabled: bool = True,
        compression_age_days: int = 7
    ):
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.critical_retention_days = critical_retention_days
        self.max_file_size_mb = max_file_size_mb
        self.compression_enabled = compression_enabled
        self.compression_age_days = compression_age_days
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("dispatcher.audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add rotating file handler
        self._setup_file_handler()
        
        # Add console handler
        self._setup_console_handler()
        
        # Start background cleanup thread
        self._start_cleanup_thread()
        
        # Register cleanup on exit
        atexit.register(self._cleanup_on_exit)
    
    def _setup_file_handler(self):
        """Setup daily rotating file handler with audit format"""
        # Create log filename with date
        today = datetime.now().strftime('%Y-%m-%d')
        log_filename = self.log_dir / f"dispatcher-audit-{today}.log"
        
        # Create rotating file handler (rotates at midnight)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_filename,
            when='midnight',
            interval=1,
            backupCount=self.retention_days
        )
        
        # Set audit-specific format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def _setup_console_handler(self):
        """Setup console handler for immediate feedback"""
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(levelname)-8s | %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def _start_cleanup_thread(self):
        """Start background thread for log cleanup"""
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background worker for log cleanup"""
        while True:
            try:
                # Clean up old logs daily
                self.cleanup_old_logs()
                
                # Compress old logs
                if self.compression_enabled:
                    self.compress_old_logs()
                
                # Sleep for 24 hours
                time.sleep(24 * 3600)
            except Exception as e:
                self.logger.error(f"Error in cleanup worker: {e}")
                time.sleep(3600)  # Retry in 1 hour on error
    
    def _cleanup_on_exit(self):
        """Cleanup function called on program exit"""
        try:
            self.cleanup_old_logs()
            if self.compression_enabled:
                self.compress_old_logs()
        except Exception as e:
            self.logger.error(f"Error during cleanup on exit: {e}")
    
    def log_skill_dispatch(
        self,
        trigger_event: str,
        skill_name: str,
        result_status: str,
        execution_time: float,
        user_identity: Optional[str] = None,
        **kwargs
    ):
        """
        Log a skill dispatch event with audit trail
        
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
            "log_version": "1.0",
            **kwargs
        }
        
        self.logger.info(f"DISPATCH: {json.dumps(log_entry)}")
    
    def log_approval(
        self,
        request_id: str,
        skill_name: str,
        decision: str,
        user_identity: str,
        reason: Optional[str] = None,
        risk_level: str = "unknown"
    ):
        """
        Log a HITL approval decision (critical event - 365-day retention)
        
        Args:
            request_id: Unique approval request ID
            skill_name: Name of the skill requiring approval
            decision: approved or rejected
            user_identity: User who made the decision
            reason: Optional reason for the decision
            risk_level: Risk level of the skill
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "hitl_approval",
            "request_id": request_id,
            "skill_name": skill_name,
            "decision": decision,
            "user_identity": user_identity,
            "reason": reason,
            "risk_level": risk_level,
            "log_version": "1.0"
        }
        
        # Log to regular log
        self.logger.critical(f"APPROVAL: {json.dumps(log_entry)}")
        
        # Also archive to critical log
        self._archive_critical_event(log_entry)
    
    def log_kill_switch(
        self,
        action: str,
        user_identity: str,
        reason: Optional[str] = None,
        skill_count_affected: int = 0
    ):
        """
        Log a kill-switch event (critical event - 365-day retention)
        
        Args:
            action: activate or deactivate
            user_identity: User who triggered the kill-switch
            reason: Optional reason for activation
            skill_count_affected: Number of skills affected by the action
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "kill_switch",
            "action": action,
            "user_identity": user_identity,
            "reason": reason,
            "skill_count_affected": skill_count_affected,
            "log_version": "1.0"
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
        Log a depth limit violation (security event)
        
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
            "execution_chain": execution_chain,
            "log_version": "1.0"
        }
        
        self.logger.warning(f"DEPTH_LIMIT: {json.dumps(log_entry)}")
    
    def log_unauthorized(
        self,
        skill_name: str,
        reason: str,
        user_identity: Optional[str] = None,
        source_ip: Optional[str] = None
    ):
        """
        Log an unauthorized skill execution attempt (security event)
        
        Args:
            skill_name: Name of the skill that was attempted
            reason: Reason for rejection (not in allowlist, etc.)
            user_identity: User who attempted (if known)
            source_ip: Source IP address (if known)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "unauthorized_attempt",
            "skill_name": skill_name,
            "reason": reason,
            "user_identity": user_identity or "unknown",
            "source_ip": source_ip,
            "log_version": "1.0"
        }
        
        self.logger.warning(f"UNAUTHORIZED: {json.dumps(log_entry)}")
    
    def log_security_scan(
        self,
        scan_type: str,
        findings_count: int,
        severity_level: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a security scan event
        
        Args:
            scan_type: Type of security scan performed
            findings_count: Number of security findings
            severity_level: Severity level of findings
            details: Additional scan details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_scan",
            "scan_type": scan_type,
            "findings_count": findings_count,
            "severity_level": severity_level,
            "details": details or {},
            "log_version": "1.0"
        }
        
        self.logger.info(f"SECURITY_SCAN: {json.dumps(log_entry)}")
    
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
    
    def compress_old_logs(self, days_threshold: Optional[int] = None):
        """
        Compress log files older than the threshold
        
        Args:
            days_threshold: Age in days after which to compress logs (defaults to compression_age_days)
        """
        if not self.compression_enabled:
            return
            
        threshold_days = days_threshold or self.compression_age_days
        threshold_date = datetime.now() - timedelta(days=threshold_days)
        
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
        
        # Clean up standard log files
        for log_file in self.log_dir.glob("*.log*"):
            # Handle critical events log separately
            if log_file.name == "critical_events.log":
                self._cleanup_critical_log(log_file, critical_threshold)
                continue
            
            # Skip compressed files when checking standard threshold
            if log_file.name.endswith('.gz'):
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
            temp_entries = []
            with open(log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            temp_entries.append(entry)
                        except json.JSONDecodeError:
                            continue  # Skip invalid lines
            
            # Filter entries newer than threshold
            filtered_entries = [
                entry for entry in temp_entries
                if datetime.fromisoformat(entry["timestamp"]) >= threshold
            ]
            
            # Write back filtered entries
            with open(log_file, 'w') as f:
                for entry in filtered_entries:
                    f.write(json.dumps(entry) + '\n')
            
            removed_count = len(temp_entries) - len(filtered_entries)
            self.logger.info(
                f"Cleaned critical log: removed {removed_count} old entries, kept {len(filtered_entries)}"
            )
        except Exception as e:
            self.logger.error(f"Failed to clean critical log: {e}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the log files
        
        Returns:
            Dictionary with log statistics
        """
        stats = {
            "total_log_files": 0,
            "total_size_mb": 0,
            "oldest_log_date": None,
            "newest_log_date": None,
            "log_files": []
        }
        
        for log_file in self.log_dir.glob("*"):
            if log_file.is_file() and (log_file.name.endswith('.log') or log_file.name.endswith('.gz')):
                file_stat = log_file.stat()
                file_info = {
                    "name": log_file.name,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                }
                
                stats["log_files"].append(file_info)
                stats["total_log_files"] += 1
                stats["total_size_mb"] += file_info["size_mb"]
                
                # Track date range
                file_date = datetime.fromtimestamp(file_stat.st_mtime)
                if stats["oldest_log_date"] is None or file_date < stats["oldest_log_date"]:
                    stats["oldest_log_date"] = file_date
                if stats["newest_log_date"] is None or file_date > stats["newest_log_date"]:
                    stats["newest_log_date"] = file_date
        
        if stats["oldest_log_date"]:
            stats["oldest_log_date"] = stats["oldest_log_date"].isoformat()
        if stats["newest_log_date"]:
            stats["newest_log_date"] = stats["newest_log_date"].isoformat()
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        return stats
    
    def rotate_logs_immediately(self):
        """Force immediate rotation of the current log file"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
                handler.doRollover()
                self.logger.info("Log rotation performed immediately")
                break
