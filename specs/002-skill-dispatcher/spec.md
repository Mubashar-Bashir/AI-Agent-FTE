# Feature Specification: Autonomous Skill Dispatcher

**Feature Branch**: `002-skill-dispatcher`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Create specification for Feature 002-skill-dispatcher (Autonomous Skill Dispatcher) based on existing plan.md. Focus on MVP requirements for Bronze Tier: event detection, skill dispatching, HITL approval for high-risk skills, security controls (allowlist, ReDoS prevention), recursion prevention (max depth 3), pattern debouncing, kill-switch, and 90-day log retention. Target: single-process deployment with file-based state management."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Error Detection and Skill Triggering (Priority: P1)

As a **system operator**, I want the Workspace Observer to automatically detect errors in log files and trigger appropriate debugging skills so that issues are identified and addressed without constant manual monitoring.

**Why this priority**: This is the core value proposition of the feature - autonomous error detection and response. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by creating a test log file with an error pattern, verifying the pattern is detected, and confirming the configured skill is triggered. Delivers immediate value by automating the first response to errors.

**Acceptance Scenarios**:

1. **Given** a log file contains "TypeError: 'NoneType' object has no attribute 'process'", **When** the observer monitors the log file, **Then** the dispatcher detects the error pattern and queues the systematic-debugging skill for execution
2. **Given** a test failure appears in test output logs, **When** the dispatcher processes the event, **Then** the test-driven-development skill is triggered with the relevant test context
3. **Given** multiple identical errors occur within 30 seconds, **When** the dispatcher applies debouncing, **Then** only the first error triggers skill execution (subsequent identical errors are suppressed)

---

### User Story 2 - Human Approval for High-Risk Skills (Priority: P1)

As a **human operator**, I want to review and approve high-risk skill executions (code modifications, file deletions) before they run so that I maintain control over potentially destructive operations.

**Why this priority**: Constitutional requirement (HITL Safeguards). Without this, the system could make unauthorized changes, violating safety principles.

**Independent Test**: Can be fully tested by triggering a high-risk skill (e.g., code modification), verifying an approval request is created with risk assessment, approving via CLI, and confirming the skill executes only after approval.

**Acceptance Scenarios**:

1. **Given** an error triggers a high-risk skill (risk_level=high), **When** the dispatcher evaluates the trigger, **Then** an approval request file is created in `.approvals/` directory with risk assessment and timeout settings
2. **Given** an approval request exists with 5-minute timeout, **When** the human operator runs `dispatcher approve {request_id}` within the timeout, **Then** the skill executes and the approval decision is logged with timestamp and user identity
3. **Given** an approval request times out without response and auto_approve_on_timeout=false, **When** the timeout expires, **Then** the skill dispatch is rejected and logged as "approval_timeout_rejection"
4. **Given** a low-risk skill (read-only analysis) is triggered, **When** the dispatcher checks risk_level, **Then** the skill executes immediately without requiring human approval

---

### User Story 3 - Recursion Prevention (Priority: P1)

As a **system administrator**, I want the dispatcher to prevent infinite loops where skills trigger more skills indefinitely so that the system remains stable and doesn't consume excessive resources.

**Why this priority**: Critical safety mechanism. Without recursion prevention, a single error could cascade into system overload. This is a Bronze Tier requirement for stability.

**Independent Test**: Can be fully tested by creating a cascade scenario (Skill A triggers Skill B triggers Skill C triggers Skill D), verifying execution stops at depth 3, and confirming the 4th skill is rejected with a depth limit error.

**Acceptance Scenarios**:

1. **Given** Skill A executes and creates a log that triggers Skill B, **When** Skill B executes and creates a log that triggers Skill C, **Then** Skill C executes (depth=3) but any further skill triggers are rejected with "Max execution depth exceeded" error
2. **Given** three independent error patterns occur simultaneously, **When** each triggers a different skill at depth=1, **Then** all three skills execute in parallel (each starts at depth=1, not cumulative)
3. **Given** a skill completes execution, **When** the execution depth counter is decremented, **Then** the global depth is reduced and new skills can be triggered (depth limit resets per execution chain)

---

### User Story 4 - Emergency Kill-Switch (Priority: P2)

As a **system operator**, I want to immediately stop all active skill executions via a CLI command so that I can halt the system during emergencies or unexpected behavior.

**Why this priority**: Important safety mechanism but not required for basic operation. Skills can still run without this, but emergency control is valuable for production use.

**Independent Test**: Can be fully tested by starting a long-running skill, activating the kill-switch via `dispatcher kill-switch activate`, and verifying all skills stop within 5 seconds. The system can be used without this feature initially.

**Acceptance Scenarios**:

1. **Given** two skills are currently executing, **When** operator runs `dispatcher kill-switch activate` with valid admin token, **Then** both skills receive termination signals and stop within 5 seconds
2. **Given** the kill-switch is active, **When** a new error triggers a skill, **Then** the skill dispatch is rejected with "Kill-switch active" status
3. **Given** the kill-switch was activated, **When** operator runs `dispatcher kill-switch deactivate` with valid admin token, **Then** normal skill dispatching resumes and the state persists across process restarts

---

### User Story 5 - Security Allowlist Enforcement (Priority: P2)

As a **security administrator**, I want the dispatcher to only execute skills from a predefined allowlist so that unauthorized or malicious skills cannot be triggered by crafted log patterns.

**Why this priority**: Important security control but system can function initially with all installed skills trusted. Becomes critical when deploying in production or multi-user environments.

**Independent Test**: Can be fully tested by configuring an allowlist with 2 skills, attempting to trigger a skill not in the allowlist, verifying rejection, and confirming the attempt is logged.

**Acceptance Scenarios**:

1. **Given** `config/allowed_skills.yaml` contains systematic-debugging and verification-before-completion, **When** an error triggers test-driven-development (not in allowlist), **Then** the skill dispatch is rejected and logged as "Unauthorized skill execution attempt"
2. **Given** the allowlist is updated to add a new skill, **When** the configuration is reloaded, **Then** the new skill can be triggered without restarting the dispatcher
3. **Given** a skill in the allowlist has risk_level=high and requires_approval=true, **When** the skill is triggered, **Then** the HITL approval flow is enforced before execution

---

### User Story 6 - Audit Logging with 90-Day Retention (Priority: P3)

As a **compliance officer**, I want all dispatcher activities logged with 90-day retention (and 1-year retention for critical events like kill-switch activations) so that I can audit system behavior and investigate incidents.

**Why this priority**: Important for production and compliance but not required for initial Bronze Tier functionality. System can operate without long-term retention during development.

**Independent Test**: Can be fully tested by triggering various events (skill execution, approval, rejection, kill-switch), verifying logs are created in `logs/dispatcher/YYYY-MM-DD.log`, running cleanup after 91 days, and confirming old logs are removed while critical events remain archived.

**Acceptance Scenarios**:

1. **Given** the dispatcher has been running for 91 days, **When** the log retention policy runs, **Then** logs older than 90 days are deleted but critical event logs (kill-switch, high-risk approvals) remain archived for 365 days
2. **Given** a skill execution completes, **When** the event is logged, **Then** the log entry includes timestamp, trigger event, skill name, result status, execution time, and user identity (for approvals)
3. **Given** log files exceed 100MB, **When** log rotation occurs at midnight, **Then** the current log is closed, a new log file is created, and logs older than 7 days are compressed with gzip

---

### Edge Cases

- **What happens when the .approvals/ directory is full (disk space)?** System should fail gracefully by logging error and rejecting new approval requests until space is available
- **How does the system handle concurrent identical events before debounce cache updates?** Event hashing with SHA256 prevents duplicate processing even in race conditions
- **What if a skill crashes during execution?** Execution depth counter is decremented in a finally block to ensure counter doesn't get stuck, and the crash is logged
- **What happens when kill-switch is activated during an approval wait?** Pending approval requests are rejected with "Kill-switch override" status
- **How does the system handle malformed regex patterns in configuration?** Pattern validation on config load rejects invalid patterns and logs detailed error messages with line numbers
- **What if the lock file (.locks/dispatcher.lock) is corrupted or stale?** Lock acquisition includes timeout (5 seconds) and stale lock detection (locks older than 60 seconds are force-released)
- **What happens when observer detects rapid-fire events exceeding debounce capacity?** LRU cache automatically evicts oldest entries; system logs "debounce cache saturation" warning

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor log files for configured error patterns and queue skill execution requests when patterns match
- **FR-002**: System MUST execute skills automatically based on event triggers without human intervention for low-risk and medium-risk skills
- **FR-003**: System MUST require human approval before executing high-risk skills (risk_level=high) by creating approval request files in `.approvals/` directory
- **FR-004**: System MUST enforce a global execution depth limit of 3 to prevent infinite recursion loops where skills trigger other skills
- **FR-005**: System MUST implement pattern debouncing with a 30-second time window to suppress duplicate skill triggers for identical log patterns
- **FR-006**: System MUST validate all skill names against an allowlist defined in `config/allowed_skills.yaml` and reject unauthorized skills
- **FR-007**: System MUST validate regex patterns for complexity to prevent ReDoS (Regular Expression Denial of Service) attacks by rejecting patterns with nested quantifiers or excessive alternation
- **FR-008**: System MUST provide a kill-switch CLI command (`dispatcher kill-switch activate`) that stops all active skill executions within 5 seconds
- **FR-009**: System MUST require authentication (admin token via environment variable) before executing kill-switch commands
- **FR-010**: System MUST persist kill-switch state across process restarts to prevent accidental skill execution after crashes during maintenance
- **FR-011**: System MUST log all dispatcher activities (skill execution, approval decisions, kill-switch events) with timestamps, user identity, and context
- **FR-012**: System MUST implement 90-day log retention policy with automatic cleanup of logs older than 90 days (except critical events retained for 365 days)
- **FR-013**: System MUST use file-based locking (fcntl) to ensure thread-safe operations for counter updates, cache modifications, and state changes
- **FR-014**: System MUST support approval request timeout with configurable behavior (auto-approve or reject) when human response doesn't arrive within specified time
- **FR-015**: System MUST provide CLI commands for approval management: `dispatcher approve {request_id}`, `dispatcher reject {request_id}`, `dispatcher status`
- **FR-016**: System MUST decrement execution depth counter even when skill execution fails or crashes to prevent counter from getting stuck
- **FR-017**: System MUST store all state (execution counter, kill-switch status, approval requests) in local files under `.state/` directory (no external dependencies)
- **FR-018**: System MUST support configuration reload without process restart when `config/allowed_skills.yaml` or event mappings are updated
- **FR-019**: System MUST compress log files older than 7 days using gzip to reduce storage requirements
- **FR-020**: System MUST use event hashing (SHA256 of pattern + content + 5-second time window) to prevent duplicate processing in concurrent scenarios

### Non-Functional Requirements

- **NFR-001**: Dispatcher overhead on observer performance MUST be less than 5% (measured by CPU and memory usage)
- **NFR-002**: Pattern matching latency MUST be under 100ms for up to 50 configured patterns
- **NFR-003**: Kill-switch response time MUST be under 5 seconds from CLI command to all skills terminated
- **NFR-004**: System MUST support at least 1000 skill executions per hour without degradation
- **NFR-005**: Lock acquisition timeout MUST be 5 seconds to prevent deadlocks
- **NFR-006**: Approval request timeout MUST be configurable (default: 300 seconds / 5 minutes)
- **NFR-007**: Log file rotation MUST occur at midnight daily and individual log files MUST NOT exceed 100MB
- **NFR-008**: Configuration reload MUST complete within 2 seconds
- **NFR-009**: System MUST remain operational during configuration errors (invalid regex, missing allowlist) by logging errors and continuing with previous valid configuration

### Key Entities

- **Event Trigger**: Represents a configured mapping between log patterns and skills. Contains event_type (error/warning/info), regex pattern, skill_to_invoke, risk_level (low/medium/high), requires_human_approval flag, approval_timeout, and enabled flag.

- **Skill Dispatch Record**: Represents a skill execution event. Contains unique ID, timestamp, trigger_event details, skill_invoked name, result status (success/failure/pending_approval), execution_log output, approval_status (approved/rejected/pending/timeout), approved_by user, and approval_timestamp.

- **Human Approval Request**: Represents a pending approval for high-risk skill execution. Contains request_id, timestamp, trigger_event details, skill_to_invoke name, risk_assessment (description, potential_impact, affected_files, reversibility), recommended_action (approve/reject with reasoning), status (pending/approved/rejected/timeout), and expires_at timestamp.

- **Dispatcher State**: Represents the global state of the dispatcher. Contains global_execution_depth counter, kill_switch_active boolean, instance_id (UUID), and last_heartbeat timestamp. Persisted in `.state/global_counter.json`.

- **Allowed Skill Entry**: Represents a whitelisted skill in the security allowlist. Contains skill name, risk_level (low/medium/high), requires_approval flag, and description. Defined in `config/allowed_skills.yaml`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can configure event-to-skill mappings and the system begins monitoring within 5 seconds of configuration update
- **SC-002**: System automatically detects and responds to error patterns within 1 second of log entry appearing
- **SC-003**: Human operators receive approval notifications for high-risk skills within 2 seconds of trigger and can approve/reject via CLI in under 10 seconds
- **SC-004**: System prevents infinite recursion by enforcing maximum depth of 3 skill executions per chain with 100% reliability
- **SC-005**: Duplicate events within 30-second window are suppressed with 95%+ accuracy (measured by event hash collisions)
- **SC-006**: Unauthorized skills (not in allowlist) are rejected 100% of the time with security events logged
- **SC-007**: Kill-switch stops all active skills within 5 seconds of activation in 100% of tests
- **SC-008**: System maintains operational uptime above 99.5% (excluding planned maintenance) with graceful degradation during errors
- **SC-009**: Log retention policy successfully maintains 90 days of standard logs and 365 days of critical event logs without manual intervention
- **SC-010**: Configuration changes (new patterns, allowlist updates) take effect within 2 seconds without requiring process restarts
- **SC-011**: System performance overhead remains below 5% of observer baseline CPU and memory usage under normal load (up to 100 events/hour)
- **SC-012**: Pattern matching accuracy is 100% for valid regex patterns and 0 false positives for ReDoS validation (nested quantifiers correctly rejected)

## Assumptions

- The Workspace Observer infrastructure is already implemented and operational
- Skills follow a standard execution interface that can be invoked programmatically
- The system runs on a POSIX-compliant operating system (Linux/macOS) supporting fcntl file locking
- Log files are in plain text format (not binary) and accessible via standard file reading APIs
- Human operators have access to the CLI environment where the dispatcher is running
- Admin token for kill-switch can be securely distributed via environment variables or secure config files
- Single-process deployment (MVP) - multi-process/multi-machine distribution is deferred to Phase 2
- Disk space is sufficient for 90 days of logs (estimated 1-5GB depending on event volume)
- The system can write to `.state/`, `.approvals/`, `logs/`, `locks/`, and `config/` directories with appropriate permissions

## Dependencies

- **Workspace Observer (001-workspace-observer)**: Provides file monitoring infrastructure and event detection capabilities
- **Existing Skill Framework**: Skills must be discoverable and executable via programmatic interface
- **Python 3.11+**: Required for implementation (watchdog, fcntl, pathlib, hashlib, PyYAML)
- **File System**: Requires read/write access to working directory for state persistence and logging

## Out of Scope (Phase 2 / Future Enhancements)

- Multi-machine distributed deployment with Redis/ZooKeeper coordination
- Write-Ahead Logging (WAL) for crash recovery of atomic counter operations
- Persistent event hash storage (MVP uses in-memory hash set with basic disk persistence)
- Advanced heartbeat mechanisms for distributed instance health monitoring
- Real-time dashboard or web UI for monitoring dispatcher activity
- Integration with external notification systems (email, Slack, PagerDuty)
- Rate limiting per event source or per skill
- Dynamic skill loading/unloading without configuration changes
- Skill execution history analytics and trend analysis
- Cost/resource tracking per skill execution
