"""
Pattern debouncer with time-window caching to prevent rapid-fire triggers
"""

import time
from typing import Dict, Tuple, Optional
from functools import lru_cache
import threading


class Debouncer:
    """
    Prevents duplicate skill execution within a configurable time window
    
    Uses LRU cache with time-based expiration to suppress rapid repeated triggers
    """
    
    def __init__(
        self,
        time_window_seconds: int = 30,
        cache_size_limit: int = 1000
    ):
        self.time_window = time_window_seconds
        self.cache_size_limit = cache_size_limit
        
        # Cache: (pattern_id, content_hash) -> timestamp of last trigger
        self._cache: Dict[Tuple[str, str], float] = {}
        self._lock = threading.Lock()
    
    def should_suppress(
        self,
        pattern_id: str,
        content_hash: str,
        debounce_seconds: Optional[int] = None
    ) -> bool:
        """
        Check if an event should be suppressed based on debounce window
        
        Args:
            pattern_id: ID of the trigger pattern
            content_hash: Hash of the event content
            debounce_seconds: Override default time window for this event
            
        Returns:
            True if event should be suppressed, False if it should trigger
        """
        with self._lock:
            current_time = time.time()
            cache_key = (pattern_id, content_hash)
            
            # Check if we've seen this event recently
            if cache_key in self._cache:
                last_trigger_time = self._cache[cache_key]
                time_window = debounce_seconds or self.time_window
                
                # Check if still within debounce window
                if current_time - last_trigger_time < time_window:
                    return True  # Suppress - too soon
            
            # Update cache with current timestamp
            self._cache[cache_key] = current_time
            
            # Cleanup old entries if cache is getting large
            if len(self._cache) > self.cache_size_limit:
                self._cleanup_old_entries()
            
            return False  # Allow trigger
    
    def _cleanup_old_entries(self):
        """Remove entries older than the time window (internal, must hold lock)"""
        current_time = time.time()
        
        # Find keys to remove
        keys_to_remove = [
            key for key, timestamp in self._cache.items()
            if current_time - timestamp > self.time_window * 2  # Keep 2x window
        ]
        
        # Remove old entries
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear(self):
        """Clear all cached entries (for testing)"""
        with self._lock:
            self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)
    
    def is_in_window(self, pattern_id: str, content_hash: str) -> bool:
        """
        Check if an event is within the debounce window (without updating cache)
        
        Args:
            pattern_id: ID of the trigger pattern
            content_hash: Hash of the event content
            
        Returns:
            True if event is within debounce window, False otherwise
        """
        with self._lock:
            cache_key = (pattern_id, content_hash)
            if cache_key not in self._cache:
                return False
            
            current_time = time.time()
            last_trigger_time = self._cache[cache_key]
            return current_time - last_trigger_time < self.time_window
