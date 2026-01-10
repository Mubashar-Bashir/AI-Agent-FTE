"""
Spec processor module for the Automated Workspace Observer.

This module handles the processing of spec file changes,
including queuing changes in alphabetical order and processing them.
"""
import os
import time
import threading
from pathlib import Path
from queue import PriorityQueue
from typing import Dict, List, Tuple
import yaml
from .utils import setup_logger
from .state_manager import StateManager
from .kanban_updater import KanbanUpdater
from .tracker_updater import TrackerUpdater


class SpecProcessor:
    """Processes spec file changes in alphabetical order."""

    def __init__(self, logger=None, state_manager=None):
        # Priority queue to ensure alphabetical processing
        self.process_queue = PriorityQueue()
        self.logger = logger or setup_logger()
        self.state_manager = state_manager or StateManager()

        # Initialize updaters for Obsidian bridge
        self.kanban_updater = KanbanUpdater()
        self.tracker_updater = TrackerUpdater()

        # Thread for processing the queue
        self.processing_thread = None
        self.stop_processing = False

        # Lock for thread safety
        self.queue_lock = threading.Lock()

    def queue_file_change(self, file_path: str, change_type: str):
        """
        Queue a file change for processing in alphabetical order.

        Args:
            file_path: Path to the file that changed
            change_type: Type of change ('created', 'modified', 'deleted')
        """
        # Use the file path as priority to ensure alphabetical processing
        # Lower ASCII values (like 'a') have higher priority (lower numbers)
        priority = file_path.lower()

        with self.queue_lock:
            # Put tuple of (priority_string, file_path, change_type) in queue
            # We'll use the length and content of the path for comparison
            path_key = (len(file_path), file_path)
            self.process_queue.put((path_key, file_path, change_type))

        self.logger.info(f"Queued {change_type} event for: {file_path} (alphabetical priority)")

        # Start processing thread if not already running
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self._start_processing_thread()

    def _start_processing_thread(self):
        """Start the processing thread."""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.stop_processing = False
            self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.processing_thread.start()

    def _process_queue(self):
        """Process items in the queue in alphabetical order."""
        while not self.stop_processing:
            try:
                # Get the next item from the queue (with timeout)
                path_key, file_path, change_type = self.process_queue.get(timeout=1)

                # Process the file change
                self._process_file_change(file_path, change_type)

                # Mark task as done
                self.process_queue.task_done()

            except Exception as e:
                # Handle queue empty exception or other errors
                if "empty" not in str(e).lower():
                    self.logger.error(f"Error processing queue: {e}")
                continue

    def _process_file_change(self, file_path: str, change_type: str):
        """
        Process a single file change event.

        Args:
            file_path: Path to the file that changed
            change_type: Type of change ('created', 'modified', 'deleted')
        """
        try:
            self.logger.info(f"Processing {change_type} event for: {file_path}")

            # Update state manager with the processed file
            if change_type == 'deleted':
                self.state_manager.remove_processed_file(file_path)
            else:
                self.state_manager.mark_file_processed(file_path)

            # Handle different change types
            if change_type in ['created', 'modified']:
                self._handle_spec_file_update(file_path)
            elif change_type == 'deleted':
                self._handle_spec_file_deletion(file_path)

        except Exception as e:
            self.logger.error(f"Error processing file change for {file_path}: {e}")

    def _handle_spec_file_update(self, file_path: str):
        """
        Handle updates to spec files.

        Args:
            file_path: Path to the spec file that was updated
        """
        try:
            spec_path = Path(file_path)
            if not spec_path.exists():
                self.logger.warning(f"Spec file no longer exists: {file_path}")
                return

            # Read the spec file content
            with open(spec_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML metadata from the spec file
            yaml_data = self._extract_yaml_metadata(content)

            if yaml_data:
                self.logger.info(f"Extracted YAML metadata from {file_path}: {yaml_data}")
                # Update the Kanban board and SDD tracker with the extracted data
                self.kanban_updater.update_kanban_card(file_path, yaml_data)
                self.tracker_updater.update_tracker_entry(file_path, yaml_data)
            else:
                self.logger.info(f"No YAML metadata found in {file_path}")
                # Even if no YAML metadata is found, we should still create/update the card with default values
                default_yaml_data = {
                    'status': 'Implementation',
                    'percentage': '0%',
                    'next_step': 'Review spec',
                    'description': f'Specification for {spec_path.stem}'
                }
                self.kanban_updater.update_kanban_card(file_path, default_yaml_data)
                self.tracker_updater.update_tracker_entry(file_path, default_yaml_data)

        except Exception as e:
            self.logger.error(f"Error handling spec file update for {file_path}: {e}")

    def _handle_spec_file_deletion(self, file_path: str):
        """
        Handle deletion of spec files.

        Args:
            file_path: Path to the spec file that was deleted
        """
        try:
            self.logger.info(f"Handling deletion of spec file: {file_path}")
            # Remove corresponding Kanban board entries and tracker entries
            self.kanban_updater.remove_kanban_card(file_path)
            self.tracker_updater.remove_tracker_entry(file_path)

        except Exception as e:
            self.logger.error(f"Error handling spec file deletion for {file_path}: {e}")

    def _extract_yaml_metadata(self, content: str) -> dict:
        """
        Extract YAML metadata from the beginning of a spec file.

        Args:
            content: Content of the spec file

        Returns:
            Dictionary containing the extracted YAML metadata
        """
        try:
            # Look for YAML front matter (between --- delimiters)
            lines = content.split('\n')
            yaml_start_idx = -1
            yaml_end_idx = -1

            for i, line in enumerate(lines):
                if line.strip() == '---' and yaml_start_idx == -1:
                    yaml_start_idx = i
                elif line.strip() == '---' and yaml_start_idx != -1 and yaml_end_idx == -1:
                    yaml_end_idx = i
                    break

            if yaml_start_idx != -1 and yaml_end_idx != -1 and yaml_start_idx < yaml_end_idx:
                # Extract YAML content
                yaml_content = '\n'.join(lines[yaml_start_idx + 1:yaml_end_idx])

                # Parse YAML safely
                yaml_data = yaml.safe_load(yaml_content)

                if isinstance(yaml_data, dict):
                    return yaml_data
                else:
                    self.logger.warning("Parsed YAML is not a dictionary")
                    return {}
            else:
                # If no YAML front matter found, try to find YAML in the content
                # This handles cases where YAML metadata might be embedded differently
                return self._parse_embedded_yaml(content)

        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error in {content[:100]}...: {e}")
            return self._fallback_yaml_parsing(content)
        except Exception as e:
            self.logger.error(f"Unexpected error during YAML extraction: {e}")
            return self._fallback_yaml_parsing(content)

    def _parse_embedded_yaml(self, content: str) -> dict:
        """
        Try to parse embedded YAML metadata in the content.

        Args:
            content: Content of the spec file

        Returns:
            Dictionary containing the extracted YAML metadata
        """
        try:
            # Look for common YAML patterns in the file
            lines = content.split('\n')
            yaml_lines = []
            in_yaml_section = False

            for line in lines[:50]:  # Only check first 50 lines for efficiency
                stripped = line.strip()
                if stripped.startswith('#') or stripped == '':
                    continue

                # Look for key-value patterns that might indicate YAML
                if ':' in stripped and not stripped.startswith('-'):
                    yaml_lines.append(line)
                    in_yaml_section = True
                elif in_yaml_section and (stripped.startswith(' ') or stripped.startswith('\t')):
                    yaml_lines.append(line)
                elif in_yaml_section and stripped.startswith('-'):
                    yaml_lines.append(line)
                else:
                    break

            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
                try:
                    yaml_data = yaml.safe_load(yaml_content)
                    if isinstance(yaml_data, dict):
                        return yaml_data
                except yaml.YAMLError:
                    pass

            return {}

        except Exception as e:
            self.logger.error(f"Error during embedded YAML parsing: {e}")
            return {}

    def _fallback_yaml_parsing(self, content: str) -> dict:
        """
        Fallback method for YAML parsing when safe_load fails.
        This method attempts to extract basic key-value pairs.

        Args:
            content: Content of the spec file

        Returns:
            Dictionary containing basic extracted data
        """
        self.logger.warning("Using fallback YAML parsing method")

        try:
            # Simple fallback: extract common metadata fields
            result = {}

            # Look for common fields in the first portion of the file
            lines = content.split('\n')[:30]  # Check first 30 lines only

            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"\'')  # Remove quotes
                        if key in ['status', 'percentage', 'percent', 'next', 'next_step', 'title', 'feature']:
                            result[key] = value

            return result

        except Exception as e:
            self.logger.error(f"Fallback YAML parsing failed: {e}")
            return {}

    def stop_processing(self):
        """Stop the processing thread."""
        self.stop_processing = True
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)  # Wait up to 2 seconds