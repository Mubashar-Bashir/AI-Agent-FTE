#!/usr/bin/env python3
"""
Direct observer runner for PM2 - bypasses relative import issues
"""
import sys
import os
from pathlib import Path
import time
import signal

def setup_environment():
    """Setup the Python environment with correct paths."""
    # Add the src directory to the Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Change to the project directory to ensure relative imports work correctly
    os.chdir(Path(__file__).parent)

def run_direct_observer(spec_dir: str = "./specs", pid_file: str = ".observer.pid"):
    """
    Run the workspace observer service directly.

    Args:
        spec_dir: Directory to monitor for spec file changes
        pid_file: File to store the process ID
    """
    # Setup environment first
    setup_environment()

    # Import the observer components after environment setup
    from observer.monitor import SpecMonitor
    from observer.utils import setup_logger

    class DirectWorkspaceObserver:
        """Direct implementation of the workspace observer without relative imports."""

        def __init__(self, spec_dir: str = "./specs", pid_file: str = ".observer.pid"):
            self.spec_dir = Path(spec_dir)
            self.pid_file = Path(pid_file)
            self.monitor = None
            self.logger = setup_logger()
            self.running = False

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

                # Keep the main thread alive
                while self.running:
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

                if self.monitor:
                    self.monitor.stop()

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

    observer = DirectWorkspaceObserver(spec_dir=spec_dir, pid_file=pid_file)
    observer.start()

if __name__ == "__main__":
    # Allow specifying spec directory via command line argument
    spec_directory = sys.argv[1] if len(sys.argv) > 1 else "./specs"
    pid_file = sys.argv[2] if len(sys.argv) > 2 else ".observer.pid"
    run_direct_observer(spec_directory, pid_file)