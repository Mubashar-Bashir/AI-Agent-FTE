"""
Main module for the Automated Workspace Observer.

This module initializes and runs the observer service that monitors
the /specs directory for changes and processes them in alphabetical order.
"""
import os
import signal
import sys
import time
import threading
from pathlib import Path

from .monitor import SpecMonitor
from .utils import setup_logger

# Import dispatcher integration
try:
    from dispatcher.integration import ObserverIntegration
    from dispatcher.main import DispatcherMain
    HAS_DISPATCHER = True
except ImportError:
    HAS_DISPATCHER = False
    print("Warning: Dispatcher not available. Some features may be limited.")


class WorkspaceObserver:
    """Main class for the workspace observer service."""

    def __init__(self, spec_dir: str = "./specs", pid_file: str = ".observer.pid"):
        self.spec_dir = Path(spec_dir)
        self.pid_file = Path(pid_file)
        self.monitor = None
        self.logger = setup_logger()
        self.running = False
        self._stop_event = threading.Event()

        # Initialize dispatcher integration if available
        self.dispatcher_integration = None
        self._initialize_dispatcher_integration()

    def _initialize_dispatcher_integration(self):
        """Initialize integration with the skill dispatcher if available."""
        if HAS_DISPATCHER:
            try:
                # Initialize dispatcher
                dispatcher = DispatcherMain()
                dispatcher.setup()

                # Create integration
                self.dispatcher_integration = ObserverIntegration(dispatcher)

                # Start monitoring for dispatcher-relevant changes
                self.dispatcher_integration.start_monitoring()

                self.logger.info("Successfully initialized dispatcher integration")
            except Exception as e:
                self.logger.error(f"Failed to initialize dispatcher integration: {e}")
                self.dispatcher_integration = None

    def start(self):
        """Start the observer service."""
        try:
            self.logger.info("Starting Workspace Observer service...")
            self.logger.info(f"Monitoring directory: {self.spec_dir}")

            # Create PID file
            self._create_pid_file()

            # Initialize the monitor
            self.monitor = SpecMonitor(spec_dir=str(self.spec_dir), logger=self.logger)

            # Start monitoring
            self.monitor.start()
            self.running = True

            self.logger.info("Workspace Observer service started successfully")

            # Only register signal handlers if running in main thread
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except ValueError:
                # If not in main thread, skip signal handlers
                self.logger.debug("Not in main thread, skipping signal handler registration")

            # Keep the main thread alive
            while self.running and not self._stop_event.is_set():
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error starting observer: {e}")
            raise
        finally:
            self.stop()

    def _create_pid_file(self):
        """Create a PID file for process tracking."""
        try:
            pid = str(os.getpid())
            with open(self.pid_file, 'w') as f:
                f.write(pid)
            self.logger.debug(f"Created PID file: {self.pid_file} with PID: {pid}")
        except Exception as e:
            self.logger.error(f"Error creating PID file: {e}")

    def stop(self):
        """Stop the observer service."""
        if self.running:
            self.logger.info("Stopping Workspace Observer service...")
            self.running = False
            self._stop_event.set()

            if self.monitor:
                self.monitor.stop()

            # Stop dispatcher integration if active
            if self.dispatcher_integration:
                self.dispatcher_integration.stop_monitoring()

            # Remove PID file
            self._remove_pid_file()

            self.logger.info("Workspace Observer service stopped")

    def _remove_pid_file(self):
        """Remove the PID file when stopping the service."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.debug(f"Removed PID file: {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Error removing PID file: {e}")

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.stop()
        sys.exit(0)

    def is_running(self):
        """Check if the observer is currently running."""
        return self.running


def run_observer(spec_dir: str = "./specs", pid_file: str = ".observer.pid"):
    """
    Run the workspace observer service.

    Args:
        spec_dir: Directory to monitor for spec file changes
        pid_file: File to store the process ID
    """
    observer = WorkspaceObserver(spec_dir=spec_dir, pid_file=pid_file)
    observer.start()


if __name__ == "__main__":
    # Allow specifying spec directory via command line argument
    spec_directory = sys.argv[1] if len(sys.argv) > 1 else "./specs"
    pid_file = sys.argv[2] if len(sys.argv) > 2 else ".observer.pid"
    run_observer(spec_directory, pid_file)