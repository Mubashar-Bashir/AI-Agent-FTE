"""
Skill Dispatcher Core (T023 - User Story 1)

Dispatches skills based on detected events.
Integrates with ConfigManager and ExecutionLogger.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .models import EventTrigger, SkillDispatchRecord, RiskLevel
from .config_manager import ConfigManager
from .logger import ExecutionLogger
from .exceptions import SkillNotAllowedError, ApprovalRequiredError


class SkillDispatcher:
    """
    Core skill dispatch logic.

    Validates skills against allowlist and dispatches with logging.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        logger: ExecutionLogger
    ):
        """
        Initialize skill dispatcher.

        Args:
            config_manager: Configuration manager
            logger: Execution logger
        """
        self.config = config_manager
        self.logger = logger

    def dispatch_skill(
        self,
        trigger: EventTrigger,
        context: Dict[str, Any],
        execution_depth: int = 0
    ) -> SkillDispatchRecord:
        """
        Dispatch a skill based on trigger.

        Args:
            trigger: Event trigger that fired
            context: Event context
            execution_depth: Current execution depth

        Returns:
            Dispatch record

        Raises:
            SkillNotAllowedError: If skill not in allowlist
            ApprovalRequiredError: If skill requires approval
        """
        skill_name = trigger.skill_to_invoke

        # Validate skill is allowed
        skill_config = self.config.get_skill_config(skill_name)
        if not skill_config:
            raise SkillNotAllowedError(f"Skill '{skill_name}' not in allowlist")

        # Check if approval required
        if skill_config.requires_approval:
            raise ApprovalRequiredError(
                f"Skill '{skill_name}' requires HITL approval"
            )

        # Generate dispatch ID
        dispatch_id = str(uuid.uuid4())

        # Create dispatch record
        record = SkillDispatchRecord(
            id=dispatch_id,
            timestamp=datetime.now(),
            trigger_event=trigger.event_type,
            skill_invoked=skill_name,
            result="queued",
            execution_log=f"Skill queued for execution: {skill_name}",
            risk_level=skill_config.risk_level,
            execution_depth=execution_depth,
            parent_dispatch_id=context.get("parent_dispatch_id")
        )

        # Log dispatch
        self.logger.log_dispatch(
            skill_name=skill_name,
            trigger_event=trigger.event_type,
            result_status="queued",
            execution_time=0.0,
            execution_depth=execution_depth,
            is_critical=(skill_config.risk_level == RiskLevel.HIGH)
        )

        self.logger.info(
            f"Dispatched skill '{skill_name}' (trigger: {trigger.event_type}, "
            f"depth: {execution_depth})"
        )

        return record

    def can_dispatch(self, skill_name: str) -> tuple[bool, str]:
        """
        Check if skill can be dispatched.

        Args:
            skill_name: Name of skill to check

        Returns:
            Tuple of (can_dispatch, reason)
        """
        # Check allowlist
        skill_config = self.config.get_skill_config(skill_name)
        if not skill_config:
            return False, f"Skill '{skill_name}' not in allowlist"

        # Check approval requirement
        if skill_config.requires_approval:
            return False, f"Skill '{skill_name}' requires HITL approval"

        return True, "OK"

    def log_unauthorized_attempt(
        self,
        skill_name: str,
        trigger_event: str,
        reason: str
    ) -> None:
        """
        Log unauthorized skill execution attempt.

        Args:
            skill_name: Skill that was attempted
            trigger_event: Trigger event
            reason: Why it was rejected
        """
        self.logger.log_unauthorized_attempt(
            skill_name=skill_name,
            trigger_event=trigger_event,
            reason=reason
        )

    def get_allowed_skills(self) -> list:
        """Get list of allowed skills."""
        return self.config.get_allowed_skills()
