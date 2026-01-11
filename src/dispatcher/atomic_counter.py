"""
Atomic counter with file-based persistence and fcntl locking
"""

import json
import os
import fcntl
import uuid
from pathlib import Path
from typing import Optional

from .lock_manager import LockManager


class AtomicCounter:
    """
    Maintains an atomic execution depth counter with file-based persistence
    
    Supports both single-process and distributed scenarios (Phase 1: single-process only)
    """
    
    def __init__(
        self,
        state_file: str = ".state/global_counter.json",
        instance_id: Optional[str] = None
    ):
        self.state_file = Path(state_file)
        self.instance_id = instance_id or self._generate_instance_id()
        self.lock_manager = LockManager()
        
        # Ensure state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize state file if it doesn't exist
        if not self.state_file.exists():
            self._initialize_state()
    
    def _generate_instance_id(self) -> str:
        """Generate a unique instance ID"""
        return f"inst-{uuid.uuid4().hex[:8]}"
    
    def _initialize_state(self):
        """Initialize the state file with default values"""
        initial_state = {
            "global_depth": 0,
            "instances": {}
        }
        with open(self.state_file, 'w') as f:
            json.dump(initial_state, f, indent=2)
    
    def _read_state(self) -> dict:
        """Read the current state from file"""
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _write_state(self, state: dict):
        """Write state to file atomically using temp file + rename"""
        temp_file = self.state_file.with_suffix('.tmp')
        
        # Write to temp file
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Atomic rename
        temp_file.replace(self.state_file)
    
    def increment(self) -> int:
        """
        Atomically increment the counter for this instance
        
        Returns:
            The new global depth after increment
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            
            # Increment this instance's depth
            instances = state.get("instances", {})
            current_instance_depth = instances.get(self.instance_id, 0)
            instances[self.instance_id] = current_instance_depth + 1
            
            # Recalculate global depth
            state["instances"] = instances
            state["global_depth"] = sum(instances.values())
            
            # Write state
            self._write_state(state)
            
            return state["global_depth"]
    
    def decrement(self) -> int:
        """
        Atomically decrement the counter for this instance
        
        Returns:
            The new global depth after decrement
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            
            # Decrement this instance's depth
            instances = state.get("instances", {})
            current_instance_depth = instances.get(self.instance_id, 0)
            new_instance_depth = max(0, current_instance_depth - 1)
            
            if new_instance_depth == 0:
                # Remove instance if depth is 0
                instances.pop(self.instance_id, None)
            else:
                instances[self.instance_id] = new_instance_depth
            
            # Recalculate global depth
            state["instances"] = instances
            state["global_depth"] = sum(instances.values())
            
            # Write state
            self._write_state(state)
            
            return state["global_depth"]
    
    def get_depth(self) -> int:
        """
        Get the current global execution depth
        
        Returns:
            Current global depth
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            return state.get("global_depth", 0)
    
    def get_instance_depth(self) -> int:
        """
        Get the execution depth for this specific instance
        
        Returns:
            Depth for this instance
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            instances = state.get("instances", {})
            return instances.get(self.instance_id, 0)
    
    def reset(self):
        """Reset the counter (for testing purposes)"""
        with self.lock_manager.acquire():
            state = {
                "global_depth": 0,
                "instances": {}
            }
            self._write_state(state)
