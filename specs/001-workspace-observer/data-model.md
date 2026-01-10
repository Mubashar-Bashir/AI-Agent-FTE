# Data Model: Automated Workspace Observer

## Entities

### Spec File Monitor
- **Name**: SpecFileMonitor
- **Fields**:
  - `specs_directory`: str - Path to the /specs directory being monitored
  - `event_handler`: FileSystemEventHandler - Handler for file system events
  - `observer`: Observer - The watchdog observer instance
  - `is_running`: bool - Current running state of the monitor
- **Relationships**:
  - Contains -> FileChangeEvents
- **Validation**: specs_directory must exist and be accessible
- **State Transitions**: stopped -> running -> stopped

### File Change Event
- **Name**: FileChangeEvent
- **Fields**:
  - `event_type`: str - Type of event (created, modified, deleted)
  - `file_path`: str - Path to the affected file
  - `timestamp`: datetime - Time of the event occurrence
  - `processed`: bool - Whether the event has been processed
- **Relationships**:
  - Processed by -> SpecProcessor
- **Validation**: file_path must be within specs directory
- **State Transitions**: unprocessed -> processed

### Spec Processor
- **Name**: SpecProcessor
- **Fields**:
  - `processing_queue`: list - Queue of files to process in alphabetical order
  - `state_manager`: StateManager - Reference to state persistence
  - `kanban_updater`: KanbanUpdater - Reference to Kanban board updater
  - `tracker_updater`: TrackerUpdater - Reference to SDD tracker updater
- **Relationships**:
  - Processes <- FileChangeEvent
  - Updates -> Kanban Cards
  - Updates -> SDD Tracker Entries
- **Validation**: Processing queue must maintain alphabetical order (FR-008)
- **State Transitions**: idle -> processing -> idle

### Kanban Card
- **Name**: KanbanCard
- **Fields**:
  - `title`: str - Title of the spec file
  - `status`: str - Current status (e.g., "To Do", "In Progress", "Completed")
  - `percentage`: int - Completion percentage
  - `next_steps`: str - Next steps from spec metadata
  - `file_reference`: str - Reference to the corresponding spec file
- **Relationships**:
  - Updated by <- KanbanUpdater
  - Derived from -> Spec File
- **Validation**: Status must be one of predefined Kanban statuses
- **State Transitions**: Created -> Updated -> Archived (on spec deletion)

### SDD Tracker Entry
- **Name**: TrackerEntry
- **Fields**:
  - `spec_name`: str - Name of the specification
  - `status`: str - Current status of the specification
  - `percentage`: int - Completion percentage
  - `last_updated`: datetime - Timestamp of last update
  - `file_path`: str - Path to the spec file
- **Relationships**:
  - Updated by <- TrackerUpdater
  - Derived from -> Spec File
- **Validation**: Percentage must be between 0 and 100
- **State Transitions**: Created -> Updated -> Removed (on spec deletion)

### State Manager
- **Name**: StateManager
- **Fields**:
  - `state_file_path`: str - Path to .observer_state.json
  - `processed_files`: dict - Map of processed files and timestamps
  - `last_run_timestamp`: datetime - Time of last successful run
- **Relationships**:
  - Persists -> .observer_state.json
  - Referenced by <- SpecProcessor
- **Validation**: State file must be writable and persistent
- **State Transitions**: Initialized -> Updated -> Saved

### Spec File
- **Name**: SpecFile
- **Fields**:
  - `file_path`: str - Path to the spec file
  - `yaml_metadata`: dict - Parsed YAML metadata from the file
  - `content`: str - Full content of the file
  - `last_modified`: datetime - Last modification timestamp
- **Relationships**:
  - Creates -> KanbanCard
  - Creates -> TrackerEntry
- **Validation**: Must contain valid YAML frontmatter
- **State Transitions**: Created -> Modified -> Deleted

## Relationships Summary

```
Spec File Monitor
    ↓ monitors
File Change Events
    ↓ processed by
Spec Processor
    ↓ updates
Kanban Cards ↔ Factory_Board.md
Tracker Entries ↔ SDD_Tracker.md
    ↓ state maintained by
State Manager ↔ .observer_state.json
```