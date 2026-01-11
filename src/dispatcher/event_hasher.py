"""
Event hashing and deduplication for concurrent event handling
"""

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Set, Optional

from .lock_manager import LockManager


class EventHasher:
    """
    Generates SHA256 hashes for events and maintains a set of currently processing events
    to prevent duplicate processing
    """
    
    def __init__(
        self,
        state_file: str = ".state/processing_hashes.json",
        time_window: int = 5
    ):
        self.state_file = Path(state_file)
        self.time_window = time_window  # Round timestamps to this many seconds
        self.processing_hashes: Set[str] = set()
        self.lock = threading.Lock()
        self.lock_manager = LockManager()
        
        # Ensure state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load persisted state
        self._load_state()
    
    def _load_state(self):
        """Load persisted hash set from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.processing_hashes = set(data.get("hashes", []))
            except Exception:
                # If load fails, start fresh
                self.processing_hashes = set()
    
    def _persist_state(self):
        """Persist hash set to disk"""
        try:
            data = {"hashes": list(self.processing_hashes)}
            with open(self.state_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass  # Best effort
    
    def generate_hash(self, pattern_id: str, log_content: str) -> str:
        """
        Generate a SHA256 hash for an event
        
        Args:
            pattern_id: ID of the trigger pattern
            log_content: Content that matched the pattern
            
        Returns:
            SHA256 hash string
        """
        # Round timestamp to time window
        timestamp_window = int(time.time() / self.time_window) * self.time_window
        
        # Create hash input
        hash_input = f"{pattern_id}:{log_content}:{timestamp_window}"
        
        # Generate SHA256 hash
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def is_duplicate(self, event_hash: str) -> bool:
        """
        Check if an event is currently being processed
        
        Args:
            event_hash: Hash of the event to check
            
        Returns:
            True if event is already being processed, False otherwise
        """
        with self.lock:
            return event_hash in self.processing_hashes
    
    def mark_processing(self, event_hash: str):
        """
        Mark an event as being processed
        
        Args:
            event_hash: Hash of the event to mark
        """
        with self.lock:
            self.processing_hashes.add(event_hash)
            self._persist_state()
    
    def mark_completed(self, event_hash: str):
        """
        Remove an event from the processing set
        
        Args:
            event_hash: Hash of the event to remove
        """
        with self.lock:
            self.processing_hashes.discard(event_hash)
            self._persist_state()
    
    def cleanup_old_hashes(self, max_age_seconds: int = 300):
        """
        Clean up hashes that have been in the set for too long
        
        This is a safety mechanism to prevent unbounded growth if mark_completed
        is not called due to crashes or errors.
        
        Args:
            max_age_seconds: Maximum age for hashes in seconds
        """
        # For Phase 1, we simply clear all hashes periodically
        # In Phase 2, we could add timestamps to track hash age
        with self.lock:
            # Only clear if set is getting large
            if len(self.processing_hashes) > 1000:
                self.processing_hashes.clear()
                self._persist_state()
    
    def get_processing_count(self) -> int:
        """
        Get the count of currently processing events
        
        Returns:
            Number of events currently being processed
        """
        with self.lock:
            return len(self.processing_hashes)
