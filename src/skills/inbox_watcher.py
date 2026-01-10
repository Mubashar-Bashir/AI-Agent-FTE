"""
Inbox Watcher for AI Employee System

Monitors the Inbox folder for new files and moves them to Needs_Action
when certain conditions are met.
"""
import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InboxHandler(FileSystemEventHandler):
    """Handles file system events in the Inbox directory."""

    def __init__(self, inbox_dir, needs_action_dir):
        self.inbox_dir = Path(inbox_dir)
        self.needs_action_dir = Path(needs_action_dir)

        # Create destination directory if it doesn't exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)

        # Track processed files to avoid duplicates
        self.processed_files = set()

    def on_created(self, event):
        """Handle file creation events in the Inbox."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if this is a markdown file and not already processed
        if file_path.suffix.lower() == '.md' and str(file_path) not in self.processed_files:
            self.process_file(file_path)

    def on_moved(self, event):
        """Handle file move events in the Inbox."""
        if event.is_directory:
            return

        file_path = Path(event.dest_path)  # Note: for move events, use dest_path

        # Check if this is a markdown file and not already processed
        if file_path.suffix.lower() == '.md' and str(file_path) not in self.processed_files:
            self.process_file(file_path)

    def process_file(self, file_path):
        """Process a file by moving it to Needs_Action."""
        try:
            # Add to processed set to avoid duplicate processing
            self.processed_files.add(str(file_path))

            # Log the file detection
            logger.info(f"Detected new file in Inbox: {file_path.name}")

            # Create log entry in system log
            from datetime import datetime
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File detected in Inbox: {file_path.name}\n"
            logs_dir = Path("99_Internal/Logs")
            logs_dir.mkdir(exist_ok=True)
            with open(logs_dir / "system.log", "a") as log_file:
                log_file.write(log_entry)

            # Move the file to Needs_Action
            destination = self.needs_action_dir / file_path.name
            file_path.rename(destination)

            # Update the file with processing status
            with open(destination, "a") as f:
                f.write(f"\n\n**Status:** Automatically moved to Needs Action by Inbox Watcher\n")
                f.write(f"**Moved at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            logger.info(f"Moved {file_path.name} to Needs_Action: {destination}")

            # Log the movement
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File moved to Needs Action: {file_path.name}\n"
            with open(logs_dir / "system.log", "a") as log_file:
                log_file.write(log_entry)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")


def start_inbox_watcher():
    """Start the inbox watcher to monitor for new files."""
    inbox_dir = Path("00_Workspace/Inbox")
    needs_action_dir = Path("00_Workspace/Needs_Action")

    # Create directories if they don't exist
    inbox_dir.mkdir(parents=True, exist_ok=True)
    needs_action_dir.mkdir(parents=True, exist_ok=True)

    # Create the event handler
    event_handler = InboxHandler(inbox_dir, needs_action_dir)

    # Create the observer
    observer = Observer()
    observer.schedule(event_handler, str(inbox_dir), recursive=False)

    # Start the observer
    observer.start()
    logger.info(f"Inbox Watcher started. Monitoring: {inbox_dir}")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Inbox Watcher...")
        observer.stop()

    observer.join()
    logger.info("Inbox Watcher stopped.")


if __name__ == "__main__":
    start_inbox_watcher()