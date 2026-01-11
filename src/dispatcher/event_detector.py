"""
Event Detector (T019 - User Story 1)

Monitors log files for error patterns and triggers skill dispatch.
Integrates with EventHasher for deduplication and Debouncer for suppression.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from queue import Queue, Empty

from .models import EventTrigger, RiskLevel
from .config_manager import ConfigManager
from .event_hasher import EventHasher
from .debouncer import Debouncer
from .regex_validator import RegexValidator
from .exceptions import ValidationError


class EventDetector:
    """
    Detects events based on pattern matching and queues them for processing.

    Integrates deduplication (EventHasher) and debouncing (Debouncer).
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        debounce_window: int = 30
    ):
        """
        Initialize event detector.

        Args:
            config_manager: Configuration manager for loading triggers
            debounce_window: Debounce window in seconds
        """
        self.config = config_manager
        self.triggers = config_manager.get_event_triggers()

        # Initialize deduplication and debouncing
        self.hasher = EventHasher(time_window_seconds=debounce_window)
        self.debouncer = Debouncer(window_seconds=debounce_window)

        # Regex validator for pattern safety
        self.validator = RegexValidator()

        # Event queue for async processing
        self.event_queue: Queue = Queue()

        # Compile patterns for performance
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        for trigger in self.triggers:
            if not trigger.enabled:
                continue

            # Validate pattern
            is_valid, error_msg = self.validator.validate(trigger.pattern)
            if not is_valid:
                print(f"⚠️  Skipping invalid pattern: {error_msg}")
                continue

            try:
                self._compiled_patterns[trigger.pattern] = re.compile(trigger.pattern)
            except re.error as e:
                print(f"⚠️  Failed to compile pattern '{trigger.pattern}': {e}")

    def detect_events(self, log_content: str) -> List[EventTrigger]:
        """
        Detect events in log content.

        Args:
            log_content: Content to scan for patterns

        Returns:
            List of triggered events
        """
        triggered_events = []

        for trigger in self.triggers:
            if not trigger.enabled:
                continue

            # Get compiled pattern
            pattern = self._compiled_patterns.get(trigger.pattern)
            if not pattern:
                continue

            # Check for matches
            if pattern.search(log_content):
                # Check deduplication
                event_data = f"{trigger.event_type}:{trigger.pattern}:{log_content[:200]}"
                if self.hasher.is_duplicate(event_data):
                    continue

                # Check debouncing
                event_key = f"{trigger.skill_to_invoke}:{trigger.event_type}"
                if not self.debouncer.should_process(event_key):
                    continue

                # Verify skill is allowed
                if not self.config.is_skill_allowed(trigger.skill_to_invoke):
                    print(f"⚠️  Skill '{trigger.skill_to_invoke}' not in allowlist - skipping")
                    continue

                # Event should be processed
                triggered_events.append(trigger)

                # Mark as processed
                self.hasher.mark_processed(event_data)

        return triggered_events

    def queue_event(self, trigger: EventTrigger, context: Dict[str, Any]) -> None:
        """
        Queue event for processing.

        Args:
            trigger: Event trigger that fired
            context: Additional context about the event
        """
        self.event_queue.put({
            "trigger": trigger,
            "context": context,
            "timestamp": self.hasher.mark_processed(
                f"{trigger.event_type}:{trigger.skill_to_invoke}"
            )
        })

    def get_queued_event(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Get next queued event.

        Args:
            timeout: Timeout in seconds

        Returns:
            Event dict or None if queue empty
        """
        try:
            return self.event_queue.get(timeout=timeout)
        except Empty:
            return None

    def scan_file(self, file_path: Path) -> List[EventTrigger]:
        """
        Scan a file for error patterns.

        Args:
            file_path: Path to file to scan

        Returns:
            List of triggered events
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self.detect_events(content)
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
            return []

    def reload_triggers(self) -> None:
        """Reload event triggers from config."""
        self.config.reload()
        self.triggers = self.config.get_event_triggers()
        self._compiled_patterns.clear()
        self._compile_patterns()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get detector statistics.

        Returns:
            Stats dict
        """
        return {
            "triggers_loaded": len(self.triggers),
            "triggers_enabled": sum(1 for t in self.triggers if t.enabled),
            "patterns_compiled": len(self._compiled_patterns),
            "queued_events": self.event_queue.qsize(),
            "hasher_cache_size": self.hasher.get_cache_size(),
            "debouncer_cache_size": self.debouncer.get_cache_size()
        }
