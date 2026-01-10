# Kanban Component Skill Creator

## Skill Template: Kanban Board Component Generator

### Purpose
Generate a reusable Kanban board component that can be integrated into various applications and platforms, following the Obsidian Kanban plugin format and the automated workspace observer patterns.

### Parameters
- `board_name`: Name of the Kanban board
- `columns`: List of column names (default: To Do, In Progress, Done)
- `initial_cards`: Optional list of initial cards to populate the board
- `integration_type`: Type of integration (web, obsidian, desktop, etc.)

### Implementation

```python
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

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
        if 'done' in status.lower() or 'complete' in status.lower():
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


# Command execution
if __name__ == "__main__":
    import sys
    import json

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python kanban_skill.py <board_name> [columns_json] [cards_json] [output_path]")
        sys.exit(1)

    board_name = sys.argv[1]
    columns = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    cards = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    output_path = sys.argv[4] if len(sys.argv) > 4 else f"{board_name.lower().replace(' ', '_')}.md"

    content = create_kanban_component(board_name, columns, cards, output_path)
    print(content)
```

### Usage Examples

#### 1. Basic Kanban Board
```
python kanban_skill.py "Project Dashboard"
```

#### 2. Custom Columns
```
python kanban_skill.py "Development Board" '["Backlog", "Ready", "In Progress", "Review", "Done"]'
```

#### 3. With Initial Cards
```
python kanban_skill.py "Sprint Board" '["To Do", "In Progress", "Done"]' '[{"title": "Implement Feature X", "column": "To Do", "details": {"assignee": "John", "priority": "High"}}, {"title": "Fix Bug Y", "column": "In Progress", "details": {"assignee": "Jane", "status": "in progress"}}]'
```

### Features
- ✅ Compatible with Obsidian Kanban plugin
- ✅ Customizable columns and card details
- ✅ Status-aware checkbox indicators
- ✅ Reusable component pattern
- ✅ File export capability

### Integration Points
- Can be used with the workspace observer system
- Integrates with existing automation workflows
- Follows the same patterns as the workspace observer

### Output Format
Generates properly formatted markdown files compatible with Obsidian Kanban plugin and follows the same structural patterns as implemented in the workspace observer system.