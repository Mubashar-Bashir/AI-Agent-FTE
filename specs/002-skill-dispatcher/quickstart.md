# Quickstart Guide: Autonomous Skill Dispatcher

## Overview
The Autonomous Skill Dispatcher enables automatic execution of skills when specific events are detected in monitored files or logs. This guide will walk you through setting up and using the dispatcher.

## Prerequisites
- Workspace Observer infrastructure is running
- Python 3.11+ with required dependencies installed
- Access to the skill framework

## Installation

1. Ensure the Workspace Observer is properly configured and running
2. Verify that the skill framework is accessible
3. Install additional dependencies if needed:
   ```bash
   pip install -r requirements-dispatcher.txt
   ```

## Configuration

### 1. Set up Dispatcher Configuration
Create or update the dispatcher configuration file (`config/dispatcher.yaml`):

```yaml
dispatcher:
  enabled: true
  max_concurrent_dispatches: 3
  throttle_interval_ms: 1000
  retry_attempts: 2
  retry_delay_ms: 5000
  recursion_depth_limit: 3
  log_level: info
```

### 2. Define Event-to-Skill Mappings
Create event trigger configurations in `config/event-triggers.json`:

```json
[
  {
    "name": "error-detection",
    "event_type": "error",
    "pattern": "ERROR|Exception|Traceback",
    "skill_to_invoke": "systematic-debugging",
    "enabled": true,
    "priority": 5
  },
  {
    "name": "performance-warning",
    "event_type": "warning",
    "pattern": "slow|timeout|performance",
    "skill_to_invoke": "optimization-advisor",
    "enabled": true,
    "priority": 10
  }
]
```

## Usage

### Starting the Dispatcher
1. Ensure the Workspace Observer is running with file monitoring enabled
2. Start the dispatcher service:
   ```bash
   python -m dispatcher.main
   ```

### Registering New Triggers
Use the API to register new event triggers:

```bash
curl -X POST http://localhost:8000/api/dispatcher/register-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "name": "syntax-error-handler",
    "event_type": "error",
    "pattern": "SyntaxError|IndentationError",
    "skill_to_invoke": "code-fix",
    "enabled": true
  }'
```

### Monitoring Dispatcher Status
Check the current status of the dispatcher:

```bash
curl http://localhost:8000/api/dispatcher/status
```

### Viewing Dispatch Records
View recent dispatch records:

```bash
curl "http://localhost:8000/api/dispatcher/dispatches?limit=10"
```

## Common Use Cases

### 1. Error Detection and Debugging
Automatically trigger debugging skills when errors are detected in logs:
- Pattern: `ERROR.*Database|ConnectionError|TimeoutError`
- Skill: `systematic-debugging`

### 2. Performance Monitoring
Trigger optimization advice when performance warnings appear:
- Pattern: `slow query|memory leak|high cpu`
- Skill: `performance-analyzer`

### 3. Code Quality Issues
Automatically run code improvement skills when quality issues are detected:
- Pattern: `TODO|FIXME|HACK|refactor`
- Skill: `code-improver`

## Security Considerations

1. **Skill Whitelist**: Only allow approved skills to be executed automatically
2. **Parameter Validation**: Ensure all parameters passed to skills are validated
3. **Rate Limiting**: Prevent excessive skill execution that could overwhelm the system
4. **Recursion Prevention**: Avoid infinite loops where skills trigger more events

## Troubleshooting

### Dispatcher Not Responding to Events
- Check that the Workspace Observer is monitoring the correct files
- Verify that event patterns are correctly defined
- Ensure the target skills exist and are accessible

### Too Many False Positives
- Refine event patterns to be more specific
- Adjust trigger priorities to resolve conflicts
- Consider adding additional conditions to triggers

### Performance Issues
- Reduce the number of active triggers
- Increase throttle intervals
- Limit concurrent dispatches

### Failed Skill Executions
- Check dispatcher logs for error details
- Verify that target skills are properly configured
- Ensure sufficient resources are available for skill execution

## Best Practices

1. **Start Simple**: Begin with a few well-defined triggers before expanding
2. **Monitor Performance**: Keep track of dispatch frequency and system load
3. **Regular Review**: Periodically review and refine event patterns
4. **Logging**: Maintain detailed logs of all dispatch activities
5. **Testing**: Test new triggers in a safe environment before deploying to production