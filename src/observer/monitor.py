"""
File monitoring module for the Automated Workspace Observer.

This module uses the watchdog library to monitor the /specs directory
for file creation, modification, and deletion events.
"""
import os
import time
import threading
from pathlib import Path
from typing import Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .processor import SpecProcessor
from .utils import setup_logger

# Import dispatcher integration
try:
    from dispatcher.integration import ObserverIntegration
    from dispatcher.main import DispatcherMain
    HAS_DISPATCHER = True
except ImportError:
    HAS_DISPATCHER = False


class SpecEventHandler(FileSystemEventHandler):
    """Handles file system events for spec files."""

    def __init__(self, processor: SpecProcessor, logger=None):
        super().__init__()
        self.processor = processor
        self.logger = logger or setup_logger()

        # Initialize dispatcher integration if available
        self.dispatcher_integration = None
        if HAS_DISPATCHER:
            try:
                dispatcher = DispatcherMain()
                dispatcher.setup()
                self.dispatcher_integration = ObserverIntegration(dispatcher)
                self.dispatcher_integration.start_monitoring()
                self.logger.info("Successfully initialized dispatcher integration in event handler")
            except Exception as e:
                self.logger.error(f"Failed to initialize dispatcher integration: {e}")
                self.dispatcher_integration = None

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Process with spec processor for spec files
        if file_path.suffix.lower() in ['.md', '.txt'] and 'specs' in str(file_path):
            self.logger.info(f"File created: {file_path}")
            self.processor.queue_file_change(str(file_path), 'created')

        # Also process with dispatcher for log-like files
        if self.dispatcher_integration and file_path.suffix.lower() in ['.log', '.txt', '.out']:
            self.logger.info(f"Processing created file with dispatcher: {file_path}")
            self.dispatcher_integration._process_file_content(str(file_path))

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Process with spec processor for spec files
        if file_path.suffix.lower() in ['.md', '.txt'] and 'specs' in str(file_path):
            self.logger.info(f"File modified: {file_path}")
            self.processor.queue_file_change(str(file_path), 'modified')

        # Also process with dispatcher for log-like files
        if self.dispatcher_integration and file_path.suffix.lower() in ['.log', '.txt', '.out']:
            self.logger.info(f"Processing modified file with dispatcher: {file_path}")
            self.dispatcher_integration._process_file_content(str(file_path))

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Process with spec processor for spec files
        if file_path.suffix.lower() in ['.md', '.txt'] and 'specs' in str(file_path):
            self.logger.info(f"File deleted: {file_path}")
            self.processor.queue_file_change(str(file_path), 'deleted')


class SpecMonitor:
    """Monitors the specs directory for file changes."""

    def __init__(self, spec_dir: str = "./specs", logger=None):
        self.spec_dir = Path(spec_dir)
        self.observer = Observer()
        self.processor = SpecProcessor(logger=logger)
        self.event_handler = SpecEventHandler(self.processor, logger)
        self.logger = logger or setup_logger()
        self.running = False

    def start(self):
        """Start monitoring the specs directory."""
        if not self.spec_dir.exists():
            self.spec_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created specs directory: {self.spec_dir}")

        self.observer.schedule(
            self.event_handler,
            str(self.spec_dir),
            recursive=True
        )
        self.observer.start()
        self.running = True
        self.logger.info(f"Started monitoring directory: {self.spec_dir}")

    def stop(self):
        """Stop monitoring the specs directory."""
        # Stop dispatcher integration if active
        if self.event_handler.dispatcher_integration:
            self.event_handler.dispatcher_integration.stop_monitoring()

        self.observer.stop()
        self.observer.join()
        self.running = False
        self.logger.info("Stopped monitoring")

    def is_running(self):
        """Check if the monitor is currently running."""
        return self.running