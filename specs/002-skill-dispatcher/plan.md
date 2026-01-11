# Implementation Plan: Autonomous Skill Dispatcher

## Feature Specification Reference
- **Feature**: 002-skill-dispatcher
- **Title**: Autonomous Skill Dispatcher
- **Description**: A module that allows the Workspace Observer to automatically trigger specific skills when it detects errors in logs or other events.

## Technical Context
- **System Architecture**: The Workspace Observer currently monitors file changes and logs
- **Integration Point**: Need to connect event detection with skill execution
- **Trigger Mechanism**: Error detection in logs should trigger specific skills like systematic-debugging
- **Dependency**: Workspace Observer infrastructure (already implemented)
- **Technology Stack**: Python 3.11+, watchdog for file monitoring, existing skill framework

## Constitution Check
- **Modularity**: The dispatcher should be modular and not tightly coupled with specific skills
- **Reversibility**: Configuration should be easily adjustable to disable/modify triggers
- **Smallest Viable Change**: Start with basic error-to-skill mapping before adding complex conditions
- **Observability**: All dispatched skill executions should be logged for debugging

## Gates

- ✅ **Architecture Alignment**: This fits well with the SDD architecture as it extends the Workspace Observer to provide intelligent automation based on detected events, maintaining the proactive monitoring principle.
- ✅ **Security**: Security concerns are mitigated by implementing skill name validation, requiring skills to be in a predefined allowlist, and running skills in a controlled environment with limited permissions.
- ✅ **Performance**: Performance impact will be minimal as the dispatcher will use efficient pattern matching with configurable throttling to prevent excessive skill execution, and will update asynchronously to not block the main observer loop.
- ✅ **Dependencies**: Workspace Observer infrastructure is already implemented

## Phase 0: Research & Unknowns Resolution

### Research Tasks
1. **Skill Execution Interface**: How are skills currently executed in the system?
2. **Event Detection**: What types of events/logs should trigger skills?
3. **Configuration**: How should the mapping between events and skills be configured?
4. **Error Handling**: How should failed skill dispatches be handled?

### Expected Outcomes
- Understanding of current skill execution mechanism
- Identification of log/error patterns to monitor
- Design for configurable event-to-skill mapping
- Error handling strategy for failed dispatches

## Phase 1: Design & Contracts

### Data Model

#### Event Trigger
- `event_type`: String (error, warning, info, etc.)
- `pattern`: Regex pattern to match in logs
- `skill_to_invoke`: Name of the skill to execute
- `conditions`: Additional conditions for triggering
- `enabled`: Boolean flag to enable/disable
- `risk_level`: String (low, medium, high) - Classification of skill impact
- `requires_human_approval`: Boolean - True for high-risk skills requiring HITL
- `approval_timeout`: Integer - Seconds to wait for human response (default: 300)
- `auto_approve_on_timeout`: Boolean - Whether to proceed if no response (default: False)

**Risk Level Guidelines**:
- **Low**: Read-only operations, non-destructive analysis (e.g., code exploration)
- **Medium**: Automated fixes with low impact (e.g., formatting, minor refactoring)
- **High**: Code modifications, file creation/deletion, external API calls

#### Skill Dispatch Record
- `id`: Unique identifier
- `timestamp`: When the dispatch occurred
- `trigger_event`: Details of the triggering event
- `skill_invoked`: Name of the skill executed
- `result`: Success/failure status/pending_approval
- `execution_log`: Output from skill execution
- `approval_status`: String (approved, rejected, pending, timeout) - HITL decision
- `approved_by`: String - User who approved (if applicable)
- `approval_timestamp`: Timestamp - When approval was granted/rejected

#### HITL Approval Request
- `request_id`: Unique identifier for the approval request
- `timestamp`: When the approval was requested
- `trigger_event`: Event that triggered this request
- `skill_to_invoke`: Name of the skill requiring approval
- `risk_assessment`: Detailed risk explanation
- `recommended_action`: approve/reject with reasoning
- `status`: pending/approved/rejected/timeout
- `expires_at`: Timestamp when request expires

### API Contracts
#### Event Registration
- **Endpoint**: POST `/api/dispatcher/register-trigger`
- **Input**: Event trigger configuration
- **Output**: Confirmation of registration

#### Manual Dispatch
- **Endpoint**: POST `/api/dispatcher/dispatch`
- **Input**: Event details and target skill
- **Output**: Execution result

#### Status Check
- **Endpoint**: GET `/api/dispatcher/status`
- **Output**: Current dispatcher status and statistics

### Quickstart Guide
1. Configure event-to-skill mappings in dispatcher config
2. Start the Workspace Observer with dispatcher enabled
3. Monitor logs for registered event patterns
4. Automatically execute configured skills on matching events

### Security Controls

To ensure safe and authorized skill execution, we implement comprehensive security measures:

#### 1. Skill Allowlist Enforcement
- Maintain `config/allowed_skills.yaml` with approved skills
- Each skill entry includes: name, risk_level, description, requires_approval
- Dispatcher rejects any skill not in allowlist
- Allowlist is validated on startup and reloaded on configuration changes

**Example allowed_skills.yaml**:
```yaml
skills:
  - name: "systematic-debugging"
    risk_level: "medium"
    requires_approval: false
    description: "Analyzes errors and proposes fixes without modifying code"

  - name: "test-driven-development"
    risk_level: "high"
    requires_approval: true
    description: "Creates and modifies test files"

  - name: "verification-before-completion"
    risk_level: "low"
    requires_approval: false
    description: "Runs verification commands and reports results"
```

#### 2. Regex Pattern Validation (ReDoS Prevention)
- Validate all regex patterns before compilation
- Reject patterns with excessive backtracking (e.g., nested quantifiers)
- Limit pattern complexity using metrics: length < 200 chars, nesting depth < 5
- Test patterns against malicious inputs before deployment
- Use `re.compile()` with timeout wrapper to catch catastrophic backtracking

**Pattern Validation Rules**:
- No nested quantifiers: `(a+)+`, `(a*)*`
- No excessive alternation: `(a|b|c|d|e|f|g|h|...){100}`
- Maximum capture groups: 10
- Banned constructs: lookahead/lookbehind with quantifiers

#### 3. Kill-Switch Authorization
- Kill-switch CLI commands require authentication token
- Token stored in environment variable: `DISPATCHER_ADMIN_TOKEN`
- Token validated before executing kill-switch operations
- Failed authentication attempts are logged with IP/user details
- Alternative: Check for presence of `.dispatcher_admin` file in user's home directory

**Authorization Check**:
```python
def authorize_kill_switch():
    token = os.getenv("DISPATCHER_ADMIN_TOKEN")
    if not token:
        raise UnauthorizedError("Admin token not configured")

    provided_token = input("Enter admin token: ")
    if provided_token != token:
        logger.warning(f"Unauthorized kill-switch attempt by {os.getenv('USER')}")
        raise UnauthorizedError("Invalid admin token")
```

#### 4. Log Retention Policy (90-Day Minimum)
- All dispatcher logs stored in `logs/dispatcher/` directory
- Logs organized by date: `logs/dispatcher/YYYY-MM-DD.log`
- Automatic cleanup of logs older than 90 days
- Retention policy configurable via `config/dispatcher_config.yaml`
- Critical events (kill-switch, approval requests) archived separately for 1 year
- Log rotation at midnight daily using `logging.handlers.TimedRotatingFileHandler`

**Log Retention Configuration**:
```yaml
logging:
  retention_days: 90
  critical_retention_days: 365
  max_file_size_mb: 100
  compression: gzip  # Compress logs older than 7 days
```

#### 5. Sensitive Data Protection
- No credentials or API keys in dispatcher logs
- Redact sensitive patterns from log content before processing
- Store configuration with sensitive fields in environment variables
- Encrypt approval request files if they contain sensitive context

## Phase 2: Implementation Approach

### Component 1: Event Detector
- Monitor log files using existing watchdog infrastructure
- Match events against configured patterns (with ReDoS validation)
- Check skill against allowlist before queuing
- Queue skill execution requests

### Component 2: Skill Dispatcher
- Receive skill execution requests from event detector
- Validate skill is in allowlist
- Check risk_level and requires_human_approval flags
- If approval required: Create approval request and wait for response
- If approved or no approval needed: Execute the target skill with appropriate context
- Sanitize skill parameters to prevent injection attacks

### Component 3: HITL Approval Manager (HITL Component)
- Create approval request files in `.approvals/` directory
- Request format: `.approvals/pending_{request_id}.json`
- Display approval prompt to user via CLI notification
- Monitor for approval response (Y/N) via file update or CLI input
- Handle timeout scenarios based on `auto_approve_on_timeout` flag
- Log all approval decisions with user identity and timestamp
- Clean up processed approval files after 24 hours

**Approval Flow**:
1. High-risk skill triggered → Create `.approvals/pending_{id}.json`
2. Notify user via console output and optional system notification
3. User reviews risk assessment and responds:
   - Option 1: Update JSON file with `{"status": "approved", "user": "mubashar"}`
   - Option 2: Run CLI command: `dispatcher approve {request_id}`
   - Option 3: Run CLI command: `dispatcher reject {request_id} --reason "..."`
4. Approval manager detects response and proceeds/cancels accordingly
5. Log decision and continue workflow

**Approval Request File Structure** (`.approvals/pending_{id}.json`):
```json
{
  "request_id": "req-20260111-123456",
  "timestamp": "2026-01-11T12:34:56Z",
  "expires_at": "2026-01-11T12:39:56Z",
  "trigger_event": {
    "event_type": "error",
    "pattern": "TypeError: .* object has no attribute",
    "matched_log": "TypeError: 'NoneType' object has no attribute 'process'"
  },
  "skill_to_invoke": "systematic-debugging",
  "risk_level": "high",
  "risk_assessment": {
    "description": "This skill will analyze the code and may propose modifications to fix the TypeError.",
    "potential_impact": ["Code file modifications", "Test file creation"],
    "affected_files": ["src/processor.py"],
    "reversible": true
  },
  "recommended_action": "approve",
  "reasoning": "Systematic debugging is needed to resolve the TypeError. All changes will be version-controlled.",
  "status": "pending",
  "auto_approve_on_timeout": false
}
```

**User Response Format** (update same file or use CLI):
```json
{
  ...
  "status": "approved",
  "approved_by": "mubashar",
  "approval_timestamp": "2026-01-11T12:35:30Z",
  "user_comment": "Approved - please proceed with debugging"
}
```

**Implementation Files**:
- Create: `src/dispatcher/approval_manager.py` (HITL approval logic)
- Create: `src/dispatcher/cli_commands.py` (approve/reject CLI commands)
- Create: `.approvals/` directory (approval request storage)
- Modify: `src/dispatcher/skill_dispatcher.py` (check approval before execution)

### Component 4: Configuration Manager
- Load and validate `config/allowed_skills.yaml` on startup
- Load and manage event-to-skill mappings
- Validate regex patterns against ReDoS rules
- Provide runtime configuration updates (with re-validation)
- Store dispatcher settings
- Reload configuration without restart when files change

### Component 5: Execution Logger
- Log all dispatch events for observability (with 90-day retention)
- Track skill execution outcomes
- Provide debugging information
- Redact sensitive data from logs
- Archive critical events separately

## Phase 3: Integration & Testing

### Integration Points
- Integrate with Workspace Observer's file monitoring
- Connect to existing skill execution framework
- Ensure compatibility with current logging system

### Testing Strategy
- Unit tests for event pattern matching
- Integration tests for skill dispatch mechanism
- End-to-end tests with actual skill execution
- Error condition testing

## Risk Analysis & Mitigation

### Top 3 Risks
1. **Recursive Execution**: Skills triggered by logs might generate more logs
   - *Mitigation*: Implement recursion detection and prevention
2. **Performance Impact**: Constant monitoring might slow down the system
   - *Mitigation*: Use efficient pattern matching and throttling
3. **Security Issues**: Unauthorized skill execution
   - *Mitigation*: Validate skill names and implement access controls

## Implementation Phases: MVP vs Future Enhancements

To satisfy the "Smallest Viable Change" constitutional principle, we implement the dispatcher in two phases:

### Phase 1: MVP (Minimum Viable Product)
**Goal**: Establish core dispatching with essential safety mechanisms

**In Scope**:
- ✅ Basic event detection and skill dispatching
- ✅ **HITL Approval Manager** (Constitutional requirement for high-risk skills)
- ✅ **Security Controls**: Skill allowlist, regex validation, kill-switch authorization
- ✅ **Global Execution Counter** (max depth = 3, single-process only)
- ✅ **Pattern Debouncing** (30-second time window)
- ✅ **Kill-Switch CLI** (emergency stop mechanism)
- ✅ **Thread-Safe Lock Manager** (file-based locking for critical operations)
- ✅ **Basic Event Hashing** (in-memory deduplication)
- ✅ **90-Day Log Retention** (Constitutional requirement)

**Out of Scope** (Deferred to Phase 2):
- ❌ Distributed Instance Manager (multi-machine coordination)
- ❌ Write-Ahead Logging for crash recovery
- ❌ Persistent event hash storage
- ❌ Advanced heartbeat mechanisms
- ❌ Redis/ZooKeeper integration

**Rationale**: MVP focuses on single-process deployment with robust safety mechanisms (HITL, security controls) while deferring distributed system complexity. This provides immediate value while maintaining constitutional compliance.

### Phase 2: Future Enhancements (Post-MVP)
**Goal**: Scale to distributed deployments and advanced resilience

**Planned Features**:
- Distributed Instance Manager with heartbeat coordination
- Write-Ahead Logging for atomic counter operations
- Persistent event hash storage for crash recovery
- Multi-machine deployment support (Redis/ZooKeeper)
- Advanced metrics and monitoring dashboards
- Rate limiting per event source
- Dynamic skill loading/unloading

**Prerequisites**: MVP must be deployed and validated in production for at least 2 weeks before starting Phase 2 enhancements.

## Recursive Guardrails & Safety Mechanisms (Phase 1 - MVP)

To address the critical risk of infinite recursion and cascading skill triggers, we implement multiple layers of protection:

### 1. Global Execution Counter (Max Depth = 3)

**Purpose**: Prevent deep recursion chains where skills trigger other skills repeatedly.

**Implementation Approach**:
- Maintain a thread-safe global counter tracking the current "execution depth"
- When a skill is triggered:
  - Increment the counter before execution
  - Check if counter > MAX_DEPTH (default: 3)
  - If exceeded, reject the skill dispatch and log a warning
  - Decrement the counter after execution completes (success or failure)
- Track execution context (which skill triggered which) for debugging

**Acceptance Criteria**:
- ✅ System rejects skill dispatches when depth exceeds 3
- ✅ Counter is thread-safe and works with concurrent skill executions
- ✅ Execution chain is logged for post-mortem analysis
- ✅ Counter resets properly after each top-level skill completes

**Integration Points**:
- `src/dispatcher/skill_dispatcher.py`: Add counter check before skill execution
- `src/dispatcher/recursion_guard.py`: Implement counter and depth tracking logic
- `src/dispatcher/logger.py`: Log execution chain and depth warnings

**Files to Create/Modify**:
- Create: `src/dispatcher/execution_context.py` (manages execution depth and chain)
- Modify: `src/dispatcher/skill_dispatcher.py` (add depth check before dispatch)
- Modify: `src/dispatcher/logger.py` (log execution chain details)

### 2. Pattern Debouncing (Time-Window Protection)

**Purpose**: Prevent rapid-fire triggers of the same pattern within a short time window.

**Implementation Approach**:
- Maintain a time-based cache of recently triggered patterns
- Key: (pattern_id, log_content_hash)
- Value: timestamp of last trigger
- Before dispatching a skill:
  - Check if the same pattern+content was triggered within the last N seconds (default: 30s)
  - If yes, suppress the trigger and log a debounce event
  - If no, allow the trigger and update the cache
- Use LRU cache with configurable size limit to prevent memory bloat

**Acceptance Criteria**:
- ✅ Identical events within 30 seconds are suppressed (only first triggers)
- ✅ Different events (different log content) are not suppressed
- ✅ Cache size is bounded and uses LRU eviction
- ✅ Debounce window is configurable per pattern
- ✅ Debounced events are logged for monitoring

**Integration Points**:
- `src/dispatcher/event_detector.py`: Add debounce check before queuing events
- `src/dispatcher/config_manager.py`: Support per-pattern debounce configuration
- `src/dispatcher/logger.py`: Log debounced events for analysis

**Files to Create/Modify**:
- Create: `src/dispatcher/debouncer.py` (implements time-window caching)
- Modify: `src/dispatcher/event_detector.py` (add debounce check)
- Modify: `config/dispatcher_config.yaml` (add debounce_seconds per pattern)

### 3. Kill-Switch CLI Command (Emergency Stop)

**Purpose**: Provide immediate emergency stop mechanism for all active skill executions.

**Implementation Approach**:
- Create a global "kill switch" flag accessible from CLI and programmatically
- When activated:
  - Set a global `KILL_SWITCH_ACTIVE` flag to True
  - Send termination signals to all currently executing skills
  - Prevent new skill dispatches until the switch is deactivated
  - Log the kill-switch activation event with timestamp and user
- Provide CLI commands:
  - `dispatcher kill-switch activate` - Stop all skills immediately
  - `dispatcher kill-switch deactivate` - Resume normal operation
  - `dispatcher kill-switch status` - Check current state

**Acceptance Criteria**:
- ✅ Kill-switch stops all active skills within 5 seconds
- ✅ No new skills can be dispatched while kill-switch is active
- ✅ Kill-switch state persists across process restarts (stored in state file)
- ✅ CLI commands are accessible and provide clear feedback
- ✅ All kill-switch events are logged with full context

**Integration Points**:
- `src/dispatcher/skill_dispatcher.py`: Check kill-switch before dispatch
- `src/dispatcher/cli.py`: Implement kill-switch CLI commands
- `src/observer/.observer_state.json`: Persist kill-switch state
- `src/dispatcher/logger.py`: Log all kill-switch events

**Files to Create/Modify**:
- Create: `src/dispatcher/kill_switch.py` (implements emergency stop mechanism)
- Create: `src/dispatcher/cli.py` (CLI interface for kill-switch)
- Modify: `src/dispatcher/skill_dispatcher.py` (check kill-switch before execution)
- Modify: `src/observer/.observer_state.json` (add kill_switch_active field)

### Safety Mechanism Interaction

These three mechanisms work together to provide layered protection:

1. **First Layer - Debouncing**: Prevents rapid repeated triggers of the same pattern
2. **Second Layer - Execution Depth**: Prevents deep cascading chains even if patterns are different
3. **Third Layer - Kill Switch**: Manual override for emergency situations

**Combined Example Scenario**:
- Error log appears → Pattern matched (debounce allows first trigger)
- Skill A executes (depth = 1) → Creates log that triggers Skill B
- Skill B executes (depth = 2) → Creates log that triggers Skill C
- Skill C executes (depth = 3) → Creates log that would trigger Skill D
- **Depth limit reached** → Skill D dispatch is rejected
- If rapid cascades continue, operator can activate **kill-switch** to stop everything

## Concurrency & Atomicity Controls

To ensure thread-safe operations and prevent race conditions in concurrent skill dispatching scenarios, we implement atomic locking and state management mechanisms:

### 1. Thread-Safe Lock Manager (File-Based Locking)

**Purpose**: Prevent concurrent modifications to shared state and ensure atomic skill dispatch operations.

**Implementation Approach**:
- Use file-based locking with `fcntl` (POSIX) for cross-process/thread synchronization
- Create a dedicated lock file: `locks/dispatcher.lock`
- Implement lock acquisition before any critical operations:
  - Skill dispatch decision (read counter + pattern check)
  - Execution counter increment/decrement
  - Debounce cache updates
  - Kill-switch state changes
- Use context managers for automatic lock release (even on exceptions)
- Implement timeout mechanism (default: 5 seconds) to prevent deadlocks
- Log all lock acquisitions and releases for debugging

**Acceptance Criteria**:
- ✅ Only one thread/process can hold the lock at a time
- ✅ Lock is automatically released even if skill execution fails
- ✅ Timeout prevents indefinite blocking (raises LockTimeoutError)
- ✅ Lock works across multiple processes (for distributed scenarios)
- ✅ Lock acquisition/release is logged with timestamps

**Integration Points**:
- `src/dispatcher/skill_dispatcher.py`: Acquire lock before dispatch decision
- `src/dispatcher/event_detector.py`: Acquire lock before cache updates
- `src/dispatcher/kill_switch.py`: Acquire lock before state changes
- `src/dispatcher/execution_context.py`: Acquire lock for counter operations

**Files to Create/Modify**:
- Create: `src/dispatcher/lock_manager.py` (implements file-based locking with fcntl)
- Create: `locks/dispatcher.lock` (lock file, initially empty)
- Modify: All dispatcher components to use lock manager

**Implementation Example**:
```python
# src/dispatcher/lock_manager.py
import fcntl
import time
from contextlib import contextmanager

class LockManager:
    def __init__(self, lock_file_path="locks/dispatcher.lock"):
        self.lock_file_path = lock_file_path
        self.lock_file = None

    @contextmanager
    def acquire(self, timeout=5):
        """Acquire lock with timeout"""
        self.lock_file = open(self.lock_file_path, 'w')
        start_time = time.time()

        while True:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                yield  # Lock acquired
                break
            except IOError:
                if time.time() - start_time > timeout:
                    raise LockTimeoutError("Failed to acquire lock")
                time.sleep(0.1)

        fcntl.flock(self.lock_file, fcntl.LOCK_UN)
        self.lock_file.close()
```

### 2. Atomic File Writes (Global Execution Counter) - MVP Implementation

**Purpose**: Prevent state corruption when multiple processes read/write the execution counter simultaneously.

**Phase 1 (MVP) Implementation**:
- Store execution counter in `.state/global_counter.json`
- Use atomic write pattern with file locking:
  1. Acquire file lock using `fcntl`
  2. Read current counter value
  3. Modify counter (increment/decrement)
  4. Write directly to file (simple approach for single-process)
  5. Release file lock
- Single-process deployment only (no instance tracking in MVP)

**Phase 2 Enhancement** (Deferred):
- Track per-instance state for distributed scenarios
- Each instance has unique `instance_id` (UUID generated on startup)
- Counter file stores: `{"global_depth": 2, "instances": {"inst-123": 1, "inst-456": 1}}`
- Global depth = sum of all instance depths
- Implement write-ahead logging for counter changes (crash recovery)

**Acceptance Criteria (Phase 1 - MVP)**:
- ✅ Counter reads/writes are atomic (no partial updates visible)
- ✅ Single process can safely update counter with file locking
- ✅ Counter survives process crashes (persisted to disk)

**Acceptance Criteria (Phase 2 - Future)**:
- ✅ Multiple processes can safely update counter without corruption
- ✅ Distributed instances maintain consistent global depth
- ✅ Write-ahead log allows recovery from crashes mid-update

**Integration Points**:
- `src/dispatcher/execution_context.py`: Use atomic counter for depth tracking
- `src/dispatcher/lock_manager.py`: Coordinate with file locking
- `src/observer/.observer_state.json`: Store instance_id for distributed tracking

**Files to Create/Modify**:
- Create: `src/dispatcher/atomic_counter.py` (implements atomic counter operations)
- Create: `.state/global_counter.json` (counter state file)
- Create: `.state/counter_wal.log` (write-ahead log for recovery)
- Modify: `src/dispatcher/execution_context.py` (use atomic counter)

**Implementation Example**:
```python
# src/dispatcher/atomic_counter.py
import json
import os
import fcntl

class AtomicCounter:
    def __init__(self, state_file=".state/global_counter.json", instance_id=None):
        self.state_file = state_file
        self.instance_id = instance_id or self._generate_instance_id()

    def increment(self):
        """Atomically increment counter for this instance"""
        with open(self.state_file, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            state = json.load(f)
            state['instances'][self.instance_id] = state['instances'].get(self.instance_id, 0) + 1
            state['global_depth'] = sum(state['instances'].values())

            # Write to temp file first
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, 'w') as tmp:
                json.dump(state, tmp)

            # Atomic rename
            os.rename(temp_file, self.state_file)
            fcntl.flock(f, fcntl.LOCK_UN)

        return state['global_depth']
```

### 3. Event Hashing (Duplicate Prevention)

**Purpose**: Prevent duplicate skill execution when identical events are processed concurrently (Edge Case 2.1 and 2.4).

**Implementation Approach**:
- Generate unique fingerprint for each incoming event:
  - Hash = SHA256(pattern_id + log_content + timestamp_window)
  - Timestamp window: round to nearest 5 seconds (groups near-simultaneous events)
- Maintain in-memory hash set of "currently processing" events:
  - Before processing: Check if hash exists in set
  - If exists: Discard event (already being processed)
  - If not: Add hash to set, process event, remove hash after completion
- Persist hash set to disk every 10 seconds (for crash recovery)
- Clean up old hashes (older than debounce window) every minute
- Use atomic set operations with thread lock for hash additions/removals

**Acceptance Criteria**:
- ✅ Identical events arriving concurrently only trigger skill once
- ✅ Hash set is thread-safe (atomic add/remove operations)
- ✅ Hash set is bounded in size (automatic cleanup of old entries)
- ✅ System handles hash collisions gracefully (use full SHA256, not truncated)
- ✅ Persisted hash set allows recovery from crashes

**Integration Points**:
- `src/dispatcher/event_detector.py`: Generate hash and check for duplicates
- `src/dispatcher/debouncer.py`: Coordinate with time-window debouncing
- `src/dispatcher/lock_manager.py`: Use lock for hash set operations

**Files to Create/Modify**:
- Create: `src/dispatcher/event_hasher.py` (implements hashing and deduplication)
- Create: `.state/processing_hashes.json` (persisted hash set)
- Modify: `src/dispatcher/event_detector.py` (add hash check before queuing)

**Implementation Example**:
```python
# src/dispatcher/event_hasher.py
import hashlib
import json
import threading
import time

class EventHasher:
    def __init__(self, state_file=".state/processing_hashes.json"):
        self.state_file = state_file
        self.processing_hashes = set()
        self.lock = threading.Lock()
        self._load_state()

    def generate_hash(self, pattern_id, log_content):
        """Generate SHA256 hash for event"""
        timestamp_window = int(time.time() / 5) * 5  # Round to 5-second window
        hash_input = f"{pattern_id}:{log_content}:{timestamp_window}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def is_duplicate(self, event_hash):
        """Check if event is currently being processed"""
        with self.lock:
            return event_hash in self.processing_hashes

    def mark_processing(self, event_hash):
        """Mark event as being processed"""
        with self.lock:
            self.processing_hashes.add(event_hash)
            self._persist_state()

    def mark_completed(self, event_hash):
        """Remove event from processing set"""
        with self.lock:
            self.processing_hashes.discard(event_hash)
            self._persist_state()
```

### 4. Distributed Instance Protection (Edge Case 2.6) - **PHASE 2 ONLY**

**Purpose**: Prevent bypassing safety limits when multiple observer instances run simultaneously.

**Status**: ⚠️ **DEFERRED TO PHASE 2** - Not included in MVP

**Phase 2 Implementation Approach**:
- Assign unique `instance_id` to each observer process (UUID generated on startup)
- Store instance registry in shared state file: `.state/instance_registry.json`
- Each instance reports its state (alive, last_heartbeat, active_skills count)
- Implement heartbeat mechanism:
  - Each instance updates its heartbeat every 10 seconds
  - Instances older than 30 seconds are considered dead and removed
- Calculate global execution depth across all live instances:
  - Global depth = sum of depth counters from all live instances
  - Reject skill dispatch if global depth > MAX_DEPTH (even if local depth is 0)
- Implement distributed lock coordination:
  - Use file-based lock that works across processes on same machine
  - For true distributed systems (multiple machines), document requirement for Redis or similar

**Acceptance Criteria**:
- ✅ Multiple observer instances maintain consistent global execution depth
- ✅ Dead instances are automatically detected and removed from registry
- ✅ Skill dispatch is rejected if global depth exceeds limit
- ✅ System works correctly on single machine with multiple processes
- ✅ Documentation clearly states limitations for multi-machine deployments

**Integration Points**:
- `src/dispatcher/execution_context.py`: Check global depth across instances
- `src/observer/main.py`: Register instance on startup, send heartbeats
- `.state/instance_registry.json`: Store registry of active instances

**Files to Create/Modify**:
- Create: `src/dispatcher/instance_manager.py` (manages instance registry and heartbeats)
- Create: `.state/instance_registry.json` (registry of active instances)
- Modify: `src/dispatcher/execution_context.py` (check global depth)
- Modify: `src/observer/main.py` (register instance and send heartbeats)

**Multi-Machine Limitation**:
For deployments across multiple machines, file-based locking is insufficient. Document upgrade path:
- Option 1: Use Redis with distributed locks and atomic counters
- Option 2: Use ZooKeeper for distributed coordination
- Option 3: Use database with row-level locking (PostgreSQL)

For MVP, focus on single-machine multi-process support using file-based locks.

### Concurrency Control Interaction

These mechanisms work together to provide comprehensive race condition protection:

1. **Lock Manager**: Ensures only one process modifies state at a time
2. **Atomic Counter**: Guarantees counter integrity even during crashes
3. **Event Hashing**: Prevents duplicate processing of concurrent identical events
4. **Instance Manager**: Maintains global view across distributed instances

**Combined Example Scenario (Race Condition Prevention)**:
- Event A and Event B (identical) arrive simultaneously
- Both generate same hash (SHA256 of pattern + content + time window)
- Event A: Hash check → Not in set → Acquire lock → Add to hash set → Process
- Event B: Hash check → Already in set → Discard immediately (no lock needed)
- Event A completes: Remove hash from set → Release lock
- Result: Only one skill execution despite concurrent identical events

## Success Criteria

### Functional Requirements
- ✅ Events can be mapped to specific skills via configuration
- ✅ Skills are automatically executed when events are detected
- ✅ All dispatch activities are properly logged with 90-day retention
- ✅ System handles errors gracefully with fallback mechanisms
- ✅ Performance impact is minimal (<5% overhead on observer)
- ✅ Recursion depth is enforced (max 3 levels)
- ✅ Pattern debouncing prevents rapid-fire triggers
- ✅ Kill-switch can stop all skills within 5 seconds

### Constitutional Compliance Checklist

#### ✅ HITL Safeguards (Constitution Article II)
- [x] High-risk skills require human approval before execution
- [x] Approval requests include risk assessment and potential impact
- [x] User can approve/reject via CLI or file update
- [x] Timeout handling respects `auto_approve_on_timeout` flag
- [x] All approval decisions are logged with user identity

#### ✅ Security Requirements (Constitution Privacy & Security)
- [x] Skill allowlist enforced (`config/allowed_skills.yaml`)
- [x] Regex patterns validated to prevent ReDoS attacks
- [x] Kill-switch protected by authentication token
- [x] No plaintext credentials in logs or config files
- [x] Sensitive data redacted from log content
- [x] Environment variables used for sensitive configuration

#### ✅ Logging & Audit Trail (Constitution Privacy & Security)
- [x] 90-day minimum retention for all dispatcher logs
- [x] Critical events (kill-switch, approvals) archived for 1 year
- [x] All external skill executions logged with timestamps
- [x] Log rotation at midnight daily
- [x] Compressed storage for logs older than 7 days

#### ✅ Error Recovery & Graceful Degradation (Constitution Article VI)
- [x] Atomic counter operations prevent state corruption
- [x] File-based locking ensures consistency
- [x] Kill-switch provides emergency fallback
- [x] Failed skill executions don't crash the dispatcher
- [x] Lock timeout prevents deadlocks (5-second max)

#### ✅ Local-First Data Sovereignty (Constitution Article V)
- [x] All state stored locally in `.state/` directory
- [x] No external dependencies for core functionality
- [x] File-based locking (no cloud services required)
- [x] Approval requests stored locally in `.approvals/`

#### ✅ Smallest Viable Change (Constitution Article III)
- [x] Phase 1 (MVP) focuses on single-process deployment
- [x] Advanced features (distributed, WAL) deferred to Phase 2
- [x] Core safety mechanisms (HITL, security) included in MVP
- [x] MVP can be validated before adding complexity

### Acceptance Tests
1. **HITL Test**: Trigger high-risk skill → Verify approval request created → Approve → Verify skill executes
2. **Security Test**: Attempt to execute skill not in allowlist → Verify rejection → Log unauthorized attempt
3. **Recursion Test**: Create cascading error logs → Verify execution stops at depth 3 → No infinite loop
4. **Kill-Switch Test**: Activate kill-switch during skill execution → Verify all skills stop within 5 seconds
5. **Debounce Test**: Generate identical events rapidly → Verify only first event triggers skill (within 30s window)
6. **Log Retention Test**: Run dispatcher for 91 days → Verify logs older than 90 days are cleaned up
7. **Authorization Test**: Attempt kill-switch without token → Verify rejection and security log entry