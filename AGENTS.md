# AGENTS.md - Dig_AI_Emp Autonomous FTE Factory

## Project Mission
Building a production-ready 'Digital FTE' (Digital Full-Time Equivalent) with an Obsidian Dashboard. This AI employee operates 24/7 to manage personal and business affairs autonomously, serving as a proactive business partner that anticipates needs and identifies opportunities.

## Technical Stack
- **Language:** Python 3.12+
- **Package Management:** uv for fast, reliable dependency management
- **Project Layout:** src/ directory structure with modular organization
- **User Interface:** Obsidian as the knowledge base and dashboard
- **Architecture:** Hybrid layout optimized for both local operation and future cloud deployment
- **Version Control:** Git with semantic commit messages

## Operational Rules
1. **Dashboard Monitoring:** Always check `project_overview.html` before and after tasks to maintain situational awareness
2. **Execution Protocol:** Use `uv run` for all script executions to ensure consistent environment
3. **Planning Discipline:** Follow a 'Plan-First' approach: Propose logic before writing code
4. **File Organization:** Respect the folder hierarchy (00_Workspace, 10_Governance, 20_Archive, 99_Internal)
5. **Code Quality:** Maintain PEP8 compliance with proper type hints and documentation

## Commit Guidelines
Use descriptive, prefix-based commits following conventional commits standards:
- `feat:` - New features (e.g., `feat: add gmail watcher`)
- `fix:` - Bug fixes (e.g., `fix: resolve dashboard query issue`)
- `docs:` - Documentation updates (e.g., `docs: update AGENTS.md`)
- `style:` - Code formatting (e.g., `style: format inbox_watcher.py`)
- `refactor:` - Code restructuring (e.g., `refactor: reorganize src layout`)
- `test:` - Adding tests (e.g., `test: add watcher unit tests`)
- `chore:` - Maintenance tasks (e.g., `chore: update dependencies`)

## Memory Management
- **Long-term Memory:** Use `10_Governance/Strategy/Company_Handbook.md` as behavioral memory and rules reference
- **Configuration:** Store all settings in `.env` template following security guidelines
- **State Tracking:** Update dashboard files in `00_Workspace/` to reflect system state
- **Knowledge Base:** Maintain project specifications in `10_Governance/Specs/`

## Standard Operating Procedures (SOP)
1. **Before Implementation:** Review AGENTS.md and existing code structure
2. **During Development:** Follow src layout and PEP8 standards
3. **After Changes:** Update dashboard and verify build integrity with `uv run`
4. **Before Commit:** Use proper commit prefixes and test functionality
5. **For New Features:** Add to appropriate modules in `src/skills/`

## Security & Best Practices
- Never hardcode credentials; use environment variables from `.env`
- Implement proper error handling and logging
- Follow the Human-in-the-Loop (HITL) pattern for sensitive operations
- Maintain audit trails for all external actions
- Use the approval workflow for financial transactions

## Emergency Protocols
- **Build Failures:** Revert changes and diagnose with `uv sync`
- **Security Breach:** Follow incident response in AGENTS.md
- **Data Corruption:** Restore from last known good state
- **Service Disruption:** Activate backup processes