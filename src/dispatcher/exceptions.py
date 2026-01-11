"""
Custom exceptions for the Autonomous Skill Dispatcher
"""


class DispatcherException(Exception):
    """Base exception for all dispatcher-related errors"""
    pass


class LockTimeoutError(DispatcherException):
    """Raised when a lock cannot be acquired within the timeout period"""
    pass


class UnauthorizedError(DispatcherException):
    """Raised when an unauthorized action is attempted (e.g., kill-switch without token)"""
    pass


class DepthLimitError(DispatcherException):
    """Raised when execution depth exceeds the configured limit"""
    pass


class ConfigurationError(DispatcherException):
    """Raised when there's an error in configuration files"""
    pass


class SkillNotAllowedError(DispatcherException):
    """Raised when a skill is not in the allowlist"""
    pass


class InvalidPatternError(DispatcherException):
    """Raised when a regex pattern is invalid or potentially dangerous (ReDoS)"""
    pass


class ApprovalTimeoutError(DispatcherException):
    """Raised when an approval request times out"""
    pass
