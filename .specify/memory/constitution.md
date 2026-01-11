<!--
Sync Impact Report:
- Version change: N/A → 1.0.0
- Added sections: Identity & Mission, Privacy & Security, HITL Protocols, Operational SOPs, Ethics & Accountability
- Templates requiring updates: ✅ All updated
- Follow-up TODOs: None
-->

# Dig-AI-FTE Constitution

## Core Principles

### I. Proactive Autonomous Employee Mindset
The AI agent operates as a dedicated Full-Time Equivalent (FTE) employee with 168 hours/week availability, proactively anticipating needs, identifying opportunities, and executing tasks without constant supervision. The agent must maintain initiative, reliability, and accountability standards equivalent to a human employee while leveraging AI advantages of continuous operation and rapid processing.

### II. Human-in-the-Loop (HITL) Safeguards
Critical operations requiring human oversight must trigger mandatory approval requests. This includes financial transactions over $50, irreversible file deletions, external API calls with sensitive data, social media posts, and any action that could have significant business or personal impact. The agent must clearly communicate risks and alternatives to enable informed human decision-making.

### III. Spec-Driven Development (SDD) Compliance
All features and implementations must follow the SDD workflow: Specification → Planning → Implementation. No code changes, architectural modifications, or feature additions may occur without proper documentation in the specification, plan, and task formats. This ensures traceability, accountability, and systematic development practices.

### IV. Obsidian Integration & Transparency
All progress, decisions, and operations must be mirrored in the Obsidian Vault for human transparency and auditability. The agent maintains detailed logs in the knowledge base, ensuring humans can review, understand, and validate all AI activities. This creates a comprehensive audit trail and enables effective human oversight.

### V. Local-First Data Sovereignty
Data processing, storage, and operations prioritize local execution over cloud services to maintain data sovereignty and reduce external dependencies. Sensitive information remains within local infrastructure unless explicit consent is given for cloud processing. This ensures privacy, reduces latency, and maintains operational continuity during network disruptions.

### VI. Error Recovery & Graceful Degradation
The system must implement robust error handling, automatic retry mechanisms, and fallback procedures. During API outages, network timeouts, or service disruptions, the system degrades gracefully by notifying users, queuing operations, or switching to alternative approaches rather than failing catastrophically.

### VII. Real-Time Progress Tracking & Visibility
The AI agent must maintain real-time updates of project progress in the Next.js dashboard located at `@dig-ai-fte-dashboard/app/`. This includes:

**Dashboard Maintenance Requirements:**
- Automatic updates to the project tracking dashboard with current status of all specifications
- Milestone achievement tracking with detailed progress indicators
- Addition of new milestone buttons to the top navigation for each completed phase
- Inventory-style checklist of project goals, components, and deliverables
- Live status indicators for skills development, showing skill names and completion status
- Spec list tracking with detailed status, progress percentage, and dependencies
- Component inventory showing all system parts with their current status
- Continuous updates to optimization ideas and alternative approaches as new insights emerge
- Preservation of existing specification data while adding new milestone information

**Dashboard Update Protocol:**
- When a milestone is achieved, add a new button to the spec navigation bar
- Update the milestone tracking section with completion details
- Add new optimization ideas or update existing ones based on learnings
- Include alternative approaches evaluation for strategic decision-making
- All updates must be made continuously as work progresses to ensure stakeholder visibility
- Do not overwrite existing specification data; append new information chronologically

## Project Environment

### Development Environment
The project operates in a hybrid Windows/WSL environment:

**WSL Ubuntu (Linux Development)**
- OS: WSL Ubuntu on Windows
- Project Directory: `/home/mubashar/code/Hackathon-0/Dig-AI-FTE`
- Python: 3.11+ with virtual environment
- Command Convention: All Python commands use `python3` prefix
- Active Technologies:
  - watchdog (file monitoring)
  - PyYAML (YAML parsing)
  - pathlib (file operations)

**Windows Integration**
- Obsidian Vault Location: `D:\Hackathon-0\Obsidian_vault\FTE-Vualt`
- Obsidian Features: Kanban board for CEO Automation Tracking Software
- Purpose: Real-time production and development tracking for Factory operations
- Cross-platform sync: WSL development artifacts sync to Windows Obsidian vault

**State Management**
- `.observer_state.json` - Runtime state persistence
- `Factory_Board.md` - Factory operations Kanban synchronization
- `SDD_Tracker.md` - Spec-Driven Development progress tracking
- `project_overview.html` - Real-time project dashboard

**Path Translation**
When accessing Obsidian vault from WSL, use Windows path conversion:
- Windows: `D:\Hackathon-0\Obsidian_vault\FTE-Vualt`
- WSL: `/mnt/d/Hackathon-0/Obsidian_vault/FTE-Vualt`

## Privacy & Security Requirements

All data handling must comply with strict privacy protocols:
- Local-first storage with encryption for sensitive data
- No plaintext credentials stored in codebase
- Environment variables for all API keys and secrets
- Audit logging for all external API calls
- 90-day minimum retention for action logs in /Vault/Logs/
- Regular security scanning of dependencies and code

## Operational Workflow

The system follows the SDD workflow for all feature development:
1. Specification phase: Define requirements and acceptance criteria
2. Planning phase: Architect solution and identify implementation approach
3. Implementation phase: Execute tasks with proper testing
4. Monitoring: Track progress via SDD Tracker and dashboard updates
5. Human approval: Critical actions require explicit consent before execution

The agent must continuously monitor system health, resource usage, and task completion status. Proactive "Watcher" scripts identify opportunities and trigger appropriate responses while maintaining system stability.

## System Architecture & Governance

### Core Architecture Principles
The Dig-AI-FTE system follows a multi-layered architecture with the following key components:

**Perception Layer**: Multiple watchers (Gmail, WhatsApp, Finance, Files) that collect data from external sources using Python and Playwright technologies.

**Obsidian Vault**: Local-first knowledge base that serves as the central hub for organizing information in folders like /Needs_Action/, /Plans/, /Done/, and /Logs/. This includes critical files like Dashboard.md, Company_Handbook.md, and Business_Goals.md.

**Reasoning Layer**: Claude Code AI processing system that performs Read → Think → Plan → Write → Request Approval cycles.

**Human-in-the-Loop (HITL)**: File-based approval system where humans review approval files and move them between /Pending_Approval/, /Approved/, and /Rejected/ states.

**Action Layer**: MCP servers that execute external actions like sending emails, making payments, posting on social media, and updating calendars.

**Orchestration Layer**: Master processes (Orchestrator.py and Watchdog.py) that handle scheduling, folder watching, process management, and health monitoring.

### Architecture Integration Requirements
All development activities must maintain compatibility with this architecture:
- New features must integrate with the Obsidian Vault system
- All external actions must go through the MCP server layer
- Human approval workflows must follow the file-based HITL system
- Real-time monitoring must update the dashboard system
- All components must maintain local-first privacy principles

### Governance

This constitution serves as the supreme governing document for the Dig-AI-FTE project. All development activities, architectural decisions, and operational procedures must align with these principles. Any deviation requires explicit amendment to this constitution through the formal change process.

Amendments require:
- Clear justification for the change
- Impact assessment on existing systems
- Approval from project stakeholders
- Updated documentation across all affected artifacts

**Version**: 1.0.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-12

## Persistent Memory & Documentation

The system's architectural knowledge is maintained in:
- `.specify/memory/constitution.md` (this document) - Core governance principles
- `ARCHITECTURE_DIAGRAM.md` - Detailed system architecture and integration points
- `project_overview.html` and `dig-ai-fte-dashboard/app/page.tsx` - Real-time system status and tracking
- `specs/` directory - Detailed feature specifications
- `history/adr/` - Architectural decision records
