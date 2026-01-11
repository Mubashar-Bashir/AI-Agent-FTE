# 🤖 Self-Healing FTE (Full-Time Equivalent) - AI-Powered Developer Automation

> **The Next Generation of Autonomous Development Operations**

The Self-Healing FTE is an advanced AI automation system that operates as a full-time equivalent developer, continuously monitoring, detecting, and resolving issues in your codebase with human oversight and enterprise-grade security.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Workspace   │────▶│ Skill Dispatcher │────▶│ Claude Code     │
│   Observer    │    │                  │    │ Skills          │
│  (Continuous   │    │  (Intelligent   │    │ (Automated      │
│   Monitoring)  │    │   Decision-Maker)│    │   Actions)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │   Event Triggers │
                       │   Configuration  │
                       └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   Human-in-the-  │
                       │   Loop Approval  │
                       └──────────────────┘
```

### Core Components
1. **Workspace Observer** - Continuous file monitoring system that watches for changes, errors, and patterns in real-time.
2. **Skill Dispatcher** - Intelligent decision engine that evaluates detected events and triggers appropriate Claude Code skills.
3. **Human-in-the-Loop (HITL)** - Secure approval system for high-risk operations with audit trails.
4. **PM2 Process Manager** - Production-grade process management ensuring 24/7 uptime and resilience.

---

## ⚡ PM2-Managed Resilience (Standard for 2026)

Our system leverages **PM2** for enterprise-grade process management, ensuring your Self-Healing FTE operates with maximum reliability:

### Why PM2 for Self-Healing Systems?

- **Automatic Restart**: Processes automatically recover from crashes
- **Zero-Downtime Reloads**: Updates without service interruption
- **Load Balancing**: Multiple process clustering for high availability
- **Memory Limits**: Prevents memory leaks from affecting system stability
- **Startup Scripts**: Automatic boot sequence on server restart
- **Monitoring**: Real-time CPU/Memory usage tracking

### PM2 Configuration Example

```bash
# Install PM2 globally
npm install -g pm2

# Start the observer and dispatcher with auto-restart
pm2 start src/observer/main.py --name "workspace-observer" --interpreter python
pm2 start src/dispatcher/main.py --name "skill-dispatcher" --interpreter python

# Save the process list for automatic startup
pm2 save
pm2 startup

# Monitor health
pm2 monit
```

### Production Benefits

| Feature | Benefit |
| ------- | ------- |
| Auto-Restart | Zero downtime after crashes |
| Cluster Mode | Handle more events simultaneously |
| Memory Thresholds | Prevent resource exhaustion |
| Startup Scripts | Automatic recovery after reboot |
| Health Checks | Proactive failure detection |

---

## 🔐 File-Based HITL (Human-in-the-Loop) - Security Focus

Enterprise-grade security through file-based approval workflows that ensure human oversight for critical operations:

### How File-Based HITL Works

1. **Detection Phase**: Observer detects an issue requiring high-risk action
2. **Approval Request**: Dispatcher creates `.approvals/request_<timestamp>.json` file
3. **Human Review**: Team member reviews the approval file and either approves/rejects
4. **Action Execution**: Upon approval, the skill executes with full audit trail

### Security Features

- **Immutable Approval Files**: Once created, approval requests cannot be modified
- **Timeout Protection**: Requests expire after configurable time limits
- **Audit Trail**: Every approval/rejection is logged with timestamps and user identity
- **Risk Classification**: Different approval requirements based on action severity

### Approval File Format

```json
{
  "id": "req_abc123",
  "timestamp": "2024-01-15T10:30:00Z",
  "skill": "test-driven-development",
  "risk_level": "high",
  "event_context": {
    "file": "src/auth/login.py",
    "error": "TypeError: 'NoneType' object has no attribute 'process'",
    "severity": "critical"
  },
  "action_summary": "Generate tests and fix authentication bug",
  "expires_at": "2024-01-15T11:30:00Z",
  "status": "pending"
}
```

### CLI Approval Commands

```bash
# List pending approvals
python src/dispatcher/cli_commands.py status

# Approve a request
python src/dispatcher/cli_commands.py approve req_abc123 --comment "Critical auth fix approved"

# Reject a request
python src/dispatcher/cli_commands.py reject req_abc123 --reason "Requires additional review"
```

---

## 🛡️ Regex-Safe Validation (Prevents Injection)

Advanced security measures to prevent ReDoS (Regular Expression Denial of Service) and injection attacks:

### Validation Layers

#### 1. Pattern Whitelist
- Pre-approved regex patterns only
- Time-limited execution with timeouts
- Complexity scoring to prevent catastrophic backtracking

#### 2. Input Sanitization
- Skill name validation prevents path traversal
- Parameter sanitization removes dangerous characters
- Context isolation prevents cross-skill contamination

#### 3. Runtime Protection
- Execution time monitoring
- Memory usage limits
- Recursive call prevention

### Security Configuration

```yaml
security:
  regex_timeout_seconds: 5
  max_pattern_complexity: 100
  allowed_patterns:
    - "^ERROR:.*$"
    - "^CRITICAL:.*$"
    - "^TypeError:.*$"
    - "^AttributeError:.*$"
  blocked_characters: ["..", ";", "&", "|", "$", "`"]
```

---

## 🎯 Live Demo: Closed-Loop in Action

Demonstrate the complete Self-Healing cycle with this simple test:

### 1. Trigger: Create a Mock Error Log
```bash
echo "ERROR: TypeError: 'NoneType' object has no attribute 'process'" >> /tmp/app.log
```

### 2. Detection: Observer Picks Up the Error Pattern
- File monitoring detects the pattern match
- Event context captured with severity classification
- Notification sent to skill dispatcher

### 3. Reasoning: Dispatcher Creates Approval File
- Creates `.approvals/request_<timestamp>.json` file
- Sets risk level to "high" for critical errors
- Waits for human approval before proceeding

### 4. Action: Approve via CLI and Watch Audit Log Update
```bash
# Check pending approvals
python src/dispatcher/cli_commands.py status

# Approve the request
python src/dispatcher/cli_commands.py approve req_abc123 --comment "Auto-fix for critical error"

# Verify audit trail
cat logs/audit.log
```

### Expected Outcome
- Skill executes to fix the error
- Audit log shows complete action trail
- System returns to normal operation

---

## 🔐 Enterprise Security: Credentials Handling

**Security First Approach:**

- **Environment Variables**: All credentials stored in `.env` files (never committed)
- **Config Manager**: Centralized credential management via `config/config_manager.py`
- **No Git Commits**: Credential files explicitly ignored in `.gitignore`
- **HITL Gateway**: High-risk actions require file-based human approval
- **Audit Trail**: Every credential access logged with user identification

### Security Best Practices

```python
# config/config_manager.py
import os
from dotenv import load_dotenv

load_dotenv()

class ConfigManager:
    def __init__(self):
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.admin_token = os.getenv('ADMIN_TOKEN')

    def get_secure_value(self, key):
        """Secure credential retrieval with audit logging"""
        # Implementation with logging
        pass
```

---

## 🚀 Production Deployment

### Prerequisites

- Python 3.8+
- Node.js 14+ (for PM2)
- Claude Code environment configured

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Dig-AI-FTE

# Install Python dependencies
pip install -r requirements.txt

# Install PM2 globally
npm install -g pm2

# Configure environment
cp .env.example .env
# Edit .env with your Claude API keys and other configurations
```

### Production Deployment

```bash
# Start services with PM2
pm2 start ecosystem.config.js

# Or start individually
pm2 start src/observer/main.py --name "workspace-observer" --interpreter python --watch
pm2 start src/dispatcher/main.py --name "skill-dispatcher" --interpreter python --watch

# View logs
pm2 logs

# Monitor status
pm2 status
```

---

## 📋 Gold Tier Compliance Table

| Feature | Status | Details |
| ------- | ------ | ------- |
| PM2 Process Management | ✅ **Implemented** | Auto-restart, clustering, monitoring |
| File-based HITL | ✅ **Implemented** | Immutable approval files with audit trail |
| Regex-Safe Validation | ✅ **Implemented** | ReDoS prevention and injection protection |
| Recursion Prevention | ✅ **Implemented** | Depth tracking with atomic counters |
| Kill-Switch Mechanism | ✅ **Implemented** | Emergency stop with token authorization |
| Audit Logging | ✅ **Implemented** | 90-day retention, daily rotation |
| Security Allowlist | ✅ **Implemented** | Configurable skill authorization |
| Risk Classification | ✅ **Implemented** | Low/Medium/High risk levels |
| De-bouncing | ✅ **Implemented** | Prevent duplicate event processing |
| Event Pattern Matching | ✅ **Implemented** | Configurable regex patterns |

---

## 🧪 Testing & Validation

### Core Test Suite

```bash
# Run all tests
python -m pytest tests/

# Individual test modules
python test_dispatcher_us1.py           # Error Detection
python test_hitl_and_killswitch.py     # Approval & Kill-Switch
python test_recursion_prevention.py    # Recursion Prevention
python test_security_allowlist.py      # Security Allowlist
python test_audit_logging.py           # Audit Logging
```

---

## 🏆 Innovation Highlights

Self-Healing FTE represents the future of development operations:

- ✅ **Autonomous Operation**: Works 24/7 without human intervention
- ✅ **Enterprise Security**: Multiple security layers and audit trails
- ✅ **Scalable Architecture**: Handles multiple events concurrently
- ✅ **Production Ready**: PM2-managed with zero-downtime capabilities
- ✅ **Human Oversight**: Critical actions require approval
- ✅ **Cost Effective**: Replaces multiple FTE hours with automated processes

*Join the revolution in autonomous development operations with Self-Healing FTE - where AI works as a permanent member of your development team.*