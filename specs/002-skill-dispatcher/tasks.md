---
description: "Task list for Autonomous Skill Dispatcher implementation"
---

# Tasks: Autonomous Skill Dispatcher

**Input**: Design documents from `/specs/002-skill-dispatcher/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, quickstart.md

**Tests**: Tests are NOT explicitly requested in the spec.md, so test tasks are OMITTED per template instructions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure with `src/dispatcher/` for dispatcher components
- Configuration in `config/`
- State files in `.state/`
- Approval requests in `.approvals/`
- Logs in `logs/dispatcher/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic directory structure

- [ ] T001 Create dispatcher directory structure (src/dispatcher/, config/, .state/, .approvals/, locks/, logs/dispatcher/)
- [ ] T002 [P] Create requirements-dispatcher.txt with Python 3.11+ dependencies (watchdog, PyYAML, pathlib)
- [ ] T003 [P] Initialize config/dispatcher_config.yaml with default settings (max_concurrent_dispatches=3, recursion_depth_limit=3)
- [ ] T004 [P] Initialize config/allowed_skills.yaml with empty skills list and validation schema
- [ ] T005 [P] Initialize config/event_triggers.yaml with sample error detection pattern
- [ ] T006 [P] Create locks/dispatcher.lock as empty file for file-based locking
- [ ] T007 [P] Create .state/global_counter.json with initial state {"global_depth": 0, "instances": {}}
- [ ] T008 [P] Create logs/dispatcher/.gitkeep to ensure logs directory exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Implement LockManager in src/dispatcher/lock_manager.py with fcntl-based file locking and 5-second timeout
- [ ] T010 [P] Implement ConfigManager in src/dispatcher/config_manager.py with YAML loading, reload support, and validation
- [ ] T011 [P] Implement ExecutionLogger in src/dispatcher/logger.py with 90-day retention, daily rotation, and gzip compression
- [ ] T012 [P] Implement RegexValidator in src/dispatcher/regex_validator.py with ReDoS prevention rules (max length 200, depth < 5)
- [ ] T013 Implement AtomicCounter in src/dispatcher/atomic_counter.py with file-based state persistence and fcntl locking
- [ ] T014 [P] Implement EventHasher in src/dispatcher/event_hasher.py with SHA256 hashing and time-window deduplication
- [ ] T015 [P] Create base DispatcherException hierarchy in src/dispatcher/exceptions.py (LockTimeoutError, UnauthorizedError, DepthLimitError)
- [ ] T016 Create DispatcherState model in src/dispatcher/models.py with global_execution_depth, kill_switch_active, instance_id fields

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automatic Error Detection and Skill Triggering (Priority: P1) 🎯 MVP

**Goal**: System automatically detects error patterns in log files and triggers configured skills without manual intervention

**Independent Test**: Create a test log file with "TypeError: 'NoneType' object has no attribute 'process'", verify pattern is detected, and confirm systematic-debugging skill is queued for execution

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create EventTrigger model in src/dispatcher/models.py with event_type, pattern, skill_to_invoke, risk_level, enabled fields
- [ ] T018 [P] [US1] Create SkillDispatchRecord model in src/dispatcher/models.py with id, timestamp, trigger_event, skill_invoked, result, execution_log fields
- [ ] T019 [US1] Implement EventDetector in src/dispatcher/event_detector.py with pattern matching and event queue management
- [ ] T020 [US1] Implement Debouncer in src/dispatcher/debouncer.py with 30-second time-window caching using LRU cache
- [ ] T021 [US1] Integrate EventHasher with EventDetector in src/dispatcher/event_detector.py to prevent duplicate processing
- [ ] T022 [US1] Integrate Debouncer with EventDetector in src/dispatcher/event_detector.py for pattern suppression
- [ ] T023 [US1] Implement SkillDispatcher core in src/dispatcher/skill_dispatcher.py with basic skill invocation logic
- [ ] T024 [US1] Add ConfigManager integration to EventDetector in src/dispatcher/event_detector.py for loading event triggers from config/event_triggers.yaml
- [ ] T025 [US1] Add ExecutionLogger integration to SkillDispatcher in src/dispatcher/skill_dispatcher.py for logging all dispatch events
- [ ] T026 [US1] Create main dispatcher entry point in src/dispatcher/main.py that initializes EventDetector and SkillDispatcher

**Checkpoint**: At this point, User Story 1 should be fully functional - errors automatically detected and skills triggered with debouncing

---

## Phase 4: User Story 2 - Human Approval for High-Risk Skills (Priority: P1)

**Goal**: High-risk skills (code modifications, file deletions) require explicit human approval before execution to maintain control over destructive operations

**Independent Test**: Trigger a high-risk skill (systematic-debugging with risk_level=high), verify approval request is created in .approvals/ directory, approve via CLI command, confirm skill executes only after approval

### Implementation for User Story 2

- [ ] T027 [P] [US2] Create HITLApprovalRequest model in src/dispatcher/models.py with request_id, risk_assessment, recommended_action, status, expires_at fields
- [ ] T028 [P] [US2] Implement HITLApprovalManager in src/dispatcher/hitl_approval_manager.py with approval request creation and file-based storage
- [ ] T029 [US2] Implement approval request file generation in src/dispatcher/hitl_approval_manager.py creating .approvals/pending_{request_id}.json with risk assessment
- [ ] T030 [US2] Implement approval response parsing in src/dispatcher/hitl_approval_manager.py to detect approve/reject decisions from file updates
- [ ] T031 [US2] Implement timeout handling in src/dispatcher/hitl_approval_manager.py respecting auto_approve_on_timeout flag (default: reject)
- [ ] T032 [US2] Create CLI commands module in src/dispatcher/cli_commands.py with approve/reject/status command implementations
- [ ] T033 [US2] Integrate HITLApprovalManager with SkillDispatcher in src/dispatcher/skill_dispatcher.py to check risk_level and requires_approval flags
- [ ] T034 [US2] Add approval decision logging to ExecutionLogger in src/dispatcher/logger.py with user identity and timestamp
- [ ] T035 [US2] Implement approval request cleanup in src/dispatcher/hitl_approval_manager.py to remove processed requests after 24 hours
- [ ] T036 [US2] Update config/allowed_skills.yaml schema to include risk_level and requires_approval fields per skill

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - automatic detection with HITL approval for high-risk skills

---

## Phase 5: User Story 3 - Recursion Prevention (Priority: P1)

**Goal**: System enforces maximum execution depth of 3 to prevent infinite loops where skills trigger cascading skills

**Independent Test**: Create a cascade scenario (Skill A creates log triggering Skill B, which creates log triggering Skill C, which triggers Skill D), verify execution stops at depth 3 and Skill D is rejected with "Max execution depth exceeded" error

### Implementation for User Story 3

- [ ] T037 [P] [US3] Implement ExecutionContext in src/dispatcher/execution_context.py to track execution depth and parent-child skill chains
- [ ] T038 [US3] Implement depth counter increment logic in src/dispatcher/execution_context.py using AtomicCounter before skill execution
- [ ] T039 [US3] Implement depth counter decrement logic in src/dispatcher/execution_context.py using finally block to ensure cleanup even on failures
- [ ] T040 [US3] Implement depth limit check in src/dispatcher/skill_dispatcher.py before skill dispatch (reject if depth > 3)
- [ ] T041 [US3] Add execution chain logging to ExecutionLogger in src/dispatcher/logger.py showing parent → child → grandchild relationships
- [ ] T042 [US3] Integrate ExecutionContext with SkillDispatcher in src/dispatcher/skill_dispatcher.py to track context per skill invocation
- [ ] T043 [US3] Add DepthLimitError exception handling in src/dispatcher/skill_dispatcher.py to log and reject skills exceeding depth limit
- [ ] T044 [US3] Update .state/global_counter.json persistence in src/dispatcher/atomic_counter.py to track per-instance depth for distributed scenarios

**Checkpoint**: All P1 user stories (1, 2, 3) should now be independently functional with full safety controls

---

## Phase 6: User Story 4 - Emergency Kill-Switch (Priority: P2)

**Goal**: Operators can immediately stop all active skill executions via CLI command for emergency situations or unexpected behavior

**Independent Test**: Start a long-running skill, activate kill-switch via `dispatcher kill-switch activate`, verify all skills stop within 5 seconds and no new skills can be dispatched until deactivation

### Implementation for User Story 4

- [ ] T045 [P] [US4] Implement KillSwitch in src/dispatcher/kill_switch.py with activate/deactivate/status methods and state persistence
- [ ] T046 [US4] Implement kill-switch authentication in src/dispatcher/kill_switch.py checking DISPATCHER_ADMIN_TOKEN environment variable
- [ ] T047 [US4] Add kill-switch state persistence to .state/global_counter.json in src/dispatcher/kill_switch.py
- [ ] T048 [US4] Implement skill termination logic in src/dispatcher/kill_switch.py sending termination signals to all active skills
- [ ] T049 [US4] Create CLI kill-switch commands in src/dispatcher/cli_commands.py (activate, deactivate, status)
- [ ] T050 [US4] Integrate KillSwitch check into SkillDispatcher in src/dispatcher/skill_dispatcher.py to reject dispatches when active
- [ ] T051 [US4] Add kill-switch event logging to ExecutionLogger in src/dispatcher/logger.py with timestamp, user, and reason
- [ ] T052 [US4] Implement kill-switch override for pending approvals in src/dispatcher/hitl_approval_manager.py to reject with "Kill-switch override" status
- [ ] T053 [US4] Add UnauthorizedError handling in src/dispatcher/cli_commands.py for failed authentication attempts with security logging

**Checkpoint**: User Stories 1-4 should work together - automatic detection, approval, recursion prevention, and emergency stop

---

## Phase 7: User Story 5 - Security Allowlist Enforcement (Priority: P2)

**Goal**: Only skills in predefined allowlist can be triggered to prevent unauthorized or malicious skill execution from crafted log patterns

**Independent Test**: Configure allowlist with 2 skills (systematic-debugging, verification-before-completion), attempt to trigger test-driven-development (not in allowlist), verify rejection and confirm security log entry

### Implementation for User Story 5

- [ ] T054 [P] [US5] Create AllowedSkill model in src/dispatcher/models.py with skill_name, risk_level, requires_approval, description fields
- [ ] T055 [US5] Implement allowlist validation in src/dispatcher/config_manager.py loading config/allowed_skills.yaml on startup
- [ ] T056 [US5] Implement skill authorization check in src/dispatcher/skill_dispatcher.py before dispatch (reject if not in allowlist)
- [ ] T057 [US5] Add unauthorized skill attempt logging to ExecutionLogger in src/dispatcher/logger.py with "Unauthorized skill execution attempt" events
- [ ] T058 [US5] Implement config reload support in src/dispatcher/config_manager.py to refresh allowlist without restart when config/allowed_skills.yaml changes
- [ ] T059 [US5] Add allowlist validation to EventDetector in src/dispatcher/event_detector.py to reject triggers for non-allowed skills at detection time
- [ ] T060 [US5] Populate config/allowed_skills.yaml with initial allowed skills (systematic-debugging, verification-before-completion, test-driven-development)
- [ ] T061 [US5] Integrate allowlist enforcement with HITLApprovalManager in src/dispatcher/hitl_approval_manager.py to ensure HITL flow is enforced per skill configuration

**Checkpoint**: User Stories 1-5 should work - full security controls with allowlist, approval, and recursion prevention

---

## Phase 8: User Story 6 - Audit Logging with 90-Day Retention (Priority: P3)

**Goal**: All dispatcher activities are logged with 90-day retention (365 days for critical events) for compliance and incident investigation

**Independent Test**: Trigger various events (skill execution, approval, rejection, kill-switch), verify logs are created in logs/dispatcher/YYYY-MM-DD.log, run cleanup after 91 simulated days, confirm old logs removed while critical events archived

### Implementation for User Story 6

- [ ] T062 [P] [US6] Implement TimedRotatingFileHandler configuration in src/dispatcher/logger.py for daily log rotation at midnight
- [ ] T063 [P] [US6] Implement log retention policy in src/dispatcher/logger.py with 90-day cleanup for standard logs
- [ ] T064 [US6] Implement critical event archival in src/dispatcher/logger.py with 365-day retention for kill-switch and high-risk approval events
- [ ] T065 [US6] Implement log compression in src/dispatcher/logger.py using gzip for logs older than 7 days
- [ ] T066 [US6] Create log cleanup scheduler in src/dispatcher/log_cleanup.py running daily to enforce retention policies
- [ ] T067 [US6] Implement log file size limit in src/dispatcher/logger.py enforcing 100MB max per file before rotation
- [ ] T068 [US6] Add structured logging fields to all log entries in src/dispatcher/logger.py (timestamp, trigger_event, skill_name, result_status, execution_time, user_identity)
- [ ] T069 [US6] Implement sensitive data redaction in src/dispatcher/logger.py to remove credentials and API keys from logged content
- [ ] T070 [US6] Update config/dispatcher_config.yaml with logging configuration (retention_days=90, critical_retention_days=365, max_file_size_mb=100)

**Checkpoint**: All user stories (1-6) should now be independently functional with comprehensive audit logging

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T071 [P] Add comprehensive error handling across all dispatcher modules with specific exception types from src/dispatcher/exceptions.py
- [ ] T072 [P] Implement graceful degradation in src/dispatcher/main.py to continue with previous valid config when new config has errors
- [ ] T073 [P] Add performance monitoring to src/dispatcher/skill_dispatcher.py to track dispatcher overhead and validate <5% CPU/memory impact under 100 events/hour load (NFR-001)
- [ ] T074 [P] Implement stale lock detection in src/dispatcher/lock_manager.py to force-release locks older than 60 seconds
- [ ] T075 [P] Add configuration validation tests in src/dispatcher/config_manager.py to validate config files on startup
- [ ] T076 Add integration with Workspace Observer in src/observer/main.py to connect event detection with file monitoring infrastructure
- [ ] T077 [P] Create dispatcher CLI entry point script in scripts/dispatcher_cli.py for approve/reject/kill-switch/status commands
- [ ] T078 [P] Update quickstart.md with actual CLI commands and configuration examples based on implemented features
- [ ] T079 [P] Add environment variable documentation to quickstart.md for DISPATCHER_ADMIN_TOKEN and other config settings
- [ ] T080 Run quickstart.md validation to ensure all documented workflows work end-to-end
- [ ] T081 [P] [NFR] Implement pattern matching latency test in tests/test_performance.py validating <100ms for 50 patterns (NFR-002)
- [ ] T082 [P] [NFR] Implement throughput load test in tests/test_load.py validating 1000 executions/hour without degradation (NFR-004)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5 → US6)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 SkillDispatcher but independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 SkillDispatcher but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 SkillDispatcher but independently testable
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 EventDetector and SkillDispatcher but independently testable
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Enhances existing logger but independently testable

### Within Each User Story

- Models before services
- Services before integration
- Core implementation before validation/logging enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T008)
- All Foundational tasks marked [P] can run in parallel (T010-T012, T014-T015 within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- All Polish tasks marked [P] can run in parallel (T071-T075, T077-T079)

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task T017: "Create EventTrigger model in src/dispatcher/models.py"
Task T018: "Create SkillDispatchRecord model in src/dispatcher/models.py"

# After models complete, these can run in parallel (different components):
Task T019: "Implement EventDetector in src/dispatcher/event_detector.py"
Task T020: "Implement Debouncer in src/dispatcher/debouncer.py"
Task T023: "Implement SkillDispatcher core in src/dispatcher/skill_dispatcher.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch model and core components together:
Task T027: "Create HITLApprovalRequest model in src/dispatcher/models.py"
Task T028: "Implement HITLApprovalManager in src/dispatcher/hitl_approval_manager.py"
Task T032: "Create CLI commands module in src/dispatcher/cli_commands.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 - All P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Automatic Error Detection)
4. Complete Phase 4: User Story 2 (HITL Approval)
5. Complete Phase 5: User Story 3 (Recursion Prevention)
6. **STOP and VALIDATE**: Test User Stories 1-3 together
7. Deploy/demo Bronze Tier MVP

**Rationale**: US1-US3 are all P1 priority and together provide the core value proposition with essential safety controls (HITL, recursion prevention). This is the minimum viable dispatcher.

### Incremental Delivery Beyond MVP

1. Add User Story 4 (Kill-Switch) → Test independently → Deploy/Demo (Enhanced Safety)
2. Add User Story 5 (Allowlist) → Test independently → Deploy/Demo (Security Hardening)
3. Add User Story 6 (Audit Logging) → Test independently → Deploy/Demo (Compliance Ready)
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Error Detection)
   - Developer B: User Story 2 (HITL Approval)
   - Developer C: User Story 3 (Recursion Prevention)
3. Integrate US1-US3 for MVP validation
4. Continue with US4-US6 in parallel if capacity allows

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All P1 stories (US1-US3) are required for Bronze Tier MVP
- P2 stories (US4-US5) add safety and security hardening
- P3 story (US6) adds compliance and audit capabilities
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Total Task Summary

- **Total Tasks**: 82
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (US1 - Error Detection)**: 10 tasks
- **Phase 4 (US2 - HITL Approval)**: 10 tasks
- **Phase 5 (US3 - Recursion Prevention)**: 8 tasks
- **Phase 6 (US4 - Kill-Switch)**: 9 tasks
- **Phase 7 (US5 - Security Allowlist)**: 8 tasks
- **Phase 8 (US6 - Audit Logging)**: 9 tasks
- **Phase 9 (Polish & NFR Validation)**: 12 tasks

**Parallel Opportunities Identified**: 37+ tasks can run in parallel across different phases

**Independent Test Criteria**:
- US1: Can trigger skills from error patterns autonomously
- US2: Can require and process human approval for high-risk skills
- US3: Can enforce depth limits to prevent recursion
- US4: Can stop all skills immediately via kill-switch
- US5: Can enforce security allowlist and reject unauthorized skills
- US6: Can maintain audit logs with proper retention

**Suggested MVP Scope**: Phases 1-5 (Setup + Foundational + US1 + US2 + US3) = 44 tasks for Bronze Tier MVP with core safety controls
