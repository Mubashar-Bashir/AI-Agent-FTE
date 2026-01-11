"""
Integration module for connecting the Skill Dispatcher with the Workspace Observer
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging

from .main import DispatcherMain
from .models import EventTrigger
from .logger import ExecutionLogger


class ObserverIntegration:
    """
    Integration layer between Workspace Observer and Skill Dispatcher
    """
    
    def __init__(
        self,
        dispatcher: DispatcherMain,
        log_paths: list = None,
        poll_interval: float = 1.0,
        logger: Optional[logging.Logger] = None
    ):
        self.dispatcher = dispatcher
        self.log_paths = log_paths or [
            "logs/",  # Default log directory
            "src/",   # Source code changes
            "tests/"  # Test files
        ]
        self.poll_interval = poll_interval
        self.logger = logger or logging.getLogger(__name__)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.last_file_stats = {}
        
        # Initialize file stats for change detection
        self._initialize_file_stats()
    
    def _initialize_file_stats(self):
        """Initialize file modification times for change detection"""
        for log_path in self.log_paths:
            path = Path(log_path)
            if path.exists():
                if path.is_file():
                    self.last_file_stats[str(path)] = path.stat().st_mtime
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            self.last_file_stats[str(file_path)] = file_path.stat().st_mtime
    
    def start_monitoring(self):
        """Start monitoring for changes that might trigger skills"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Started observer integration monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring for changes"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Stopped observer integration monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop that checks for changes and processes them"""
        while self.monitoring:
            try:
                changes = self._detect_changes()
                if changes:
                    self._process_changes(changes)
                
                time.sleep(self.poll_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.poll_interval)
    
    def _detect_changes(self) -> Dict[str, Any]:
        """Detect changes in monitored files/directories"""
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": []
        }
        
        current_stats = {}
        
        for log_path in self.log_paths:
            path = Path(log_path)
            if path.exists():
                if path.is_file():
                    current_stats[str(path)] = path.stat().st_mtime
                    if str(path) not in self.last_file_stats:
                        changes["new_files"].append(str(path))
                    elif path.stat().st_mtime > self.last_file_stats[str(path)]:
                        changes["modified_files"].append(str(path))
                elif path.is_dir():
                    # Monitor all files in directory
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            current_stats[str(file_path)] = file_path.stat().st_mtime
                            if str(file_path) not in self.last_file_stats:
                                changes["new_files"].append(str(file_path))
                            elif file_path.stat().st_mtime > self.last_file_stats[str(file_path)]:
                                changes["modified_files"].append(str(file_path))
        
        # Detect deletions
        for old_path in self.last_file_stats:
            if old_path not in current_stats:
                changes["deleted_files"].append(old_path)
        
        # Update last stats
        self.last_file_stats = current_stats
        
        return changes
    
    def _process_changes(self, changes: Dict[str, Any]):
        """Process detected changes and trigger appropriate skills"""
        # Process new and modified files
        for file_path in changes["new_files"] + changes["modified_files"]:
            try:
                self._process_file_content(file_path)
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
    
    def _process_file_content(self, file_path: str):
        """Process the content of a changed file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last N lines to catch recent changes
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines  # Last 10 lines
                
                for line in recent_lines:
                    line = line.strip()
                    if line:  # Only process non-empty lines
                        # Process the line through the dispatcher
                        dispatched_count = self.dispatcher.process_log_line(line, source_file=file_path)
                        if dispatched_count > 0:
                            self.logger.info(
                                f"Triggered {dispatched_count} skills from {file_path}: {line[:100]}..."
                            )
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
    
    def trigger_skill_manually(self, skill_name: str, parameters: Dict[str, Any] = None):
        """
        Manually trigger a skill (for integration testing or direct calls)
        
        Args:
            skill_name: Name of the skill to trigger
            parameters: Optional parameters for the skill
        """
        # Create a mock dispatch request for manual triggering
        dispatch_request = {
            "trigger_id": "manual-trigger",
            "trigger_name": "Manual Trigger",
            "event_type": "manual",
            "skill_name": skill_name,
            "risk_level": "medium",  # Default risk level
            "requires_approval": True,  # Manual triggers may need approval
            "event_hash": f"manual-{int(time.time())}",
            "trigger_event": {
                "source_file": "manual",
                "matched_line": f"Manual trigger for {skill_name}",
                "pattern": "manual",
                "match_position": 0,
                "matched_text": skill_name
            },
            "priority": 50,
            "parameters": parameters or {}
        }
        
        try:
            record = self.dispatcher.skill_dispatcher.dispatch(dispatch_request)
            self.logger.info(f"Manual trigger result: {record.status}")
            return record
        except Exception as e:
            self.logger.error(f"Manual trigger failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the integration"""
        return {
            "monitoring": self.monitoring,
            "monitor_thread_alive": self.monitor_thread.is_alive() if self.monitor_thread else False,
            "tracked_paths": self.log_paths,
            "file_stats_count": len(self.last_file_stats),
            "poll_interval": self.poll_interval
        }


def integrate_with_observer(observer_callback: Callable = None):
    """
    High-level function to integrate the dispatcher with the observer system
    
    Args:
        observer_callback: Optional callback function for observer events
    """
    # Initialize dispatcher
    dispatcher = DispatcherMain()
    dispatcher.setup()
    
    # Create integration
    integration = ObserverIntegration(dispatcher)
    
    # Start monitoring
    integration.start_monitoring()
    
    # Set up callback if provided
    if observer_callback:
        # This would connect to the actual observer's event system
        pass
    
    return integration
