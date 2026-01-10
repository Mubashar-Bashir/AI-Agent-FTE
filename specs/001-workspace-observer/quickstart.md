# Quickstart: Automated Workspace Observer

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Access to the project directory

## Setup

1. **Install Dependencies**:
   ```bash
   pip install watchdog PyYAML
   ```

2. **Create Required Directories** (if they don't exist):
   ```bash
   mkdir -p logs
   mkdir -p specs
   ```

3. **Verify Directory Structure**:
   Ensure your project has these key files/directories:
   - `/specs/` - Directory to monitor for spec changes
   - `00_Workspace/Factory_Board.md` - Kanban board file to update
   - `30_Specifications/SDD_Tracker.md` - Tracker file to update

## Running the Observer

### Option 1: Direct Execution
```bash
cd /path/to/project
python src/observer/main.py
```

### Option 2: Using CLI
```bash
python src/cli/observer_cli.py start
```

### Option 3: As a Background Service
```bash
# Start in the background
nohup python src/observer/main.py > logs/observer.log 2>&1 &
```

## Configuration

The observer uses these default settings:
- Monitors: `./specs` directory
- Kanban Board: `00_Workspace/Factory_Board.md`
- Tracker: `30_Specifications/SDD_Tracker.md`
- State File: `.observer_state.json` (in project root)
- Log File: `logs/observer.log`

## Testing the Setup

1. Start the observer service
2. Create or modify a spec file in the `/specs` directory
3. Verify that:
   - A new entry appears (or existing entry updates) in `Factory_Board.md`
   - The `SDD_Tracker.md` file is updated with the new status/percentage
   - Check `logs/observer.log` for processing messages

## Common Commands

```bash
# Stop the observer (find the process ID and kill it)
ps aux | grep observer
kill [PID]

# View logs
tail -f logs/observer.log

# Check if observer is running
ps aux | grep python.*observer
```

## Troubleshooting

- **Observer not detecting changes**: Ensure the `/specs` directory exists and has proper read/write permissions
- **Kanban board not updating**: Verify the `Factory_Board.md` file exists and is in the correct location
- **Tracker not updating**: Check that `SDD_Tracker.md` exists in the correct location
- **Permission errors**: Ensure the script has write access to the log directory and state file