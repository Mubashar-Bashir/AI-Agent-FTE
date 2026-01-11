"""
Updated skill dispatcher with recursion prevention using execution context
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from .models import SkillDispatchRecord
from .config_manager import ConfigManager
from .logger import ExecutionLogger
from .event_hasher import EventHasher
from .hitl_approval_manager import HITLApprovalManager
from .kill_switch import KillSwitch
from .execution_context import ExecutionContext
from .exceptions import DepthLimitError, SkillNotAllowedError, LockTimeoutError


class SkillDispatcher:
    """
    Manages the actual dispatching of skills with all safety controls including recursion prevention
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        execution_logger: ExecutionLogger,
        event_hasher: EventHasher,
        max_depth: int = 3,
        logger: Optional[logging.Logger] = None
    ):
        self.config_manager = config_manager
        self.execution_logger = execution_logger
        self.event_hasher = event_hasher
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.atomic_counter = self._create_atomic_counter()
        self.approval_manager = HITLApprovalManager(logger=self.logger)
        self.kill_switch = KillSwitch(logger=self.logger)
        self.execution_context = ExecutionContext(
            atomic_counter=self.atomic_counter,
            max_depth=max_depth,
            logger=self.logger
        )
        
        # Maximum recursion depth from config
        self.max_depth = self.config_manager.get_max_depth()
    
    def _create_atomic_counter(self):
        """Create atomic counter instance"""
        from .atomic_counter import AtomicCounter
        return AtomicCounter()
    
    def dispatch(self, dispatch_request: Dict[str, Any]) -> SkillDispatchRecord:
        """
        Dispatch a skill with all safety controls including recursion prevention
        
        Args:
            dispatch_request: Dictionary containing dispatch information
            
        Returns:
            SkillDispatchRecord with execution results
        """
        # Create initial dispatch record
        record = SkillDispatchRecord(
            trigger_id=dispatch_request["trigger_id"],
            trigger_event=dispatch_request["trigger_event"],
            skill_invoked=dispatch_request["skill_name"],
            parameters={"trigger_event": dispatch_request["trigger_event"]}
        )
        
        start_time = time.time()
        
        try:
            # Check kill-switch status FIRST
            if self.kill_switch.is_active():
                record.status = "failure"
                record.error_message = "Kill-switch active - all skill execution disabled"
                self.execution_logger.log_dispatch(
                    trigger_event=dispatch_request["trigger_id"],
                    skill_name=dispatch_request["skill_name"],
                    result_status=record.status,
                    execution_time=time.time() - start_time,
                    error_message=record.error_message
                )
                return record
            
            # Check if skill is allowed
            if not self.config_manager.is_skill_allowed(dispatch_request["skill_name"]):
                raise SkillNotAllowedError(
                    f"Skill '{dispatch_request['skill_name']}' not in allowlist"
                )
            
            # Enter execution context (checks depth limits)
            try:
                context_info = self.execution_context.enter_context(
                    skill_name=dispatch_request["skill_name"],
                    trigger_event=dispatch_request["trigger_event"].get("matched_line", "unknown")
                )
                
                self.logger.info(
                    f"Entered execution context: depth={context_info['current_depth']}, "
                    f"skill={dispatch_request['skill_name']}"
                )
                
            except DepthLimitError as e:
                self.execution_logger.log_depth_limit(
                    skill_name=dispatch_request["skill_name"],
                    current_depth=self.execution_context.get_current_depth(),
                    max_depth=self.max_depth,
                    execution_chain=self.execution_context.get_execution_chain()
                )
                raise e
            
            # Check if approval is required
            requires_approval = (
                dispatch_request.get("requires_approval", False) or
                self._get_skill_risk_level(dispatch_request["skill_name"]) == "high"
            )
            
            if requires_approval:
                # Create approval request
                approval_request = self.approval_manager.create_approval_request(
                    skill_name=dispatch_request["skill_name"],
                    trigger_event=dispatch_request["trigger_event"],
                    risk_level=dispatch_request.get("risk_level", "high"),
                    timeout_seconds=300  # 5 minutes default
                )
                
                # Mark as pending approval
                record.status = "pending"
                record.approval_status = "pending"
                
                self.execution_logger.log_dispatch(
                    trigger_event=dispatch_request["trigger_id"],
                    skill_name=dispatch_request["skill_name"],
                    result_status=record.status,
                    execution_time=time.time() - start_time,
                    requires_approval=True
                )
                
                # Continue monitoring for approval (in real system, this would be async)
                self._monitor_approval(approval_request.request_id, record)
                
                return record
            else:
                # Execute skill directly
                result = self._execute_skill(dispatch_request)
                record.status = result["status"]
                record.execution_log = result["log"]
                record.duration_ms = int((time.time() - start_time) * 1000)
                
                self.execution_logger.log_dispatch(
                    trigger_event=dispatch_request["trigger_id"],
                    skill_name=dispatch_request["skill_name"],
                    result_status=record.status,
                    execution_time=time.time() - start_time
                )
                
                return record
        
        except Exception as e:
            # Handle any exceptions
            record.status = "failure"
            record.error_message = str(e)
            record.duration_ms = int((time.time() - start_time) * 1000)
            
            # Log unauthorized attempts differently
            if isinstance(e, SkillNotAllowedError):
                self.execution_logger.log_unauthorized(
                    skill_name=dispatch_request["skill_name"],
                    reason=str(e),
                    user_identity="system"
                )
            elif isinstance(e, DepthLimitError):
                # Already logged in the try block
                pass
            else:
                self.execution_logger.log_dispatch(
                    trigger_event=dispatch_request["trigger_id"],
                    skill_name=dispatch_request["skill_name"],
                    result_status=record.status,
                    execution_time=time.time() - start_time,
                    error_message=record.error_message
                )
            
            return record
        finally:
            # Mark event as completed in hasher
            event_hash = dispatch_request.get("event_hash")
            if event_hash:
                self.event_hasher.mark_completed(event_hash)
            
            # Exit execution context
            try:
                # We need to track the context ID that was entered
                # For simplicity, we'll exit with the current context
                # In a real system, we'd track the specific context ID
                current_depth = self.execution_context.get_current_depth()
                if current_depth > 0:
                    # Find the most recent context to exit
                    chain = self.execution_context.get_execution_chain()
                    if chain:
                        latest_context = chain[-1]
                        self.execution_context.exit_context(latest_context["id"])
                        self.logger.info(
                            f"Exited execution context, depth now: {self.execution_context.get_current_depth()}"
                        )
            except Exception as e:
                self.logger.error(f"Failed to exit execution context: {e}")
    
    def _get_skill_risk_level(self, skill_name: str) -> str:
        """Get the risk level for a skill"""
        skill_config = self.config_manager.get_skill_config(skill_name)
        return skill_config.get("risk_level", "medium") if skill_config else "medium"
    
    def _execute_skill(self, dispatch_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill (placeholder implementation)
        
        In a real system, this would integrate with the Claude Code skill system
        """
        skill_name = dispatch_request["skill_name"]
        trigger_event = dispatch_request["trigger_event"]
        
        # Log what would be executed
        log_output = (
            f"[PLACEHOLDER] Executing skill: {skill_name}\n"
            f"  Trigger: {trigger_event.get('matched_line', 'N/A')}\n"
            f"  Source: {trigger_event.get('source_file', 'N/A')}\n"
            f"  This would integrate with Claude Code skill system in production"
        )
        
        self.logger.info(log_output)
        
        return {
            "status": "success",
            "log": log_output
        }
    
    def _monitor_approval(self, request_id: str, record: SkillDispatchRecord):
        """
        Monitor approval status and execute skill if approved
        
        In a real system, this would run asynchronously
        """
        import time
        
        # Check approval status periodically
        for _ in range(10):  # Check 10 times over 30 seconds
            status = self.approval_manager.check_approval_status(request_id)
            
            if status == "approved":
                # Execute the skill
                dispatch_request = {"skill_name": record.skill_invoked}
                result = self._execute_skill(dispatch_request)
                
                record.status = result["status"]
                record.approval_status = "approved"
                record.approved_by = "system"  # Would be actual user in real system
                record.approval_timestamp = datetime.now()
                
                break
            elif status == "rejected":
                record.status = "rejected"
                record.approval_status = "rejected"
                break
            elif status == "timeout":
                record.status = "timeout"
                record.approval_status = "timeout"
                break
            
            time.sleep(3)  # Wait 3 seconds before checking again
