"""
Security controls for skill execution including allowlist validation and authorization
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import logging

from .exceptions import SkillNotAllowedError, InvalidPatternError


class SecurityControls:
    """
    Manages security controls for skill execution including allowlist validation
    """
    
    def __init__(
        self,
        allowlist_file: str = "config/allowed_skills.yaml",
        logger: Optional[logging.Logger] = None
    ):
        self.allowlist_file = Path(allowlist_file)
        self.logger = logger or logging.getLogger(__name__)
        
        # Load allowlist
        self.allowed_skills: List[Dict[str, Any]] = []
        self.skill_lookup: Dict[str, Dict[str, Any]] = {}
        
        self._load_allowlist()
    
    def _load_allowlist(self):
        """Load and validate the skill allowlist from YAML file"""
        if not self.allowlist_file.exists():
            self.logger.warning(f"Allowlist file not found: {self.allowlist_file}")
            self.allowed_skills = []
            self.skill_lookup = {}
            return
        
        try:
            with open(self.allowlist_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or 'skills' not in config:
                self.logger.warning(f"No skills found in allowlist: {self.allowlist_file}")
                self.allowed_skills = []
                self.skill_lookup = {}
                return
            
            self.allowed_skills = config['skills']
            self.skill_lookup = {skill['name']: skill for skill in self.allowed_skills}
            
            self.logger.info(f"Loaded {len(self.allowed_skills)} allowed skills")
            
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in allowlist file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load allowlist: {e}")
            raise
    
    def is_skill_allowed(self, skill_name: str) -> bool:
        """
        Check if a skill is in the allowlist
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            True if skill is allowed, False otherwise
        """
        return skill_name in self.skill_lookup
    
    def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific skill
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill configuration dictionary or None if not found
        """
        return self.skill_lookup.get(skill_name)
    
    def validate_skill_name(self, skill_name: str) -> bool:
        """
        Validate that a skill name is safe (no injection attempts)
        
        Args:
            skill_name: Name of the skill to validate
            
        Returns:
            True if skill name is valid, False otherwise
        """
        # Check for potentially dangerous characters
        # Allow alphanumeric, hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9_.-]+$', skill_name):
            self.logger.warning(f"Invalid skill name format: {skill_name}")
            return False
        
        # Check for common attack patterns
        dangerous_patterns = [
            r'\.\.',  # Directory traversal
            r'[;&|$<>]',  # Shell metacharacters
            r'\.py$',  # Python files
            r'\.sh$',  # Shell scripts
            r'\.exe$',  # Executable files
            r'\.bat$',  # Batch files
            r'\.cmd$',  # Command files
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, skill_name, re.IGNORECASE):
                self.logger.warning(f"Potentially dangerous skill name: {skill_name}")
                return False
        
        return True
    
    def check_authorization(self, skill_name: str, user_identity: Optional[str] = None) -> bool:
        """
        Check if a user is authorized to execute a skill
        
        Args:
            skill_name: Name of the skill to check
            user_identity: Identity of the requesting user (optional)
            
        Returns:
            True if authorized, False otherwise
        """
        if not self.is_skill_allowed(skill_name):
            return False
        
        skill_config = self.get_skill_config(skill_name)
        if not skill_config:
            return False
        
        # Check if skill requires approval for this user
        requires_approval = skill_config.get('requires_approval', False)
        
        # For now, all users are authorized to execute allowed skills
        # In a real system, this would have more granular controls
        return True
    
    def get_risk_level(self, skill_name: str) -> str:
        """
        Get the risk level of a skill
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Risk level ('low', 'medium', 'high') or 'unknown' if not found
        """
        skill_config = self.get_skill_config(skill_name)
        if skill_config:
            return skill_config.get('risk_level', 'medium')
        return 'unknown'
    
    def get_allowed_skills(self) -> List[Dict[str, Any]]:
        """
        Get the complete list of allowed skills
        
        Returns:
            List of skill configuration dictionaries
        """
        return self.allowed_skills.copy()
    
    def reload_allowlist(self):
        """Reload the allowlist from file"""
        self.logger.info("Reloading skill allowlist...")
        self._load_allowlist()
    
    def log_unauthorized_attempt(
        self,
        skill_name: str,
        user_identity: Optional[str] = None,
        reason: str = "Not in allowlist"
    ):
        """
        Log an unauthorized skill execution attempt
        
        Args:
            skill_name: Name of the unauthorized skill
            user_identity: Identity of the requesting user
            reason: Reason for rejection
        """
        self.logger.warning(
            f"Unauthorized skill attempt: {skill_name} "
            f"by {user_identity or 'unknown'} - {reason}"
        )
    
    def validate_and_authorize(
        self,
        skill_name: str,
        user_identity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive validation and authorization check
        
        Args:
            skill_name: Name of the skill to validate
            user_identity: Identity of the requesting user
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "skill_name": skill_name,
            "is_valid": False,
            "is_allowed": False,
            "is_authorized": False,
            "requires_approval": False,
            "risk_level": "unknown",
            "errors": []
        }
        
        # Validate skill name format
        if not self.validate_skill_name(skill_name):
            result["errors"].append("Invalid skill name format")
            return result
        
        # Check if allowed
        if not self.is_skill_allowed(skill_name):
            result["errors"].append("Skill not in allowlist")
            return result
        
        # Check authorization
        if not self.check_authorization(skill_name, user_identity):
            result["errors"].append("User not authorized")
            return result
        
        # Get skill config
        skill_config = self.get_skill_config(skill_name)
        if skill_config:
            result["requires_approval"] = skill_config.get("requires_approval", False)
            result["risk_level"] = skill_config.get("risk_level", "medium")
            result["description"] = skill_config.get("description", "")
        
        # Set success flags
        result["is_valid"] = True
        result["is_allowed"] = True
        result["is_authorized"] = True
        
        return result


class RegexValidator:
    """
    Validates regex patterns for safety (ReDoS prevention)
    """
    
    @staticmethod
    def validate(pattern: str) -> bool:
        """
        Validate a regex pattern for safety
        
        Args:
            pattern: The regex pattern to validate
            
        Returns:
            True if pattern is safe, raises InvalidPatternError if not
        """
        # Check length
        if len(pattern) > 200:
            raise InvalidPatternError(f"Pattern too long: {len(pattern)} > 200 characters")
        
        # Check for potential ReDoS patterns
        dangerous_patterns = [
            r'\(.*\)\+',  # Nested quantifiers
            r'\(.*\)\*',  # Nested quantifiers
            r'\(.*\)\{\d*,\}',  # Nested quantifiers
            r'\(.*\)\{\d+,\d+\}',  # Nested quantifiers
            r'\(\[.*\]\)\+',  # Character class with quantifier
            r'\(\[.*\]\)\*',  # Character class with quantifier
        ]
        
        for dangerous_pattern in dangerous_patterns:
            if re.search(dangerous_pattern, pattern, re.IGNORECASE):
                raise InvalidPatternError(
                    f"Potentially dangerous regex pattern detected: {dangerous_pattern}"
                )
        
        # Check for excessive alternation
        if '||' in pattern or pattern.count('|') > 10:  # Simplified check
            raise InvalidPatternError("Excessive alternation in pattern")
        
        # Try compiling the pattern
        try:
            re.compile(pattern)
        except re.error as e:
            raise InvalidPatternError(f"Invalid regex syntax: {e}")
        
        return True
