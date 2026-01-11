#!/usr/bin/env python3
"""
Emergency Sync Script for Workspace Observer

This script performs a force re-sync of all spec files to update
the Factory_Board.md and SDD_Tracker.md files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to the path so we can import the observer modules
sys.path.insert(0, './src')

from observer.processor import SpecProcessor
from observer.kanban_updater import KanbanUpdater
from observer.tracker_updater import TrackerUpdater
from observer.utils import setup_logger


def force_resync():
    """Force re-scan all spec files and update tracking boards."""
    print("🔄 Starting Emergency Force Re-Sync of all Specifications...")

    # Set up logger
    logger = setup_logger("emergency_sync", "logs/emergency_sync.log")
    logger.info("Starting emergency sync process")

    # Initialize the processor
    processor = SpecProcessor(logger=logger)

    # Define the specs directory
    specs_dir = Path("specs")

    if not specs_dir.exists():
        print(f"❌ Specs directory {specs_dir} does not exist!")
        logger.error(f"Specs directory {specs_dir} does not exist!")
        return

    # Get all markdown files in the specs directory
    spec_files = list(specs_dir.rglob("*.md"))

    print(f"📁 Found {len(spec_files)} spec files to process")
    logger.info(f"Found {len(spec_files)} spec files to process")

    # Process each spec file
    for spec_file in spec_files:
        try:
            print(f"📝 Processing: {spec_file}")
            logger.info(f"Processing spec file: {spec_file}")

            # Queue each file as a modification to trigger processing
            processor.queue_file_change(str(spec_file), 'modified')

        except Exception as e:
            print(f"❌ Error processing {spec_file}: {e}")
            logger.error(f"Error processing {spec_file}: {e}")

    # Give the processor some time to finish processing the queue
    import time
    time.sleep(3)  # Wait for processing to complete

    print("✅ Emergency sync completed! Dashboard and Tracker updated.")
    logger.info("Emergency sync completed")


def create_factory_board_if_missing():
    """Create Factory_Board.md if it doesn't exist in the expected location."""
    factory_board_path = Path("00_Workspace/Factory_Board.md")

    if not factory_board_path.exists():
        print(f"📄 Creating Factory_Board.md at {factory_board_path}")

        # Create the directory if it doesn't exist
        factory_board_path.parent.mkdir(parents=True, exist_ok=True)

        # Create default Factory Board content
        default_content = """# Factory Board

## To Do



## In Progress



## Completed



## Blocked



## Verification Phase


---

## Legend
- [ ] To Do
- [.] In Progress
- [x] Completed
- [b] Blocked
"""

        with open(factory_board_path, 'w', encoding='utf-8') as f:
            f.write(default_content)

        print(f"✅ Created Factory_Board.md at {factory_board_path}")


def check_and_fix_paths():
    """Check if the expected files exist and create them if missing."""
    print("🔍 Checking for required tracking files...")

    # Check and create Factory Board if missing
    create_factory_board_if_missing()

    # Check if SDD Tracker exists
    tracker_path = Path("30_Specifications/SDD_Tracker.md")
    if not tracker_path.exists():
        print(f"📄 Creating SDD_Tracker.md at {tracker_path}")

        # Create the directory if it doesn't exist
        tracker_path.parent.mkdir(parents=True, exist_ok=True)

        # Create default tracker content
        default_content = """# SDD Tracker

## Active Feature Tracking

```dataview
TABLE status, current_step, percent, next_step
FROM #FTE-Feature
SORT file.name ASC
```

## All FTE Features

```dataview
TABLE status, current_step, percent, next_step, last_cmd
FROM #FTE-Feature
SORT file.name ASC
```

"""

        with open(tracker_path, 'w', encoding='utf-8') as f:
            f.write(default_content)

        print(f"✅ Created SDD_Tracker.md at {tracker_path}")


if __name__ == "__main__":
    print("🚨 Emergency Sync: Real-time tracking recovery initiated")

    # First, check and fix file paths
    check_and_fix_paths()

    # Then run the force resync
    force_resync()

    print("\n🎯 Real-time tracking recovery completed!")
    print("📋 The Observer should now be able to update your tracking files correctly")