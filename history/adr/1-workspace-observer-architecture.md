# ADR: Workspace Observer Architecture

## Status
Proposed

## Date
2026-01-10

## Context
We need to implement an automated workspace observer that monitors the /specs directory for changes in real-time. When spec files are created, modified, or deleted, the system must update the corresponding Kanban cards in 00_Workspace/Factory_Board.md and update the SDD tracker in 30_Specifications/SDD_Tracker.md based on YAML metadata. The system should run as a background service with high reliability and follow the proactive monitoring principle from Constitution I.

## Decision
We will implement the Workspace Observer using the following architectural decisions:

### Event-Driven vs Polling Approach
- **Framework**: Python watchdog library for file system monitoring
- **Rationale**: More efficient and responsive than polling, with lower CPU usage and immediate notification of file changes
- **Implementation**: Use FileSystemEventHandler to respond to file creation, modification, and deletion events

### State Management
- **Mechanism**: JSON state file (.observer_state.json) for persistence
- **Rationale**: Enables the service to remember which files were processed even after restarts, ensuring no duplicate processing or missed updates
- **Implementation**: Track processed files with timestamps and last-run information

### Predictable Sequencing
- **Strategy**: Alphabetical ordering for processing simultaneous file changes (FR-008)
- **Rationale**: Prevents race conditions and ensures deterministic processing order when multiple files change simultaneously
- **Implementation**: Sort file paths alphabetically before processing in batches

### Markdown Manipulation
- **Strategy**: Safe, non-destructive editing of Kanban board files
- **Rationale**: Preserve existing Kanban format while enabling targeted updates to specific cards
- **Implementation**: Use regex-based updates to modify specific card entries without affecting overall file structure

## Consequences

### Positive
- Efficient resource usage with event-driven monitoring vs. constant polling
- Resilient to restarts with persistent state tracking
- Deterministic processing order preventing race conditions
- Preserves existing file formats and structures
- Responsive updates within 5-second requirement (SC-001)

### Negative
- Dependency on third-party watchdog library
- Complexity of regex-based markdown manipulation
- Potential for conflicts if multiple processes access state file simultaneously
- Learning curve for team members unfamiliar with watchdog library

## Alternatives Considered

### Event-Driven vs Polling
- **Polling approach**: Periodically scan directory for changes every X seconds
  - Pros: Simpler to implement, no external dependencies
  - Cons: Higher resource usage, delayed response, potential to miss rapid changes

### State Management
- **In-memory tracking**: Store processed files in memory only
  - Pros: Faster access, simpler implementation
  - Cons: Loss of state on restart, potential for duplicate processing

### Predictable Sequencing
- **Parallel processing**: Process all changed files simultaneously
  - Pros: Faster processing for multiple changes
  - Cons: Race conditions, unpredictable order, violates FR-008 requirement

### Markdown Manipulation
- **Full rewrite approach**: Parse entire file, modify data structure, rewrite
  - Pros: More reliable parsing, less regex complexity
  - Cons: Risk of format loss, more complex implementation

## References
- Feature specification: specs/001-workspace-observer/spec.md
- Implementation plan: specs/001-workspace-observer/plan.md
- Research findings: specs/001-workspace-observer/research.md