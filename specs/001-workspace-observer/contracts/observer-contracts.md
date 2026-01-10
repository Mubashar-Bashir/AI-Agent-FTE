# API Contracts: Automated Workspace Observer

## File System Event Contract

### File Change Event Schema
```json
{
  "type": "object",
  "properties": {
    "event_type": {
      "type": "string",
      "enum": ["created", "modified", "deleted"]
    },
    "file_path": {
      "type": "string",
      "format": "uri",
      "description": "Path to the spec file that changed"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the event occurred"
    },
    "processed": {
      "type": "boolean",
      "default": false
    }
  },
  "required": ["event_type", "file_path", "timestamp"]
}
```

## Spec File Metadata Contract

### YAML Metadata Schema
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the specification"
    },
    "status": {
      "type": "string",
      "enum": ["To Do", "In Progress", "Review", "Completed", "Blocked"],
      "description": "Current status of the specification"
    },
    "percentage": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Completion percentage"
    },
    "next_steps": {
      "type": "string",
      "description": "Next steps for the specification"
    },
    "created": {
      "type": "string",
      "format": "date",
      "description": "Date when the spec was created"
    },
    "last_updated": {
      "type": "string",
      "format": "date",
      "description": "Date when the spec was last updated"
    }
  },
  "required": ["title", "status", "percentage"]
}
```

## Kanban Card Contract

### Kanban Card Schema
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the Kanban card"
    },
    "status": {
      "type": "string",
      "enum": ["To Do", "In Progress", "Review", "Completed", "Blocked"],
      "description": "Current status column in the Kanban board"
    },
    "percentage": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Completion percentage"
    },
    "next_steps": {
      "type": "string",
      "description": "Next steps to be taken"
    },
    "file_reference": {
      "type": "string",
      "format": "uri",
      "description": "Reference to the corresponding spec file"
    }
  },
  "required": ["title", "status", "percentage", "file_reference"]
}
```

## SDD Tracker Entry Contract

### Tracker Entry Schema
```json
{
  "type": "object",
  "properties": {
    "spec_name": {
      "type": "string",
      "description": "Name of the specification"
    },
    "status": {
      "type": "string",
      "enum": ["To Do", "In Progress", "Review", "Completed", "Blocked"],
      "description": "Current status of the specification"
    },
    "percentage": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Completion percentage"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp of last update"
    },
    "file_path": {
      "type": "string",
      "format": "uri",
      "description": "Path to the spec file"
    }
  },
  "required": ["spec_name", "status", "percentage", "last_updated", "file_path"]
}
```

## Internal Service Interface Contracts

### SpecProcessor Interface
```python
class SpecProcessor:
    def process_file_change(self, file_path: str, event_type: str) -> bool:
        """
        Process a file change event and update corresponding Kanban and tracker entries.

        Args:
            file_path: Path to the spec file that changed
            event_type: Type of change (created, modified, deleted)

        Returns:
            bool: True if processing was successful, False otherwise
        """
        pass

    def process_multiple_changes(self, file_paths: List[str]) -> bool:
        """
        Process multiple file changes in alphabetical order (FR-008).

        Args:
            file_paths: List of file paths to process, will be sorted alphabetically

        Returns:
            bool: True if all processing was successful, False otherwise
        """
        pass
```

### KanbanUpdater Interface
```python
class KanbanUpdater:
    def update_card(self, card: KanbanCard) -> bool:
        """
        Update a Kanban card in Factory_Board.md.

        Args:
            card: KanbanCard object with updated information

        Returns:
            bool: True if update was successful, False otherwise
        """
        pass

    def create_card(self, card: KanbanCard) -> bool:
        """
        Create a new Kanban card in Factory_Board.md.

        Args:
            card: KanbanCard object with initial information

        Returns:
            bool: True if creation was successful, False otherwise
        """
        pass

    def delete_card(self, file_reference: str) -> bool:
        """
        Delete a Kanban card from Factory_Board.md based on file reference.

        Args:
            file_reference: Reference to the spec file

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
```

### TrackerUpdater Interface
```python
class TrackerUpdater:
    def update_entry(self, entry: TrackerEntry) -> bool:
        """
        Update a tracker entry in SDD_Tracker.md.

        Args:
            entry: TrackerEntry object with updated information

        Returns:
            bool: True if update was successful, False otherwise
        """
        pass

    def create_entry(self, entry: TrackerEntry) -> bool:
        """
        Create a new tracker entry in SDD_Tracker.md.

        Args:
            entry: TrackerEntry object with initial information

        Returns:
            bool: True if creation was successful, False otherwise
        """
        pass

    def delete_entry(self, spec_name: str) -> bool:
        """
        Delete a tracker entry from SDD_Tracker.md based on spec name.

        Args:
            spec_name: Name of the specification

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
```