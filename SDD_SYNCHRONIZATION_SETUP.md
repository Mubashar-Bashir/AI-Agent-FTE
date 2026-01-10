# SDD Synchronization Setup Documentation

## Overview
This document describes the synchronization setup between the SDD workflow directories and the Obsidian vault for the Dig-AI-FTE project.

## Directory Structure
- `/specs` - Primary SDD workflow directory where specifications are created during the SDD process
- `/30_Specifications` - Symbolic link to `D:\Hackathon-0\Obsidian_vault\FTE-Vualt\30_Specifications` in the Obsidian vault

## Synchronization Mechanism
Two synchronization methods are available:

### 1. Automatic Synchronization (`auto_sync.py`)
- Monitors file changes in real-time
- Automatically syncs changes to the Obsidian vault
- Watches the following directories:
  - `00_Workspace`
  - `10_Governance`
  - `20_Archive`
  - `30_Specifications`
  - `specs` (NEW - for SDD workflow)
  - `99_Internal`

### 2. Manual Synchronization (`sync_to_obsidian.sh`)
- Performs a one-time sync of all configured directories
- Uses rsync for efficient file transfer
- Syncs the following directories:
  - `00_Workspace`
  - `10_Governance`
  - `20_Archive`
  - `30_Specifications`
  - `specs` (NEW - for SDD workflow)
  - `99_Internal`

## SDD Workflow Integration
1. During SDD workflow, specifications are created in the `/specs` directory
2. The synchronization mechanism ensures these files are automatically reflected in the Obsidian vault
3. Files in the Obsidian vault at `D:\Hackathon-0\Obsidian_vault\FTE-Vualt\specs\` stay in sync with the local `/specs` directory
4. Changes made in either location are synchronized to maintain consistency

## Usage
### Starting Auto-Sync
```bash
python auto_sync.py
```

### Manual Sync
```bash
bash sync_to_obsidian.sh
```

## Benefits
- Seamless integration between SDD workflow and Obsidian knowledge management
- Real-time synchronization ensures consistency
- Bidirectional sync supports collaborative development
- Maintains the established SDD process while connecting to the Obsidian ecosystem