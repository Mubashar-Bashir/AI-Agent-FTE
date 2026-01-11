"""
Kill-switch implementation for emergency stop of all skill executions
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from .exceptions import UnauthorizedError


class KillSwitch:
    """
    Emergency stop mechanism for all dispatcher activity
    """
    
    def __init__(
        self,
        state_file: str = ".state/dispatcher_state.json",
        token_env_var: str = "DISPATCHER_ADMIN_TOKEN",
        logger: Optional[logging.Logger] = None
    ):
        self.state_file = Path(state_file)
        self.token_env_var = token_env_var
        self.logger = logger or logging.getLogger(__name__)
        
        # Ensure state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize state file if it doesn't exist
        if not self.state_file.exists():
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize the state file with default values"""
        initial_state = {
            "kill_switch_active": False,
            "last_activation": None,
            "last_deactivation": None,
            "activation_reason": None,
            "deactivation_reason": None,
            "activated_by": None,
            "deactivated_by": None
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
    
    def _get_admin_token(self) -> str:
        """Get the admin token from environment"""
        token = os.getenv(self.token_env_var)
        if not token:
            raise UnauthorizedError(
                f"Admin token not configured. Set environment variable: {self.token_env_var}"
            )
        return token
    
    def _authorize(self):
        """Authorize kill-switch operation with token"""
        token = self._get_admin_token()
        
        # Get token from user input
        provided_token = input(f"Enter admin token ({self.token_env_var}): ").strip()
        
        if provided_token != token:
            self.logger.warning(
                f"Unauthorized kill-switch attempt by user: {os.getenv('USER', 'unknown')}"
            )
            raise UnauthorizedError("Invalid admin token")
    
    def activate(self, reason: Optional[str] = None):
        """
        Activate the kill-switch to stop all skill executions
        
        Args:
            reason: Optional reason for activation
        """
        self._authorize()
        
        state = self._read_state()
        state["kill_switch_active"] = True
        state["last_activation"] = datetime.now().isoformat()
        state["activation_reason"] = reason
        state["activated_by"] = os.getenv("USER", "unknown")
        
        self._write_state(state)
        
        self.logger.info(f"Kill-switch activated by {state['activated_by']}: {reason or 'No reason provided'}")
    
    def deactivate(self, reason: Optional[str] = None):
        """
        Deactivate the kill-switch to resume normal operation
        
        Args:
            reason: Optional reason for deactivation
        """
        self._authorize()
        
        state = self._read_state()
        state["kill_switch_active"] = False
        state["last_deactivation"] = datetime.now().isoformat()
        state["deactivation_reason"] = reason
        state["deactivated_by"] = os.getenv("USER", "unknown")
        
        self._write_state(state)
        
        self.logger.info(f"Kill-switch deactivated by {state['deactivated_by']}: {reason or 'No reason provided'}")
    
    def is_active(self) -> bool:
        """
        Check if kill-switch is currently active
        
        Returns:
            True if kill-switch is active, False otherwise
        """
        state = self._read_state()
        return state.get("kill_switch_active", False)
    
    def get_status(self) -> dict:
        """
        Get detailed kill-switch status
        
        Returns:
            Dictionary with status information
        """
        state = self._read_state()
        return {
            "active": state["kill_switch_active"],
            "last_activation": state["last_activation"],
            "last_deactivation": state["last_deactivation"],
            "activation_reason": state["activation_reason"],
            "deactivation_reason": state["deactivation_reason"],
            "activated_by": state["activated_by"],
            "deactivated_by": state["deactivated_by"]
        }
    
    def force_activate(self, reason: str = "Emergency activation"):
        """
        Force activate without token (for internal use only)
        
        Args:
            reason: Reason for activation
        """
        state = self._read_state()
        state["kill_switch_active"] = True
        state["last_activation"] = datetime.now().isoformat()
        state["activation_reason"] = reason
        state["activated_by"] = "system"
        
        self._write_state(state)
        
        self.logger.warning(f"Force kill-switch activated: {reason}")
    
    def force_deactivate(self, reason: str = "Emergency deactivation"):
        """
        Force deactivate without token (for internal use only)
        
        Args:
            reason: Reason for deactivation
        """
        state = self._read_state()
        state["kill_switch_active"] = False
        state["last_deactivation"] = datetime.now().isoformat()
        state["deactivation_reason"] = reason
        state["deactivated_by"] = "system"
        
        self._write_state(state)
        
        self.logger.warning(f"Force kill-switch deactivated: {reason}")
