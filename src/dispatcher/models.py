"""
Data models for the Autonomous Skill Dispatcher
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid


@dataclass
class DispatcherState:
    """Global state of the dispatcher system"""
    global_execution_depth: int = 0
    kill_switch_active: bool = False
    instance_id: str = field(default_factory=lambda: f"inst-{uuid.uuid4().hex[:8]}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "global_execution_depth": self.global_execution_depth,
            "kill_switch_active": self.kill_switch_active,
            "instance_id": self.instance_id
        }


@dataclass
class EventTrigger:
    """Defines a pattern that triggers skill execution"""
    id: str
    name: str
    event_type: str
    pattern: str
    skill_to_invoke: str
    enabled: bool = True
    priority: int = 10
    risk_level: str = "medium"
    requires_approval: bool = False
    debounce_seconds: int = 30
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "event_type": self.event_type,
            "pattern": self.pattern,
            "skill_to_invoke": self.skill_to_invoke,
            "enabled": self.enabled,
            "priority": self.priority,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "debounce_seconds": self.debounce_seconds,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class SkillDispatchRecord:
    """Records each skill dispatch event"""
    id: str = field(default_factory=lambda: f"dispatch-{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    trigger_id: str = ""
    trigger_event: Dict[str, Any] = field(default_factory=dict)
    skill_invoked: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, success, failure, timeout
    execution_log: str = ""
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    approval_status: Optional[str] = None  # approved, rejected, pending, timeout
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "trigger_id": self.trigger_id,
            "trigger_event": self.trigger_event,
            "skill_invoked": self.skill_invoked,
            "parameters": self.parameters,
            "status": self.status,
            "execution_log": self.execution_log,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "approval_status": self.approval_status,
            "approved_by": self.approved_by,
            "approval_timestamp": self.approval_timestamp.isoformat() if self.approval_timestamp else None
        }


@dataclass
class HITLApprovalRequest:
    """Human-in-the-loop approval request for high-risk skills"""
    request_id: str = field(default_factory=lambda: f"req-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}")
    timestamp: datetime = field(default_factory=datetime.now)
    trigger_event: Dict[str, Any] = field(default_factory=dict)
    skill_to_invoke: str = ""
    risk_level: str = "high"
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    recommended_action: str = "approve"  # approve or reject
    reasoning: str = ""
    status: str = "pending"  # pending, approved, rejected, timeout
    expires_at: Optional[datetime] = None
    auto_approve_on_timeout: bool = False
    user_comment: Optional[str] = None
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "trigger_event": self.trigger_event,
            "skill_to_invoke": self.skill_to_invoke,
            "risk_level": self.risk_level,
            "risk_assessment": self.risk_assessment,
            "recommended_action": self.recommended_action,
            "reasoning": self.reasoning,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "auto_approve_on_timeout": self.auto_approve_on_timeout,
            "user_comment": self.user_comment,
            "approved_by": self.approved_by,
            "approval_timestamp": self.approval_timestamp.isoformat() if self.approval_timestamp else None
        }


@dataclass
class AllowedSkill:
    """Whitelist entry for skills that can be auto-executed"""
    id: str = field(default_factory=lambda: f"skill-{uuid.uuid4().hex[:8]}")
    skill_name: str = ""
    allowed: bool = True
    risk_level: str = "medium"
    requires_approval: bool = False
    description: str = ""
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "allowed": self.allowed,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "description": self.description,
            "reason": self.reason,
            "created_at": self.created_at.isoformat()
        }
