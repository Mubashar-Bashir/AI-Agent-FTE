"""
Command-line interface for the Automated Workspace Observer.

This module provides start, stop, restart, and status commands for the observer service.
"""
import argparse
import sys
import os
import signal
import time
import threading
from pathlib import Path
import subprocess
import psutil

from ..observer.main import WorkspaceObserver
from ..config.settings import get_settings


class ObserverCLI:
    """Command-line interface for the observer service."""

    def __init__(self):
        self.settings = get_settings()
        self.pid_file = Path(".observer.pid")

    def start(self, args):
        """Start the observer service."""
        if self.is_running():
            print("Observer service is already running.")
            return False

        print("Starting observer service...")

        # Create a background process to run the observer
        pid = self._start_background_process()

        if pid:
            print(f"Observer service started successfully with PID: {pid}")
            return True
        else:
            print("Failed to start observer service.")
            return False

    def _start_background_process(self):
        """Start the observer as a background process."""
        try:
            # Create the observer process
            cmd = [sys.executable, "-c", f"""
import sys
import os
sys.path.insert(0, '{os.getcwd()}')
from src.observer.main import run_observer
from src.config.settings import get_settings
import atexit

# Write PID to file
pid = str(os.getpid())
with open('.observer.pid', 'w') as f:
    f.write(pid)

# Remove PID file on exit
def cleanup():
    try:
        if os.path.exists('.observer.pid'):
            os.remove('.observer.pid')
    except:
        pass

atexit.register(cleanup)

# Start the observer
settings = get_settings()
run_observer(spec_dir=settings.SPEC_DIR)
"""]

            # Start the process in the background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent process
            )

            # Write PID to file
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            return process.pid

        except Exception as e:
            print(f"Error starting background process: {e}")
            return None

    def stop(self, args):
        """Stop the observer service."""
        if not self.is_running():
            print("Observer service is not running.")
            return False

        print("Stopping observer service...")

        # Read PID from file and terminate the process
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Terminate the process
            process = psutil.Process(pid)
            process.terminate()

            # Wait for the process to terminate
            try:
                process.wait(timeout=10)  # Wait up to 10 seconds
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                process.kill()

            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()

            print("Observer service stopped successfully.")
            return True

        except Exception as e:
            print(f"Error stopping observer service: {e}")

            # Try to remove PID file anyway
            if self.pid_file.exists():
                self.pid_file.unlink()

            return False

    def restart(self, args):
        """Restart the observer service."""
        print("Restarting observer service...")

        # Stop the service if it's running
        if self.is_running():
            if not self.stop(args):
                print("Failed to stop the service for restart.")
                return False

        # Wait a moment
        time.sleep(1)

        # Start the service
        return self.start(args)

    def status(self, args):
        """Check the status of the observer service."""
        if self.is_running():
            print("Observer service is running.")
            try:
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                print(f"PID: {pid}")
            except:
                pass
        else:
            print("Observer service is not running.")

        return True

    def is_running(self):
        """Check if the observer service is currently running."""
        try:
            # Check if PID file exists
            if not self.pid_file.exists():
                return False

            # Read PID from file
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            try:
                process = psutil.Process(pid)
                return process.is_running()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process doesn't exist or we don't have permission to access it
                # Remove the stale PID file
                if self.pid_file.exists():
                    self.pid_file.unlink()
                return False

        except (ValueError, IOError):
            # Invalid PID file or file read error
            return False

    def health_check(self, args):
        """Perform a health check on the observer service."""
        if not self.is_running():
            print("Observer service is not running.")
            return False

        print("Health check: Observer service is running.")

        # Additional health checks can be added here
        # For example: check if the log file is being updated, etc.

        try:
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            print(f"PID: {pid}")

            # Get process info
            process = psutil.Process(int(pid))
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = process.cpu_percent()

            print(f"Memory usage: {memory_usage:.2f} MB")
            print(f"CPU usage: {cpu_percent}%")

            return True
        except Exception as e:
            print(f"Error getting process info: {e}")
            return False

    def run(self):
        """Run the CLI application."""
        parser = argparse.ArgumentParser(description='Automated Workspace Observer CLI')
        parser.add_argument('--version', action='version', version='1.0.0')

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Start command
        start_parser = subparsers.add_parser('start', help='Start the observer service')
        start_parser.add_argument('--spec-dir', help='Directory to monitor for spec files')

        # Stop command
        stop_parser = subparsers.add_parser('stop', help='Stop the observer service')

        # Restart command
        restart_parser = subparsers.add_parser('restart', help='Restart the observer service')

        # Status command
        status_parser = subparsers.add_parser('status', help='Check the status of the observer service')

        # Health check command
        health_parser = subparsers.add_parser('health', help='Perform a health check on the observer service')

        # Parse arguments
        args = parser.parse_args()

        # Handle commands
        if args.command == 'start':
            self.start(args)
        elif args.command == 'stop':
            self.stop(args)
        elif args.command == 'restart':
            self.restart(args)
        elif args.command == 'status':
            self.status(args)
        elif args.command == 'health':
            self.health_check(args)
        else:
            parser.print_help()


def main():
    """Entry point for the CLI."""
    cli = ObserverCLI()
    cli.run()


if __name__ == "__main__":
    main()