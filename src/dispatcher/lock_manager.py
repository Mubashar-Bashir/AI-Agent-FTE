"""
Thread-safe lock manager using file-based locking with fcntl
"""

import fcntl
import time
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from .exceptions import LockTimeoutError


class LockManager:
    """
    Manages file-based locking for atomic operations
    
    Uses fcntl for POSIX-compliant file locking that works across processes
    """
    
    def __init__(self, lock_file_path: str = "locks/dispatcher.lock"):
        self.lock_file_path = Path(lock_file_path)
        self.lock_file: Optional[int] = None
        
        # Ensure the lock directory exists
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure the lock file exists
        if not self.lock_file_path.exists():
            self.lock_file_path.touch()
    
    @contextmanager
    def acquire(self, timeout: int = 5):
        """
        Acquire an exclusive lock with timeout
        
        Args:
            timeout: Maximum time to wait for lock in seconds
            
        Raises:
            LockTimeoutError: If lock cannot be acquired within timeout
            
        Yields:
            None: Lock is held during the context
        """
        start_time = time.time()
        lock_fd = None
        
        try:
            # Open the lock file
            lock_fd = os.open(self.lock_file_path, os.O_RDWR | os.O_CREAT)
            
            # Try to acquire lock with timeout
            while True:
                try:
                    # Try non-blocking lock
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break  # Lock acquired
                except IOError:
                    # Lock is held by another process
                    if time.time() - start_time > timeout:
                        raise LockTimeoutError(
                            f"Failed to acquire lock within {timeout} seconds"
                        )
                    time.sleep(0.1)  # Wait before retrying
            
            # Lock acquired - yield control to caller
            yield
            
        finally:
            # Always release lock and close file
            if lock_fd is not None:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    os.close(lock_fd)
                except Exception:
                    pass  # Best effort cleanup
    
    def is_locked(self) -> bool:
        """
        Check if the lock is currently held (non-blocking check)
        
        Returns:
            True if lock is currently held, False otherwise
        """
        try:
            lock_fd = os.open(self.lock_file_path, os.O_RDWR)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
                return False  # Lock was available
            except IOError:
                os.close(lock_fd)
                return True  # Lock is held
        except Exception:
            return False  # Assume not locked if check fails
    
    def force_release(self):
        """
        Force release of stale locks (use with caution)
        
        This should only be used for stale lock detection and cleanup
        """
        if self.lock_file_path.exists():
            # Check file age
            file_age = time.time() - self.lock_file_path.stat().st_mtime
            if file_age > 60:  # Stale lock threshold: 60 seconds
                # Remove the lock file to release stale lock
                try:
                    self.lock_file_path.unlink()
                    self.lock_file_path.touch()
                except Exception:
                    pass  # Best effort
