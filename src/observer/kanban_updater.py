"""
Kanban updater module for the Automated Workspace Observer.

This module handles updating the Factory_Board.md Kanban board based on spec file changes.
"""
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from .utils import setup_logger, safe_read_file, safe_write_file


class KanbanUpdater:
    """Updates Factory_Board.md Kanban cards based on spec file changes."""

    def __init__(self, board_file: str = "00_Workspace/Factory_Board.md"):
        self.board_file = Path(board_file)
        self.logger = setup_logger()
        self.logger.debug(f"KanbanUpdater initialized with board file: {self.board_file}")

    def update_kanban_card(self, spec_file_path: str, yaml_data: Dict):
        """
        Update a Kanban card in Factory_Board.md based on spec file YAML data.

        Args:
            spec_file_path: Path to the spec file that was updated
            yaml_data: YAML metadata extracted from the spec file
        """
        try:
            self.logger.info(f"Updating Kanban card for spec: {spec_file_path}")

            # Read the current board content
            board_content = safe_read_file(str(self.board_file))
            if not board_content:
                self.logger.warning(f"Board file {self.board_file} does not exist or is empty")
                # Create a default board structure if it doesn't exist
                board_content = self._create_default_board()
                safe_write_file(str(self.board_file), board_content)

            # Extract spec name from file path
            spec_name = self._extract_spec_name(spec_file_path)

            # Check if the card already exists
            card_exists = self._card_exists(board_content, spec_name)

            if card_exists:
                # Update existing card
                updated_content = self._update_existing_card(board_content, spec_name, yaml_data)
                self.logger.info(f"Updated existing card for {spec_name}")
            else:
                # Create new card
                updated_content = self._create_new_card(board_content, spec_name, yaml_data)
                self.logger.info(f"Created new card for {spec_name}")

            # Write the updated content back to the file
            success = safe_write_file(str(self.board_file), updated_content)
            if success:
                self.logger.info(f"Successfully updated {self.board_file}")
            else:
                self.logger.error(f"Failed to write updated content to {self.board_file}")

        except Exception as e:
            self.logger.error(f"Error updating Kanban card for {spec_file_path}: {e}")

    def remove_kanban_card(self, spec_file_path: str):
        """
        Remove a Kanban card from Factory_Board.md when a spec file is deleted.

        Args:
            spec_file_path: Path to the spec file that was deleted
        """
        try:
            self.logger.info(f"Removing Kanban card for deleted spec: {spec_file_path}")

            # Read the current board content
            board_content = safe_read_file(str(self.board_file))
            if not board_content:
                self.logger.warning(f"Board file {self.board_file} does not exist or is empty")
                return

            # Extract spec name from file path
            spec_name = self._extract_spec_name(spec_file_path)

            # Remove the card for this spec
            updated_content = self._remove_card(board_content, spec_name)

            # Write the updated content back to the file
            success = safe_write_file(str(self.board_file), updated_content)
            if success:
                self.logger.info(f"Successfully removed card for {spec_name} from {self.board_file}")
            else:
                self.logger.error(f"Failed to write updated content to {self.board_file}")

        except Exception as e:
            self.logger.error(f"Error removing Kanban card for {spec_file_path}: {e}")

    def _extract_spec_name(self, spec_file_path: str) -> str:
        """Extract spec name from file path."""
        spec_path = Path(spec_file_path)
        # Get the stem (filename without extension) of the spec file
        spec_name = spec_path.stem
        return spec_name

    def _card_exists(self, board_content: str, spec_name: str) -> bool:
        """Check if a card for the given spec name already exists in the board."""
        # Look for the spec name in the board content
        # This pattern looks for the spec name as a list item
        pattern = rf'- \[.\]\[{re.escape(spec_name)}\]'
        return bool(re.search(pattern, board_content))

    def _update_existing_card(self, board_content: str, spec_name: str, yaml_data: Dict) -> str:
        """Update an existing card in the board content."""
        # Create the new card content
        new_card_content = self._create_card_content(spec_name, yaml_data)

        # Find the existing card and replace it
        # Pattern to match the entire card including all details
        pattern = rf'(- \[.\]\[{re.escape(spec_name)}\].*?)(?=\n- \[|\n##|$)'
        replacement = new_card_content

        # Replace the first occurrence of the card
        updated_content = re.sub(pattern, replacement, board_content, count=1, flags=re.DOTALL)

        # If the card wasn't found in the expected format, try alternative formats
        if updated_content == board_content:
            # Try simpler pattern
            simple_pattern = rf'{re.escape(spec_name)}.*?(?=\n- \[|\n##|$)'
            simple_replacement = f"{new_card_content}"
            updated_content = re.sub(simple_pattern, simple_replacement, board_content, count=1, flags=re.DOTALL)

        return updated_content

    def _create_new_card(self, board_content: str, spec_name: str, yaml_data: Dict) -> str:
        """Create a new card in the board content."""
        # Create the card content
        new_card_content = self._create_card_content(spec_name, yaml_data)

        # Add the new card to the "In Progress" section
        # Find the "In Progress" section and add the card there
        in_progress_pattern = r'(## In Progress\s*\n\s*\n)'
        replacement = rf'\g<1>{new_card_content}\n\n'

        # If "In Progress" section exists, add to it
        if re.search(in_progress_pattern, board_content):
            updated_content = re.sub(in_progress_pattern, replacement, board_content, count=1)
        else:
            # If "In Progress" section doesn't exist, create it and add the card
            header = "# Factory Board\n\n## In Progress\n\n"
            updated_content = header + new_card_content + "\n\n" + board_content

        return updated_content

    def _create_card_content(self, spec_name: str, yaml_data: Dict) -> str:
        """Create the content for a card based on spec name and YAML data."""
        # Extract relevant fields from YAML data
        status = yaml_data.get('status', 'Not Started')
        percentage = yaml_data.get('percentage', yaml_data.get('percent', '0%'))
        next_step = yaml_data.get('next_step', yaml_data.get('next', 'Define requirements'))
        description = yaml_data.get('description', f'Specification for {spec_name}')
        priority = yaml_data.get('priority', 'P3')

        # Format percentage properly
        if isinstance(percentage, (int, float)):
            percentage = f"{int(percentage)}%"
        elif isinstance(percentage, str) and not percentage.endswith('%'):
            percentage = f"{percentage}%"

        # Determine the checkbox state based on status
        checkbox = '.'  # Default to in-progress
        if 'done' in status.lower() or 'complete' in status.lower() or 'finished' in status.lower():
            checkbox = 'x'
        elif 'todo' in status.lower() or 'not started' in status.lower():
            checkbox = ' '
        elif 'completed' in status.lower():
            checkbox = 'x'
        elif 'in progress' in status.lower() or 'implementation' in status.lower():
            checkbox = '.'

        # Create the card content in the correct Obsidian Kanban format
        card_content = f"- [{checkbox}] {spec_name}\n"
        card_content += f"  - Status: {status}\n"
        card_content += f"  - Priority: {priority}\n"
        card_content += f"  - Progress: {percentage}\n"
        card_content += f"  - Description: {description}\n"
        card_content += f"  - Next: {next_step}"

        return card_content

    def _remove_card(self, board_content: str, spec_name: str) -> str:
        """Remove a card for the given spec name from the board content."""
        # Pattern to match the entire card including all details
        pattern = rf'(- \[.\]\[{re.escape(spec_name)}\].*?)(?=\n- \[|\n##|\n---|$)'

        # Remove the card
        updated_content = re.sub(pattern, '', board_content, count=1, flags=re.DOTALL)

        # Clean up any double newlines that might have been left behind
        updated_content = re.sub(r'\n\s*\n\s*\n', '\n\n', updated_content)

        return updated_content

    def _create_default_board(self) -> str:
        """Create a default board structure if the file doesn't exist."""
        default_content = """# Factory Board

## To Do


## In Progress


## Completed


## Blocked


## Verification Phase

---

## Legend
- [ ] To Do
- [.] In Progress
- [x] Completed
- [b] Blocked
"""
        self.logger.info(f"Created default board structure at {self.board_file}")
        return default_content