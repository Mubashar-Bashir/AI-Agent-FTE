"""
Updated configuration manager with enhanced security controls
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .exceptions import ConfigurationError
from .security_controls import SecurityControls


class ConfigManager:
    """
    Manages loading, validation, and reloading of configuration files
    """
    
    def __init__(
        self,
        config_dir: str = "config",
        logger: Optional[logging.Logger] = None
    ):
        self.config_dir = Path(config_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize security controls
        self.security_controls = SecurityControls(
            allowlist_file=self.config_dir / "allowed_skills.yaml",
            logger=self.logger
        )
        
        # Configuration caches
        self._dispatcher_config: Optional[Dict[str, Any]] = None
        self._event_triggers: Optional[List[Dict[str, Any]]] = None
        
        # Load configurations on initialization
        self.reload_all()
    
    def reload_all(self):
        """Reload all configuration files"""
        self._dispatcher_config = self._load_dispatcher_config()
        self._event_triggers = self._load_event_triggers()
        self.security_controls.reload_allowlist()
        self.logger.info("All configurations reloaded successfully")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load and parse a YAML file
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Parsed YAML content as dictionary
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise ConfigurationError(f"Configuration file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                content = yaml.safe_load(f)
                if content is None:
                    raise ConfigurationError(f"Empty configuration file: {filepath}")
                return content
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {filepath}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load {filepath}: {e}")
    
    def _load_dispatcher_config(self) -> Dict[str, Any]:
        """Load the main dispatcher configuration"""
        config = self._load_yaml("dispatcher_config.yaml")
        self._validate_dispatcher_config(config)
        return config
    
    def _load_event_triggers(self) -> List[Dict[str, Any]]:
        """Load the event triggers configuration"""
        config = self._load_yaml("event_triggers.yaml")
        triggers = config.get("triggers", [])
        self._validate_event_triggers(triggers)
        return triggers
    
    def _validate_dispatcher_config(self, config: Dict[str, Any]):
        """Validate dispatcher configuration structure and values"""
        dispatcher = config.get("dispatcher", {})
        
        # Validate required fields
        required_fields = ["max_concurrent_dispatches", "recursion_depth_limit"]
        for field in required_fields:
            if field not in dispatcher:
                raise ConfigurationError(f"Missing required field: dispatcher.{field}")
        
        # Validate value ranges
        max_concurrent = dispatcher["max_concurrent_dispatches"]
        if not (1 <= max_concurrent <= 10):
            raise ConfigurationError(
                f"max_concurrent_dispatches must be between 1 and 10, got {max_concurrent}"
            )
        
        depth_limit = dispatcher["recursion_depth_limit"]
        if not (1 <= depth_limit <= 10):
            raise ConfigurationError(
                f"recursion_depth_limit must be between 1 and 10, got {depth_limit}"
            )
    
    def _validate_event_triggers(self, triggers: List[Dict[str, Any]]):
        """Validate event triggers configuration"""
        trigger_ids = set()
        
        for trigger in triggers:
            # Check required fields
            required_fields = ["id", "pattern", "skill_to_invoke"]
            for field in required_fields:
                if field not in trigger:
                    raise ConfigurationError(f"Trigger missing required field: {field}")
            
            trigger_id = trigger["id"]
            
            # Check for duplicate IDs
            if trigger_id in trigger_ids:
                raise ConfigurationError(f"Duplicate trigger ID: {trigger_id}")
            trigger_ids.add(trigger_id)
            
            # Validate priority
            priority = trigger.get("priority", 10)
            if not (0 <= priority <= 100):
                raise ConfigurationError(
                    f"Invalid priority {priority} for trigger '{trigger_id}'. "
                    "Must be between 0 and 100"
                )
            
            # Validate skill is in allowlist
            skill_name = trigger["skill_to_invoke"]
            if not self.security_controls.is_skill_allowed(skill_name):
                raise ConfigurationError(
                    f"Skill '{skill_name}' in trigger '{trigger_id}' is not in allowlist"
                )
    
    # Public property accessors
    
    @property
    def dispatcher_config(self) -> Dict[str, Any]:
        """Get the dispatcher configuration"""
        return self._dispatcher_config.copy()
    
    @property
    def event_triggers(self) -> List[Dict[str, Any]]:
        """Get the list of event triggers"""
        return self._event_triggers.copy()
    
    def is_skill_allowed(self, skill_name: str) -> bool:
        """
        Check if a skill is in the allowlist
        
        Args:
            skill_name: Name of the skill to check
            
        Returns:
            True if skill is allowed, False otherwise
        """
        return self.security_controls.is_skill_allowed(skill_name)
    
    def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific skill
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill configuration dictionary or None if not found
        """
        return self.security_controls.get_skill_config(skill_name)
    
    def get_max_depth(self) -> int:
        """Get the configured maximum execution depth"""
        return self._dispatcher_config["dispatcher"]["recursion_depth_limit"]
    
    def get_max_concurrent(self) -> int:
        """Get the configured maximum concurrent dispatches"""
        return self._dispatcher_config["dispatcher"]["max_concurrent_dispatches"]
    
    def validate_and_authorize_skill(
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
        return self.security_controls.validate_and_authorize(skill_name, user_identity)
