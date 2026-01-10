#!/usr/bin/env python3
"""
Kanban Component Skill - Generate customizable Kanban boards
Compatible with Obsidian Kanban plugin and workspace observer system
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import sys


class KanbanComponentGenerator:
    """Generates Kanban board components with customizable configurations."""

    def __init__(self, board_name: str, columns: Optional[List[str]] = None):
        self.board_name = board_name
        self.columns = columns or ["To Do", "In Progress", "Done"]
        self.cards = []

    def add_card(self, title: str, column: str, details: Optional[Dict] = None):
        """Add a card to a specific column."""
        card = {
            'title': title,
            'column': column,
            'details': details or {}
        }
        self.cards.append(card)

    def generate_obsidian_format(self) -> str:
        """Generate Kanban board in Obsidian format."""
        content = "---\nkanban-plugin: basic\n---\n\n"
        content += f"# {self.board_name}\n\n"

        for column in self.columns:
            content += f"## {column}\n"
            column_cards = [card for card in self.cards if card['column'] == column]
            for card in column_cards:
                status_char = self._get_status_char(card['details'].get('status', ''))
                content += f"- [{status_char}] {card['title']}\n"
                for key, value in card['details'].items():
                    if key != 'status':
                        content += f"  - {key.title()}: {value}\n"
                content += "\n"

        return content

    def _get_status_char(self, status: str) -> str:
        """Get the appropriate checkbox character based on status."""
        if 'done' in status.lower() or 'complete' in status.lower() or 'completed' in status.lower():
            return 'x'
        elif 'todo' in status.lower() or 'not started' in status.lower():
            return ' '
        elif 'in progress' in status.lower() or 'progress' in status.lower():
            return '.'
        elif 'blocked' in status.lower():
            return 'b'
        else:
            return '.'

    def save_to_file(self, filepath: str):
        """Save the Kanban board to a file."""
        content = self.generate_obsidian_format()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def create_kanban_component(board_name: str, columns: List[str] = None,
                          initial_cards: List[Dict] = None,
                          output_path: str = None) -> str:
    """
    Create a Kanban component with specified parameters.

    Args:
        board_name: Name of the Kanban board
        columns: List of column names
        initial_cards: List of initial cards to add
        output_path: Optional path to save the board

    Returns:
        Generated Kanban board content
    """
    generator = KanbanComponentGenerator(board_name, columns)

    if initial_cards:
        for card in initial_cards:
            title = card.get('title', '')
            column = card.get('column', 'To Do')
            details = card.get('details', {})
            generator.add_card(title, column, details)

    content = generator.generate_obsidian_format()

    if output_path:
        generator.save_to_file(output_path)

    return content


def main():
    """Main function to run the kanban component skill."""
    if len(sys.argv) < 2:
        print("Usage: python kanban_component_skill.py <board_name> [columns_json] [cards_json] [output_path]")
        print("\nExamples:")
        print("  python kanban_component_skill.py 'Project Dashboard'")
        print("  python kanban_component_skill.py 'Sprint Board' '[\"Backlog\", \"Ready\", \"In Progress\", \"Review\", \"Done\"]'")
        print("  python kanban_component_skill.py 'Team Board' '[\"To Do\", \"In Progress\", \"Done\"]' '[{\"title\": \"Task 1\", \"column\": \"To Do\", \"details\": {\"assignee\": \"Alice\"}}]'")
        sys.exit(1)

    board_name = sys.argv[1]
    columns = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    cards = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    output_path = sys.argv[4] if len(sys.argv) > 4 else f"{board_name.lower().replace(' ', '_').replace('/', '_')}.md"

    content = create_kanban_component(board_name, columns, cards, output_path)
    print(content)

    if output_path:
        print(f"\nKanban board saved to: {output_path}")


if __name__ == "__main__":
    main()