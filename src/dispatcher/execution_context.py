"""
Execution context management for recursion prevention and depth tracking
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .atomic_counter import AtomicCounter
from .lock_manager import LockManager
from .exceptions import DepthLimitError


class ExecutionContext:
    """
    Manages execution context for recursion prevention and depth tracking
    """
    
    def __init__(
        self,
        atomic_counter: AtomicCounter,
        max_depth: int = 3,
        state_file: str = ".state/execution_context.json",
        logger: Optional[logging.Logger] = None
    ):
        self.atomic_counter = atomic_counter
        self.max_depth = max_depth
        self.state_file = Path(state_file)
        self.logger = logger or logging.getLogger(__name__)
        self.lock_manager = LockManager("locks/context.lock")
        
        # Ensure state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize state file if it doesn't exist
        if not self.state_file.exists():
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize the execution context state file"""
        initial_state = {
            "current_depth": 0,
            "execution_stack": [],
            "total_executions": 0,
            "last_reset": datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(initial_state, f, indent=2)
    
    def _read_state(self) -> dict:
        """Read the current state from file"""
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _write_state(self, state: dict):
        """Write state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def enter_context(
        self,
        skill_name: str,
        trigger_event: str,
        parent_context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enter a new execution context, checking depth limits
        
        Args:
            skill_name: Name of the skill being executed
            trigger_event: Event that triggered this execution
            parent_context_id: ID of parent context (if any)
            
        Returns:
            Context information dictionary
            
        Raises:
            DepthLimitError: If maximum depth would be exceeded
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            
            # Calculate proposed new depth
            proposed_depth = state["current_depth"] + 1
            
            if proposed_depth > self.max_depth:
                raise DepthLimitError(
                    f"Execution depth limit ({self.max_depth}) exceeded. "
                    f"Current depth: {state['current_depth']}, attempting to enter: {skill_name}"
                )
            
            # Create context ID
            context_id = f"ctx-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}-{skill_name[:8]}"
            
            # Update execution stack
            execution_entry = {
                "id": context_id,
                "skill_name": skill_name,
                "trigger_event": trigger_event,
                "parent_context_id": parent_context_id,
                "enter_time": datetime.now().isoformat(),
                "depth": proposed_depth
            }
            
            state["execution_stack"].append(execution_entry)
            state["current_depth"] = proposed_depth
            state["total_executions"] = state.get("total_executions", 0) + 1
            
            # Write updated state
            self._write_state(state)
            
            # Also increment atomic counter
            self.atomic_counter.increment()
            
            self.logger.info(
                f"Entered execution context: {context_id} (depth: {proposed_depth}, skill: {skill_name})"
            )
            
            return {
                "context_id": context_id,
                "current_depth": proposed_depth,
                "max_depth": self.max_depth,
                "execution_chain": self._get_execution_chain(state)
            }
    
    def exit_context(self, context_id: str) -> Dict[str, Any]:
        """
        Exit an execution context
        
        Args:
            context_id: ID of the context to exit
            
        Returns:
            Context information dictionary
        """
        with self.lock_manager.acquire():
            state = self._read_state()
            
            # Find and remove the context from stack
            stack = state["execution_stack"]
            context_index = -1
            
            for i, entry in enumerate(reversed(stack)):
                if entry["id"] == context_id:
                    context_index = len(stack) - 1 - i
                    break
            
            if context_index == -1:
                self.logger.warning(f"Context {context_id} not found in execution stack")
                return {
                    "context_id": context_id,
                    "current_depth": state["current_depth"],
                    "exited": False
                }
            
            # Remove the context
            exited_context = stack.pop(context_index)
            
            # Update depth
            state["current_depth"] = len(stack)
            
            # Mark exit time
            exited_context["exit_time"] = datetime.now().isoformat()
            
            # Write updated state
            self._write_state(state)
            
            # Also decrement atomic counter
            self.atomic_counter.decrement()
            
            self.logger.info(
                f"Exited execution context: {context_id} (depth now: {state['current_depth']})"
            )
            
            return {
                "context_id": context_id,
                "current_depth": state["current_depth"],
                "exited": True,
                "execution_chain": self._get_execution_chain(state)
            }
    
    def get_current_depth(self) -> int:
        """Get the current execution depth"""
        with self.lock_manager.acquire():
            state = self._read_state()
            return state["current_depth"]
    
    def get_execution_chain(self) -> List[Dict[str, Any]]:
        """Get the current execution chain"""
        with self.lock_manager.acquire():
            state = self._read_state()
            return self._get_execution_chain(state)
    
    def _get_execution_chain(self, state: dict) -> List[Dict[str, Any]]:
        """Extract execution chain from state"""
        return [
            {
                "id": entry["id"],
                "skill_name": entry["skill_name"],
                "trigger_event": entry["trigger_event"],
                "depth": entry["depth"],
                "enter_time": entry["enter_time"]
            }
            for entry in state["execution_stack"]
        ]
    
    def check_depth_available(self) -> bool:
        """Check if another level of execution is available"""
        with self.lock_manager.acquire():
            state = self._read_state()
            return state["current_depth"] < self.max_depth
    
    def get_depth_remaining(self) -> int:
        """Get number of depth levels remaining"""
        with self.lock_manager.acquire():
            state = self._read_state()
            return max(0, self.max_depth - state["current_depth"])
    
    def reset_context(self):
        """Reset the execution context (for testing)"""
        with self.lock_manager.acquire():
            initial_state = {
                "current_depth": 0,
                "execution_stack": [],
                "total_executions": 0,
                "last_reset": datetime.now().isoformat()
            }
            self._write_state(initial_state)
            self.logger.info("Execution context reset")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self.lock_manager.acquire():
            state = self._read_state()
            return {
                "current_depth": state["current_depth"],
                "max_depth": self.max_depth,
                "depth_remaining": self.max_depth - state["current_depth"],
                "total_executions": state["total_executions"],
                "stack_size": len(state["execution_stack"]),
                "execution_chain": self._get_execution_chain(state)
            }
