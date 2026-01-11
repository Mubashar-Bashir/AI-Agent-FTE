# Autonomous Skill Dispatcher

An intelligent system that automatically triggers Claude Code skills when it detects relevant events in logs, code changes, or other system activities.

## 🎯 Overview

The Autonomous Skill Dispatcher is a proactive automation system that bridges the gap between the Workspace Observer and Claude Code skills. It monitors system events and automatically executes appropriate skills to address detected issues or opportunities.

## ✨ Features

### 1. Automatic Error Detection
- Monitors logs for error patterns
- Automatically triggers debugging skills for common errors
- Supports customizable error patterns

### 2. Human-in-the-Loop (HITL) Approval
- High-risk skills require explicit approval
- Console notifications for pending approvals
- Timeout handling with configurable policies
- Detailed risk assessment for each request

### 3. Recursion Prevention
- Execution depth tracking (max 3 levels by default)
- Atomic counter with file-based persistence
- Thread-safe operation with fcntl locking

### 4. Kill-Switch Mechanism
- Emergency stop for all skill executions
- Token-based authorization
- Audit logging for all kill-switch events

### 5. Security Controls
- Skill allowlist with risk classification
- Regex validation to prevent ReDoS attacks
- Skill name injection protection

### 6. Comprehensive Audit Logging
- 90-day standard retention
- 365-day critical event retention
- Daily log rotation
- Automatic compression of old logs

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Workspace   │────▶│ Skill Dispatcher │────▶│ Claude Code     │
│   Observer    │    │                  │    │ Skills          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │   Event Triggers │
                       │   Configuration  │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Claude Code environment

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Dig-AI-FTE
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Configure the dispatcher by modifying the files in the `config/` directory:

#### `config/dispatcher_config.yaml`
```yaml
dispatcher:
  max_concurrent_dispatches: 3
  recursion_depth_limit: 3
  
logging:
  retention_days: 90
  critical_retention_days: 365
  max_file_size_mb: 100

debouncing:
  time_window_seconds: 30
  cache_size_limit: 1000
```

#### `config/allowed_skills.yaml`
```yaml
skills:
  - name: "systematic-debugging"
    risk_level: "medium"
    requires_approval: false
    description: "Analyzes errors and proposes fixes"

  - name: "test-driven-development"
    risk_level: "high"
    requires_approval: true
    description: "Creates and modifies tests"

  - name: "verification-before-completion"
    risk_level: "low"
    requires_approval: false
    description: "Runs verification commands"
```

#### `config/event_triggers.yaml`
```yaml
triggers:
  - id: "error-detection"
    name: "Error Detection"
    event_type: "error"
    pattern: "ERROR:.*|CRITICAL:.*|TypeError:.*|AttributeError:.*"
    skill_to_invoke: "systematic-debugging"
    enabled: true
    priority: 10
    risk_level: "medium"
    requires_approval: false
    debounce_seconds: 30

  - id: "test-failure"
    name: "Test Failure Detection"
    event_type: "test_failure"
    pattern: "FAILED.*test_|AssertionError|pytest.*failed"
    skill_to_invoke: "test-driven-development"
    enabled: true
    priority: 20
    risk_level: "high"
    requires_approval: true
    debounce_seconds: 60
```

### Running the Dispatcher

```bash
python -m src.dispatcher.main
```

## 🔧 Usage

### Manual Skill Triggering

```python
from src.dispatcher.integration import ObserverIntegration

# Initialize and integrate with observer
integration = ObserverIntegration(dispatcher_main_instance)
integration.start_monitoring()

# Or trigger manually
record = integration.trigger_skill_manually("systematic-debugging", {
    "problem_description": "TypeError in user authentication"
})
```

### CLI Commands

#### Approval Management
```bash
# Approve a pending request
python src/dispatcher/cli_commands.py approve <request_id> --comment "Approved for critical fix"

# Reject a request
python src/dispatcher/cli_commands.py reject <request_id> --reason "Too risky for production"

# Check status
python src/dispatcher/cli_commands.py status
```

#### Kill-Switch Management
```bash
# Activate kill-switch (requires admin token)
python src/dispatcher/cli_commands.py kill-switch activate --reason "Security incident"

# Deactivate kill-switch
python src/dispatcher/cli_commands.py kill-switch deactivate --reason "Issue resolved"

# Check kill-switch status
python src/dispatcher/cli_commands.py kill-switch status
```

## 🛡️ Security

### Skill Allowlist
All skills must be explicitly allowed in `config/allowed_skills.yaml`. Unauthorized skill attempts are logged and rejected.

### Risk Classification
Skills are classified by risk level:
- **Low**: Read-only operations, analysis
- **Medium**: Automated fixes with limited scope
- **High**: Code modifications, file creation/deletion, external API calls

### Injection Protection
- Skill name validation prevents path traversal and shell injection
- Regex pattern validation prevents ReDoS attacks

### Authorization
- Kill-switch requires admin token
- Approval requests include detailed risk assessment

## 📊 Logging & Monitoring

### Log Structure
- `logs/dispatcher/` - Main dispatcher logs
- `.approvals/` - Pending approval requests
- `.state/` - Execution state and counters
- `locks/` - File-based locks

### Retention Policy
- Standard logs: 90 days
- Critical events: 365 days
- Automatic rotation and compression

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Individual tests:
```bash
python test_dispatcher_us1.py    # User Story 1: Error Detection
python test_hitl_and_killswitch.py  # User Stories 2 & 4: Approval & Kill-Switch
python test_recursion_prevention.py  # User Story 3: Recursion Prevention
python test_security_allowlist.py    # User Story 5: Security Allowlist
python test_audit_logging.py         # User Story 6: Audit Logging
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Update tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🆘 Support

For issues and questions, please open an issue in the repository.
