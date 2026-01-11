# Data Model: Autonomous Skill Dispatcher

## Entities

### EventTrigger
**Description**: Defines a pattern that triggers skill execution when matched in monitored logs/files

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier for the trigger | Required, UUID format |
| name | string | Human-readable name for the trigger | Required, max 100 chars |
| event_type | string | Type of event to monitor (error, warning, info, etc.) | Required, predefined enum |
| pattern | string | Regex pattern to match in logs | Required, valid regex |
| skill_to_invoke | string | Name of the skill to execute when pattern matches | Required, valid skill name |
| conditions | object | Additional conditions for triggering | Optional, key-value pairs |
| enabled | boolean | Whether this trigger is active | Required, default true |
| priority | integer | Priority level for resolving conflicts (lower = higher priority) | Optional, default 10 |
| created_at | datetime | Timestamp when trigger was created | Auto-generated |
| updated_at | datetime | Timestamp when trigger was last updated | Auto-generated |

### SkillDispatchRecord
**Description**: Records each skill dispatch event for observability and debugging

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier for the dispatch record | Required, UUID format |
| timestamp | datetime | When the dispatch occurred | Required, auto-generated |
| trigger_id | string | ID of the trigger that caused this dispatch | Required, foreign key to EventTrigger |
| trigger_event | object | Details of the triggering event (file, line, content) | Required |
| skill_invoked | string | Name of the skill that was executed | Required |
| parameters | object | Parameters passed to the skill | Optional |
| status | string | Execution status (pending, success, failure, timeout) | Required, predefined enum |
| execution_log | string | Output from skill execution | Optional, max 10000 chars |
| duration_ms | integer | Time taken for skill execution in milliseconds | Optional |
| error_message | string | Error message if execution failed | Optional, max 1000 chars |

### DispatcherConfig
**Description**: Configuration settings for the dispatcher system

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier for config | Required, UUID format |
| enabled | boolean | Whether the dispatcher is enabled | Required, default true |
| max_concurrent_dispatches | integer | Maximum number of concurrent skill executions | Optional, default 3 |
| throttle_interval_ms | integer | Minimum time between dispatches | Optional, default 1000 |
| retry_attempts | integer | Number of retry attempts for failed dispatches | Optional, default 2 |
| retry_delay_ms | integer | Delay between retry attempts | Optional, default 5000 |
| recursion_depth_limit | integer | Maximum depth of nested skill calls | Optional, default 3 |
| log_level | string | Logging level (debug, info, warning, error) | Optional, default "info" |
| created_at | datetime | Timestamp when config was created | Auto-generated |
| updated_at | datetime | Timestamp when config was last updated | Auto-generated |

### AllowedSkill
**Description**: Whitelist of skills that can be automatically executed by the dispatcher

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier for the entry | Required, UUID format |
| skill_name | string | Name of the skill | Required, valid skill name |
| allowed | boolean | Whether this skill is allowed for auto-execution | Required, default true |
| reason | string | Reason why this skill is allowed/disallowed | Optional, max 500 chars |
| created_at | datetime | Timestamp when entry was created | Auto-generated |

## Relationships

1. **EventTrigger** 1 --- * **SkillDispatchRecord**: One trigger can cause multiple dispatch records
2. **DispatcherConfig** 1 --- 1 **ActiveConfig**: Only one active configuration at a time
3. **AllowedSkill** * --- * **EventTrigger**: Multiple allowed skills can be referenced by multiple triggers

## State Transitions

### SkillDispatchRecord Status Transitions
```
PENDING -> SUCCESS
PENDING -> FAILURE
PENDING -> TIMEOUT
FAILURE -> PENDING (on retry)
TIMEOUT -> PENDING (on retry)
```

### EventTrigger Enabled Transitions
```
ENABLED <-> DISABLED
```

## Validation Rules

1. **EventTrigger**:
   - Pattern must be a valid regular expression
   - skill_to_invoke must be in the AllowedSkill whitelist
   - priority must be between 0 and 100

2. **SkillDispatchRecord**:
   - Duration must be positive if provided
   - Status must be one of the predefined values

3. **DispatcherConfig**:
   - max_concurrent_dispatches must be between 1 and 10
   - throttle_interval_ms must be between 100 and 60000
   - retry_attempts must be between 0 and 5
   - recursion_depth_limit must be between 1 and 10

## Indexes

1. **EventTrigger**: Index on (enabled, priority) for efficient lookup
2. **SkillDispatchRecord**: Index on (timestamp, trigger_id) for chronological queries
3. **SkillDispatchRecord**: Index on (status, timestamp) for status-based queries
4. **AllowedSkill**: Index on (skill_name, allowed) for fast validation

## Constraints

1. **EventTrigger**: Unique constraint on name within enabled triggers
2. **DispatcherConfig**: Only one configuration can have enabled=true at any time
3. **AllowedSkill**: Unique constraint on skill_name