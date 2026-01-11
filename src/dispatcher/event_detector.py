"""
Event detector that monitors logs and triggers skills based on pattern matching
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .models import EventTrigger
from .config_manager import ConfigManager
from .regex_validator import RegexValidator
from .debouncer import Debouncer
from .event_hasher import EventHasher
from .exceptions import InvalidPatternError, SkillNotAllowedError


class EventDetector:
    """
    Detects events in log files and queues skill executions based on configured patterns
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        debouncer: Debouncer,
        event_hasher: EventHasher,
        logger: Optional[logging.Logger] = None
    ):
        self.config_manager = config_manager
        self.debouncer = debouncer
        self.event_hasher = event_hasher
        self.logger = logger or logging.getLogger(__name__)
        
        # Compiled patterns cache
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        
        # Load and compile patterns
        self._load_patterns()
    
    def _load_patterns(self):
        """Load and compile regex patterns from configuration"""
        triggers = self.config_manager.event_triggers
        
        for trigger in triggers:
            if not trigger.get("enabled", True):
                continue
            
            pattern_str = trigger["pattern"]
            trigger_id = trigger["id"]
            
            try:
                # Validate pattern for safety (ReDoS prevention)
                RegexValidator.validate(pattern_str)
                
                # Compile pattern
                compiled = re.compile(pattern_str, re.IGNORECASE)
                self._compiled_patterns[trigger_id] = compiled
                
                self.logger.info(f"Loaded pattern: {trigger_id} -> {pattern_str}")
                
            except InvalidPatternError as e:
                self.logger.error(f"Invalid pattern for trigger '{trigger_id}': {e}")
                # Skip this pattern
            except re.error as e:
                self.logger.error(f"Failed to compile pattern for trigger '{trigger_id}': {e}")
    
    def detect_events(self, log_line: str, source_file: str = "") -> List[Dict[str, Any]]:
        """
        Detect events in a log line and return list of skill dispatch requests
        
        Args:
            log_line: The log line to check for patterns
            source_file: Optional source file path for context
            
        Returns:
            List of dispatch request dictionaries
        """
        dispatch_requests = []
        triggers = self.config_manager.event_triggers
        
        # Sort triggers by priority (lower number = higher priority)
        sorted_triggers = sorted(
            [t for t in triggers if t.get("enabled", True)],
            key=lambda t: t.get("priority", 10)
        )
        
        for trigger in sorted_triggers:
            trigger_id = trigger["id"]
            
            # Skip if pattern didn't compile
            if trigger_id not in self._compiled_patterns:
                continue
            
            pattern = self._compiled_patterns[trigger_id]
            
            # Check if pattern matches
            match = pattern.search(log_line)
            if not match:
                continue
            
            # Pattern matched - create dispatch request
            skill_name = trigger["skill_to_invoke"]
            
            # Check if skill is in allowlist
            if not self.config_manager.is_skill_allowed(skill_name):
                self.logger.warning(
                    f"Skill '{skill_name}' triggered by pattern '{trigger_id}' "
                    f"but not in allowlist - rejecting"
                )
                continue
            
            # Generate event hash for deduplication
            event_hash = self.event_hasher.generate_hash(trigger_id, log_line)
            
            # Check if this event is already being processed
            if self.event_hasher.is_duplicate(event_hash):
                self.logger.debug(
                    f"Event already being processed (hash: {event_hash[:16]}...) - skipping"
                )
                continue
            
            # Check debounce window
            debounce_seconds = trigger.get("debounce_seconds", 30)
            if self.debouncer.should_suppress(trigger_id, event_hash, debounce_seconds):
                self.logger.info(
                    f"Event suppressed by debouncer: {trigger_id} "
                    f"(within {debounce_seconds}s window)"
                )
                continue
            
            # Mark event as processing
            self.event_hasher.mark_processing(event_hash)
            
            # Create dispatch request
            dispatch_request = {
                "trigger_id": trigger_id,
                "trigger_name": trigger["name"],
                "event_type": trigger["event_type"],
                "skill_name": skill_name,
                "risk_level": trigger.get("risk_level", "medium"),
                "requires_approval": trigger.get("requires_approval", False),
                "event_hash": event_hash,
                "trigger_event": {
                    "source_file": source_file,
                    "matched_line": log_line,
                    "pattern": trigger["pattern"],
                    "match_position": match.start(),
                    "matched_text": match.group(0)
                },
                "priority": trigger.get("priority", 10)
            }
            
            dispatch_requests.append(dispatch_request)
            
            self.logger.info(
                f"Event detected: {trigger_id} -> {skill_name} "
                f"(risk: {trigger.get('risk_level', 'medium')})"
            )
        
        return dispatch_requests
    
    def reload_patterns(self):
        """Reload patterns from configuration (for hot reload)"""
        self.logger.info("Reloading event patterns...")
        self._compiled_patterns.clear()
        self.config_manager.reload_all()
        self._load_patterns()
        self.logger.info(f"Loaded {len(self._compiled_patterns)} active patterns")
    
    def get_active_patterns(self) -> List[str]:
        """Get list of active pattern IDs"""
        return list(self._compiled_patterns.keys())
