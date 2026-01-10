"""
State manager module for the Automated Workspace Observer.

This module manages the state of processed files in a .observer_state.json file,
allowing the observer to resume operation after restarts.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from .utils import setup_logger


class StateManager:
    """Manages the state of processed files."""

    def __init__(self, state_file: str = ".observer_state.json"):
        self.state_file = Path(state_file)
        self.logger = setup_logger()
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from the state file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.logger.info(f"Loaded state from {self.state_file}")
                    return state
            else:
                # Initialize with default state
                initial_state = {
                    "processed_files": {},
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                }
                self._save_state(initial_state)
                self.logger.info(f"Initialized new state file: {self.state_file}")
                return initial_state
        except Exception as e:
            self.logger.error(f"Error loading state from {self.state_file}: {e}")
            # Return a default state if loading fails
            return {
                "processed_files": {},
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }

    def _save_state(self, state: Dict = None):
        """Save state to the state file."""
        try:
            state_to_save = state if state is not None else self.state
            state_to_save["last_updated"] = datetime.now().isoformat()

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_to_save, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved state to {self.state_file}")
        except Exception as e:
            self.logger.error(f"Error saving state to {self.state_file}: {e}")

    def mark_file_processed(self, file_path: str):
        """Mark a file as processed."""
        try:
            file_path_str = str(Path(file_path).resolve())
            timestamp = datetime.now().isoformat()

            self.state["processed_files"][file_path_str] = {
                "processed_at": timestamp,
                "status": "processed"
            }

            self._save_state()
            self.logger.debug(f"Marked file as processed: {file_path_str}")
        except Exception as e:
            self.logger.error(f"Error marking file as processed {file_path}: {e}")

    def is_file_processed(self, file_path: str) -> bool:
        """Check if a file has been processed."""
        try:
            file_path_str = str(Path(file_path).resolve())
            return file_path_str in self.state["processed_files"]
        except Exception as e:
            self.logger.error(f"Error checking if file is processed {file_path}: {e}")
            return False

    def remove_processed_file(self, file_path: str):
        """Remove a file from the processed list (e.g., if it's deleted)."""
        try:
            file_path_str = str(Path(file_path).resolve())
            if file_path_str in self.state["processed_files"]:
                del self.state["processed_files"][file_path_str]
                self._save_state()
                self.logger.debug(f"Removed file from processed list: {file_path_str}")
        except Exception as e:
            self.logger.error(f"Error removing processed file {file_path}: {e}")

    def get_processed_files(self) -> Dict:
        """Get all processed files."""
        return self.state.get("processed_files", {})

    def clear_state(self):
        """Clear all state (use with caution)."""
        try:
            self.state = {
                "processed_files": {},
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            self._save_state()
            self.logger.info("Cleared observer state")
        except Exception as e:
            self.logger.error(f"Error clearing state: {e}")