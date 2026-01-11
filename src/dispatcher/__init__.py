"""
Autonomous Skill Dispatcher - Main Package Interface
"""

from .main import DispatcherMain
from .event_detector import EventDetector
from .skill_dispatcher import SkillDispatcher
from .config_manager import ConfigManager
from .logger import ExecutionLogger
from .models import (
    DispatcherState,
    EventTrigger,
    SkillDispatchRecord,
    HITLApprovalRequest,
    AllowedSkill
)
from .exceptions import (
    DispatcherException,
    LockTimeoutError,
    UnauthorizedError,
    DepthLimitError,
    ConfigurationError,
    SkillNotAllowedError,
    InvalidPatternError,
    ApprovalTimeoutError
)

__version__ = "1.0.0"
__author__ = "Autonomous Skill Dispatcher"
__all__ = [
    # Main classes
    'DispatcherMain',
    'EventDetector',
    'SkillDispatcher',
    'ConfigManager',
    'ExecutionLogger',
    
    # Models
    'DispatcherState',
    'EventTrigger',
    'SkillDispatchRecord',
    'HITLApprovalRequest',
    'AllowedSkill',
    
    # Exceptions
    'DispatcherException',
    'LockTimeoutError',
    'UnauthorizedError',
    'DepthLimitError',
    'ConfigurationError',
    'SkillNotAllowedError',
    'InvalidPatternError',
    'ApprovalTimeoutError',
]
