"""
Configuration manager for loading and validating YAML configuration files
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .exceptions import ConfigurationError


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
        
        # Configuration caches
        self._dispatcher_config: Optional[Dict[str, Any]] = None
        self._allowed_skills: Optional[List[Dict[str, Any]]] = None
        self._event_triggers: Optional[List[Dict[str, Any]]] = None
        
        # Load configurations on initialization
        self.reload_all()
    
    def reload_all(self):
        """Reload all configuration files"""
        self._dispatcher_config = self._load_dispatcher_config()
        self._allowed_skills = self._load_allowed_skills()
        self._event_triggers = self._load_event_triggers()
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
    
    def _load_allowed_skills(self) -> List[Dict[str, Any]]:
        """Load the allowed skills configuration"""
        config = self._load_yaml("allowed_skills.yaml")
        skills = config.get("skills", [])
        self._validate_allowed_skills(skills)
        return skills
    
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
    
    def _validate_allowed_skills(self, skills: List[Dict[str, Any]]):
        """Validate allowed skills configuration"""
        if not skills:
            self.logger.warning("No skills in allowlist - dispatcher will reject all triggers")
        
        valid_risk_levels = {"low", "medium", "high"}
        skill_names = set()
        
        for skill in skills:
            # Check required fields
            if "name" not in skill:
                raise ConfigurationError("Skill entry missing 'name' field")
            
            skill_name = skill["name"]
            
            # Check for duplicates
            if skill_name in skill_names:
                raise ConfigurationError(f"Duplicate skill name in allowlist: {skill_name}")
            skill_names.add(skill_name)
            
            # Validate risk_level
            risk_level = skill.get("risk_level", "medium")
            if risk_level not in valid_risk_levels:
                raise ConfigurationError(
                    f"Invalid risk_level '{risk_level}' for skill '{skill_name}'. "
                    f"Must be one of: {valid_risk_levels}"
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
    
    # Public property accessors
    
    @property
    def dispatcher_config(self) -> Dict[str, Any]:
        """Get the dispatcher configuration"""
        return self._dispatcher_config.copy()
    
    @property
    def allowed_skills(self) -> List[Dict[str, Any]]:
        """Get the list of allowed skills"""
        return self._allowed_skills.copy()
    
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
        for skill in self._allowed_skills:
            if skill["name"] == skill_name:
                return True
        return False
    
    def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific skill
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill configuration dictionary or None if not found
        """
        for skill in self._allowed_skills:
            if skill["name"] == skill_name:
                return skill.copy()
        return None
    
    def get_max_depth(self) -> int:
        """Get the configured maximum execution depth"""
        return self._dispatcher_config["dispatcher"]["recursion_depth_limit"]
    
    def get_max_concurrent(self) -> int:
        """Get the configured maximum concurrent dispatches"""
        return self._dispatcher_config["dispatcher"]["max_concurrent_dispatches"]
