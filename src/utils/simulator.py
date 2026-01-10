"""
Simulator for AI Employee System

This script simulates the behavior of the AI employee system,
creating dummy files to demonstrate the workflow in the Obsidian dashboard.
"""
import os
import time
import random
from datetime import datetime
from pathlib import Path
import json

def simulate_system_activity():
    """Simulate the AI employee system by creating and moving files."""

    # Define folder paths
    inbox_dir = Path("00_Workspace/Inbox")
    needs_action_dir = Path("00_Workspace/Needs_Action")
    done_dir = Path("20_Archive/Done")
    logs_dir = Path("99_Internal/Logs")

    # Create directories if they don't exist
    inbox_dir.mkdir(exist_ok=True)
    needs_action_dir.mkdir(exist_ok=True)
    done_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    print("🤖 AI Employee Simulator Starting...")
    print(f"Monitoring folders:")
    print(f"  📥 Inbox: {inbox_dir}")
    print(f"  ⚙️ Needs Action: {needs_action_dir}")
    print(f"  ✅ Done: {done_dir}")
    print(f"  📊 Logs: {logs_dir}")
    print()

    # Create initial log entry
    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Simulator started\n"
    with open(logs_dir / "system.log", "a") as log_file:
        log_file.write(log_entry)

    # Simulate 5 cycles of activity
    for cycle in range(1, 6):
        print(f"🔄 Cycle {cycle}/5")

        # Create a new file in Inbox
        timestamp = datetime.now().strftime("%H%M%S")
        inbox_filename = f"simulated_task_{timestamp}_{random.randint(100, 999)}.md"
        inbox_filepath = inbox_dir / inbox_filename

        # Create the file content
        with open(inbox_filepath, "w") as f:
            f.write(f"""---
created: {datetime.now().isoformat()}
type: simulated-task
priority: medium
---

# Simulated Task {timestamp}

This is a simulated task created by the AI Employee Simulator.

**Task Details:**
- Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Cycle: {cycle}
- Random ID: {random.randint(100, 999)}

**Status:** New arrival in Inbox
""")

        print(f"  📥 Created: {inbox_filename}")

        # Log the creation
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File created in Inbox: {inbox_filename}\n"
        with open(logs_dir / "system.log", "a") as log_file:
            log_file.write(log_entry)

        time.sleep(2)  # Pause to simulate processing time

        # Move file to Needs Action
        needs_action_filepath = needs_action_dir / inbox_filename
        os.rename(inbox_filepath, needs_action_filepath)

        print(f"  ⚙️ Moved to Needs Action: {inbox_filename}")

        # Update the file content to reflect status
        with open(needs_action_filepath, "a") as f:
            f.write(f"""

**Status:** Processing in Needs Action
**Processing started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

        # Log the movement
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File moved to Needs Action: {inbox_filename}\n"
        with open(logs_dir / "system.log", "a") as log_file:
            log_file.write(log_entry)

        time.sleep(3)  # Pause to simulate processing time

        # Move file to Done
        done_filepath = done_dir / inbox_filename
        os.rename(needs_action_filepath, done_filepath)

        print(f"  ✅ Moved to Done: {inbox_filename}")

        # Update the file content to reflect completion
        with open(done_filepath, "a") as f:
            f.write(f"""

**Status:** Completed
**Completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Cycle completed:** {cycle}
""")

        # Log the completion
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File moved to Done: {inbox_filename}\n"
        with open(logs_dir / "system.log", "a") as log_file:
            log_file.write(log_entry)

        print(f"  📊 Updated system log")
        print()

        if cycle < 5:
            time.sleep(3)  # Pause between cycles

    print("🎉 Simulation completed!")
    print("Check your Obsidian dashboard to see the activity flow.")
    print("\nThe dashboard should now show:")
    print("- Empty Inbox (all files processed)")
    print("- Empty Needs Action (all files processed)")
    print("- Files in Done archive")
    print("- Updated activity feed in logs")

if __name__ == "__main__":
    simulate_system_activity()