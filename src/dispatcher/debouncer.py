"""
Debouncer (T020 - User Story 1)

Suppresses duplicate events within a 30-second time window.
Prevents event spam from triggering multiple skill dispatches.
"""

import time
from collections import OrderedDict
from typing import Dict, Tuple


class Debouncer:
    """
    Time-window based event debouncing.

    Uses LRU cache to suppress duplicate events within configurable time window.
    """

    def __init__(self, window_seconds: int = 30, max_cache_size: int = 1000):
        """
        Initialize debouncer.

        Args:
            window_seconds: Time window for debouncing (default: 30s)
            max_cache_size: Maximum cached events
        """
        self.window_seconds = window_seconds
        self.max_cache_size = max_cache_size

        # Cache: event_key -> (timestamp, count)
        self._cache: OrderedDict[str, Tuple[float, int]] = OrderedDict()

    def should_process(self, event_key: str) -> bool:
        """
        Check if event should be processed or debounced.

        Args:
            event_key: Unique key for the event

        Returns:
            True if event should be processed, False if debounced
        """
        current_time = time.time()

        # Clean up expired entries
        self._cleanup_expired(current_time)

        # Check if event exists in cache
        if event_key in self._cache:
            cached_time, count = self._cache[event_key]

            # Check if within debounce window
            if current_time - cached_time <= self.window_seconds:
                # Still within window - debounce (don't process)
                # Update count and timestamp
                self._cache[event_key] = (current_time, count + 1)
                self._cache.move_to_end(event_key)
                return False

            # Window expired - process and reset
            self._cache[event_key] = (current_time, 1)
            self._cache.move_to_end(event_key)
            return True

        # New event - add to cache and process
        self._cache[event_key] = (current_time, 1)

        # Enforce max cache size (LRU eviction)
        if len(self._cache) > self.max_cache_size:
            self._cache.popitem(last=False)

        return True

    def _cleanup_expired(self, current_time: float) -> None:
        """
        Remove expired entries from cache.

        Args:
            current_time: Current timestamp
        """
        expired_keys = []
        for event_key, (cached_time, _) in self._cache.items():
            if current_time - cached_time > self.window_seconds:
                expired_keys.append(event_key)
            else:
                # OrderedDict maintains insertion order
                # Once we hit non-expired, rest are also non-expired
                break

        for key in expired_keys:
            del self._cache[key]

    def get_event_count(self, event_key: str) -> int:
        """
        Get number of times event was seen within current window.

        Args:
            event_key: Event key to check

        Returns:
            Count of events (0 if not in cache or expired)
        """
        current_time = time.time()

        if event_key in self._cache:
            cached_time, count = self._cache[event_key]
            if current_time - cached_time <= self.window_seconds:
                return count

        return 0

    def clear(self) -> None:
        """Clear all cached events."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
