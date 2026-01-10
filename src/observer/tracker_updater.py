"""
Tracker updater module for the Automated Workspace Observer.

This module handles updating the SDD_Tracker.md file based on spec file changes.
"""
import re
from pathlib import Path
from typing import Dict, Optional
from .utils import setup_logger, safe_read_file, safe_write_file


class TrackerUpdater:
    """Updates SDD_Tracker.md based on spec file changes."""

    def __init__(self, tracker_file: str = "30_Specifications/SDD_Tracker.md"):
        self.tracker_file = Path(tracker_file)
        self.logger = setup_logger()
        self.logger.debug(f"TrackerUpdater initialized with tracker file: {self.tracker_file}")

    def update_tracker_entry(self, spec_file_path: str, yaml_data: Dict):
        """
        Update a tracker entry in SDD_Tracker.md based on spec file YAML data.

        Args:
            spec_file_path: Path to the spec file that was updated
            yaml_data: YAML metadata extracted from the spec file
        """
        try:
            self.logger.info(f"Updating tracker entry for spec: {spec_file_path}")

            # Read the current tracker content
            tracker_content = safe_read_file(str(self.tracker_file))
            if not tracker_content:
                self.logger.warning(f"Tracker file {self.tracker_file} does not exist or is empty")
                # Create a default tracker structure if it doesn't exist
                tracker_content = self._create_default_tracker()
                safe_write_file(str(self.tracker_file), tracker_content)

            # Extract spec name from file path
            spec_name = self._extract_spec_name(spec_file_path)

            # Check if the entry already exists
            entry_exists = self._entry_exists(tracker_content, spec_name)

            if entry_exists:
                # Update existing entry
                updated_content = self._update_existing_entry(tracker_content, spec_name, yaml_data)
                self.logger.info(f"Updated existing tracker entry for {spec_name}")
            else:
                # Create new entry
                updated_content = self._create_new_entry(tracker_content, spec_name, yaml_data)
                self.logger.info(f"Created new tracker entry for {spec_name}")

            # Write the updated content back to the file
            success = safe_write_file(str(self.tracker_file), updated_content)
            if success:
                self.logger.info(f"Successfully updated {self.tracker_file}")
            else:
                self.logger.error(f"Failed to write updated content to {self.tracker_file}")

        except Exception as e:
            self.logger.error(f"Error updating tracker entry for {spec_file_path}: {e}")

    def remove_tracker_entry(self, spec_file_path: str):
        """
        Remove a tracker entry from SDD_Tracker.md when a spec file is deleted.

        Args:
            spec_file_path: Path to the spec file that was deleted
        """
        try:
            self.logger.info(f"Removing tracker entry for deleted spec: {spec_file_path}")

            # Read the current tracker content
            tracker_content = safe_read_file(str(self.tracker_file))
            if not tracker_content:
                self.logger.warning(f"Tracker file {self.tracker_file} does not exist or is empty")
                return

            # Extract spec name from file path
            spec_name = self._extract_spec_name(spec_file_path)

            # Remove the entry for this spec
            updated_content = self._remove_entry(tracker_content, spec_name)

            # Write the updated content back to the file
            success = safe_write_file(str(self.tracker_file), updated_content)
            if success:
                self.logger.info(f"Successfully removed tracker entry for {spec_name} from {self.tracker_file}")
            else:
                self.logger.error(f"Failed to write updated content to {self.tracker_file}")

        except Exception as e:
            self.logger.error(f"Error removing tracker entry for {spec_file_path}: {e}")

    def _extract_spec_name(self, spec_file_path: str) -> str:
        """Extract spec name from file path."""
        spec_path = Path(spec_file_path)
        # Get the stem (filename without extension) of the spec file
        spec_name = spec_path.stem
        return spec_name

    def _entry_exists(self, tracker_content: str, spec_name: str) -> bool:
        """Check if a tracker entry for the given spec name already exists."""
        # Look for the spec name in the tracker content within the feature table
        pattern = rf'\| {re.escape(spec_name)} |'
        return bool(re.search(pattern, tracker_content))

    def _update_existing_entry(self, tracker_content: str, spec_name: str, yaml_data: Dict) -> str:
        """Update an existing tracker entry in the content."""
        # Extract fields from YAML data
        status = yaml_data.get('status', 'Not Started')
        current_step = yaml_data.get('current_step', yaml_data.get('step', 'Requirements Defined'))
        percentage = yaml_data.get('percentage', yaml_data.get('percent', 0))
        next_step = yaml_data.get('next_step', yaml_data.get('next', 'Implementation'))
        last_cmd = yaml_data.get('last_cmd', yaml_data.get('command', '/sp.tasks'))

        # Format percentage properly
        if isinstance(percentage, str) and '%' in percentage:
            percentage = percentage.replace('%', '')
        try:
            percentage = int(float(percentage))
        except (ValueError, TypeError):
            percentage = 0

        # Create the updated entry
        updated_entry = f"| {spec_name} | {status} | {current_step} | {percentage} | {next_step} | {last_cmd} |"

        # Find the existing entry and replace it
        # Pattern to match the entire entry row
        pattern = rf'\| {re.escape(spec_name)} .*?\n'
        replacement = updated_entry + '\n'

        # Replace the first occurrence of the entry
        updated_content = re.sub(pattern, replacement, tracker_content, count=1)

        # If the entry wasn't found in the expected format, try to add it
        if updated_content == tracker_content:
            # Find the feature section and add the entry
            feature_header_pattern = rf'## Feature: {re.escape(spec_name)}'
            if re.search(feature_header_pattern, tracker_content):
                # Update the existing feature section
                updated_content = self._update_feature_section(tracker_content, spec_name, status, current_step, percentage, next_step, last_cmd)
            else:
                # Add a new feature section
                updated_content = self._add_feature_section(tracker_content, spec_name, status, current_step, percentage, next_step, last_cmd)

        return updated_content

    def _create_new_entry(self, tracker_content: str, spec_name: str, yaml_data: Dict) -> str:
        """Create a new tracker entry in the content."""
        # Extract fields from YAML data
        status = yaml_data.get('status', 'Not Started')
        current_step = yaml_data.get('current_step', yaml_data.get('step', 'Requirements Defined'))
        percentage = yaml_data.get('percentage', yaml_data.get('percent', 0))
        next_step = yaml_data.get('next_step', yaml_data.get('next', 'Implementation'))
        last_cmd = yaml_data.get('last_cmd', yaml_data.get('command', '/sp.tasks'))

        # Format percentage properly
        if isinstance(percentage, str) and '%' in percentage:
            percentage = percentage.replace('%', '')
        try:
            percentage = int(float(percentage))
        except (ValueError, TypeError):
            percentage = 0

        # Create the new entry
        new_entry = f"| {spec_name} | {status} | {current_step} | {percentage} | {next_step} | {last_cmd} |"

        # Find the feature section for this spec or add a new one
        feature_header_pattern = rf'## Feature: {re.escape(spec_name)}'
        if re.search(feature_header_pattern, tracker_content):
            # Update the existing feature section
            updated_content = self._update_feature_section(tracker_content, spec_name, status, current_step, percentage, next_step, last_cmd)
        else:
            # Add a new feature section
            updated_content = self._add_feature_section(tracker_content, spec_name, status, current_step, percentage, next_step, last_cmd)

        return updated_content

    def _update_feature_section(self, tracker_content: str, spec_name: str, status: str, current_step: str, percentage: int, next_step: str, last_cmd: str) -> str:
        """Update an existing feature section in the tracker."""
        # Create the updated entry
        updated_entry = f"| {spec_name} | {status} | {current_step} | {percentage} | {next_step} | {last_cmd} |"

        # Find the feature section and update the table entry
        feature_header_pattern = rf'(## Feature: {re.escape(spec_name)}\s*\n\s*\n\|.*?\|\s*\n\|(?:-\s*)+\|\s*\n)'
        entry_pattern = rf'\| {re.escape(spec_name)} .*?\n'

        # Replace the existing entry
        replacement = lambda m: updated_entry + '\n' if re.search(rf'\| {re.escape(spec_name)} ', m.group()) else m.group()
        updated_content = re.sub(entry_pattern, replacement, tracker_content)

        # If no replacement happened, add the entry to the feature section
        if updated_content == tracker_content:
            # Find the feature header and table structure
            header_match = re.search(rf'(## Feature: {re.escape(spec_name)}\s*\n\s*\n)', tracker_content)
            table_header_match = re.search(rf'(## Feature: {re.escape(spec_name)}\s*\n\s*\|(?:.*?\|)+\s*\n\|(?:-*\|)+\s*\n)', tracker_content)

            if table_header_match:
                # Insert the entry after the table header
                pos = table_header_match.end()
                updated_content = tracker_content[:pos] + updated_entry + '\n' + tracker_content[pos:]
            elif header_match:
                # Add table structure and entry after the header
                table_structure = "| Spec Name | Status | Current Step | % | Next Step | Last Command |\n|-----------|--------|--------------|---|-----------|--------------|\n"
                pos = header_match.end()
                updated_content = tracker_content[:pos] + table_structure + updated_entry + '\n' + tracker_content[pos:]

        return updated_content

    def _add_feature_section(self, tracker_content: str, spec_name: str, status: str, current_step: str, percentage: int, next_step: str, last_cmd: str) -> str:
        """Add a new feature section to the tracker."""
        # Create the new entry
        new_entry = f"| {spec_name} | {status} | {current_step} | {percentage} | {next_step} | {last_cmd} |"

        # Create the feature section
        feature_section = f"\n## Feature: {spec_name}\n\n| Spec Name | Status | Current Step | % | Next Step | Last Command |\n|-----------|--------|--------------|---|-----------|--------------|\n{new_entry}\n"

        # Find the position to insert the feature section
        # Look for the end of the last feature section or the end of the document
        end_pattern = r'(## Feature:.*)$'
        end_match = re.search(end_pattern, tracker_content, re.MULTILINE | re.DOTALL)

        if end_match:
            # Insert after the last feature section
            pos = end_match.end()
            updated_content = tracker_content[:pos] + feature_section + tracker_content[pos:]
        else:
            # Insert at the end of the document
            updated_content = tracker_content.rstrip() + feature_section

        return updated_content

    def _remove_entry(self, tracker_content: str, spec_name: str) -> str:
        """Remove a tracker entry for the given spec name from the content."""
        # Remove the entry from the table
        entry_pattern = rf'\| {re.escape(spec_name)} .*?\n'
        updated_content = re.sub(entry_pattern, '', tracker_content)

        # Remove the feature section if it exists
        feature_pattern = rf'## Feature: {re.escape(spec_name)}.*?(?=\n## Feature: |\n*$)'
        updated_content = re.sub(feature_pattern, '', updated_content, flags=re.DOTALL)

        # Clean up any double newlines that might have been left behind
        updated_content = re.sub(r'\n\s*\n\s*\n', '\n\n', updated_content)

        return updated_content

    def _create_default_tracker(self) -> str:
        """Create a default tracker structure if the file doesn't exist."""
        default_content = """# SDD Tracker

## Active Feature Tracking

```dataview
TABLE status, current_step, percent, next_step
FROM #FTE-Feature
SORT file.name ASC
```

## All FTE Features

```dataview
TABLE status, current_step, percent, next_step, last_cmd
FROM #FTE-Feature
SORT file.name ASC
```

"""
        self.logger.info(f"Created default tracker structure at {self.tracker_file}")
        return default_content