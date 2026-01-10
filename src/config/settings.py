"""
Configuration settings for the Automated Workspace Observer.

This module defines all configurable parameters for the observer service.
"""
import os
from pathlib import Path


class Settings:
    """Settings class for the workspace observer."""

    def __init__(self):
        # Directory settings
        self.SPEC_DIR = os.getenv("SPEC_DIR", "./specs")
        self.LOG_DIR = os.getenv("LOG_DIR", "./logs")

        # Observer settings
        self.CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1"))  # seconds
        self.PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "30"))  # seconds
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))  # seconds

        # State management settings
        self.STATE_FILE = os.getenv("STATE_FILE", ".observer_state.json")

        # Logging settings
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.path.join(self.LOG_DIR, "observer.log")
        self.LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB in bytes
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

        # Processing settings
        self.ALPHABETICAL_PROCESSING = os.getenv("ALPHABETICAL_PROCESSING", "true").lower() == "true"
        self.PARALLEL_PROCESSING_LIMIT = int(os.getenv("PARALLEL_PROCESSING_LIMIT", "1"))  # For now, single-threaded processing
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))  # Number of files to process in a batch

        # File settings
        self.WATCHED_EXTENSIONS = os.getenv("WATCHED_EXTENSIONS", ".md,.txt").split(",")
        self.IGNORE_PATTERNS = os.getenv("IGNORE_PATTERNS", ".git,__pycache__,*.tmp,*.temp,.DS_Store,Thumbs.db").split(",")

        # API/Integration settings (if needed for future extensions)
        self.OBSIDIAN_API_ENABLED = os.getenv("OBSIDIAN_API_ENABLED", "false").lower() == "true"
        self.OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")

        # Initialize directories
        self._initialize_directories()

    def _initialize_directories(self):
        """Create necessary directories if they don't exist."""
        Path(self.LOG_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.SPEC_DIR).mkdir(parents=True, exist_ok=True)

    def get_spec_dir_path(self):
        """Get the path object for the spec directory."""
        return Path(self.SPEC_DIR)

    def get_log_dir_path(self):
        """Get the path object for the log directory."""
        return Path(self.LOG_DIR)

    def get_state_file_path(self):
        """Get the path object for the state file."""
        return Path(self.STATE_FILE)


# Global settings instance
settings = Settings()


def get_settings():
    """Get the global settings instance."""
    return settings