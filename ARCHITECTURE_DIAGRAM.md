# Dig-AI-FTE System Architecture - High Level Overview

## Core System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
│                      SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SOURCES                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     Gmail       │    WhatsApp     │     Bank APIs    │  Files   │
└────────┬────────┴────────┬────────┴─────────┬────────┴────┬─────┘
         │                 │                  │             │
         ▼                 ▼                  ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Gmail Watcher│ │WhatsApp Watch│ │Finance Watcher│            │
│  │  (Python)    │ │ (Playwright) │ │   (Python)   │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Local)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /Needs_Action/  │ /Plans/  │ /Done/  │ /Logs/            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Dashboard.md    │ Company_Handbook.md │ Business_Goals.md│  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ /Pending_Approval/  │  /Approved/  │  /Rejected/         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      CLAUDE CODE                          │ │
│  │   Read → Think → Plan → Write → Request Approval          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              ▼                                      ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│    HUMAN-IN-THE-LOOP       │    │         ACTION LAYER           │
│  ┌──────────────────────┐  │    │  ┌─────────────────────────┐   │
│  │ Review Approval Files│──┼───▶│  │    MCP SERVERS          │   │
│  │ Move to /Approved    │  │    │  │  ┌──────┐ ┌──────────┐  │   │
│  └──────────────────────┘  │    │  │  │Email │ │ Browser  │  │   │
│                            │    │  │  │ MCP  │ │   MCP    │  │   │
└────────────────────────────┘    │  │  └──┬───┘ └────┬─────┘  │   │
                                  │  └─────┼──────────┼────────┘   │
                                  └────────┼──────────┼────────────┘
                                           │          │
                                           ▼          ▼
                                  ┌────────────────────────────────┐
                                  │     EXTERNAL ACTIONS           │
                                  │  Send Email │ Make Payment     │
                                  │  Post Social│ Update Calendar  │
                                  └────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Orchestrator.py (Master Process)             │ │
│  │   Scheduling │ Folder Watching │ Process Management       │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Watchdog.py (Health Monitor)                 │ │
│  │   Restart Failed Processes │ Alert on Errors              │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Integration with Dig-AI-FTE Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIG-AI-FTE INTEGRATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EXTERNAL SOURCES → PERCEPTION LAYER → DIG-AI-FTE CORE        │
│         ↓                    ↓              ↓                   │
│  Gmail/WhatsApp/     Gmail/WhatsApp/    Workspace Observer    │
│  Bank APIs/Files     Finance Watchers    + Skill Dispatcher   │
│                                                                 │
│  OBSIDIAN VAULT ←→ DIG-AI-FTE DASHBOARD ←→ REAL-TIME MONITOR  │
│         ↓                   ↓                    ↓              │
│  Local Knowledge      Next.js Dashboard     System Metrics    │
│  Base Integration     with HITL Controls    + Event Tracking  │
│                                                                 │
│  REASONING LAYER → HUMAN-IN-THE-LOOP → ACTION LAYER           │
│         ↓                   ↓                    ↓              │
│  Claude Code with      Approval Workflow    MCP Servers +     │
│  SDD Principles        + File Management    External Actions  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Strengths & Architecture Principles

### 1. Local-First Architecture
- **Privacy-Centric**: All sensitive data stored locally in Obsidian vault
- **Offline Operation**: System functions independently of internet connectivity
- **Data Sovereignty**: Complete control over personal and business data
- **Zero-Trust External**: Minimal external API dependencies

### 2. Human-in-the-Loop (HITL) Safety System
- **File-Based Approval**: Sophisticated approval system using file states
- **Risk-Based Controls**: Different approval levels for different risk categories
- **Audit Trail**: Complete logging of all decisions and actions
- **Emergency Overrides**: Kill-switch mechanisms for immediate control

### 3. Modular Component Architecture
- **Perception Layer**: Multiple watchers for different data sources
- **Reasoning Layer**: Central AI processing with decision making
- **Action Layer**: Various MCP servers for different action types
- **Orchestration Layer**: Master processes for coordination and monitoring

### 4. Security & Safety Controls
- **Skill Allowlist**: Configurable validation of allowed actions
- **Recursive Execution Prevention**: Max depth of 3 for safety
- **Pattern Debouncing**: Prevention of rapid-fire triggers
- **Kill-switch Mechanisms**: Emergency controls at multiple levels

## System Integration Points

### Obsidian Integration
- Real-time synchronization with Obsidian vault
- Kanban board management for task tracking
- Knowledge base maintenance and updates
- Approval workflow management through file states

### Dashboard Integration
- Real-time system monitoring and metrics
- Milestone tracking and progress reporting
- Optimization ideas and alternative approaches
- Stakeholder visibility and control

### Skill Framework Integration
- Modular skill architecture with standardized interfaces
- HITL approval workflows for high-risk operations
- Execution context management and safety controls
- Event-driven skill triggering based on patterns

## Data Flow & Processing

```
External Sources → Perception Layer → Obsidian Vault → Reasoning Layer
       ↓               ↓                   ↓              ↓
   Raw Data     →   Filtered     →    Organized    →   Processed
   Collection      Events &        →    Knowledge    →   Decisions
                   Notifications   →    Base         →   & Plans

Processed Decisions → HITL Review → Action Layer → External Actions
         ↓              ↓             ↓              ↓
    Approval/      Approval/     MCP Server    →  Executed
    Rejection      Routing       Coordination      Actions
    Workflow       Management    & Execution
```

## Operational Workflow

1. **Data Ingestion**: Multiple watchers collect data from external sources
2. **Local Processing**: Data is processed and organized in Obsidian vault
3. **AI Reasoning**: Claude Code processes information and generates plans
4. **Human Review**: Critical decisions require human approval via file system
5. **Action Execution**: Approved actions are executed through MCP servers
6. **Monitoring**: System continuously monitors and adjusts operations
7. **Reporting**: Real-time dashboard updates stakeholders on system status

This architecture ensures robust, safe, and autonomous operation while maintaining human oversight for critical decisions, aligning perfectly with the constitutional principles of the Dig-AI-FTE system.