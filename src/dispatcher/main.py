#!/usr/bin/env python3
"""
Skill Dispatcher Main Entry Point

Autonomous dispatcher that monitors logs for error patterns
and triggers appropriate skills with HITL approval.

Phase 1-2 Complete: Foundational infrastructure ready
Next: Implement User Story 1 (Error Detection)
"""

import sys
import time
import signal
from pathlib import Path
from typing import NoReturn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.dispatcher.config_manager import ConfigManager
from src.dispatcher.logger import ExecutionLogger
from src.dispatcher.atomic_counter import AtomicCounter


class SkillDispatcherService:
    """
    Main dispatcher service.

    Currently implements Phase 1-2 foundational infrastructure.
    User Story implementations (error detection, HITL, etc.) to follow.
    """

    def __init__(self, config_dir: Path):
        """Initialize dispatcher service."""
        self.config_dir = config_dir
        self.running = False

        # Load configuration
        print("📋 Loading configuration...")
        self.config = ConfigManager(config_dir)

        # Setup logging
        logs_dir = PROJECT_ROOT / self.config.get("paths.logs_dir", "logs/dispatcher")
        retention_days = self.config.get("logging.retention_days", 90)
        critical_retention_days = self.config.get("logging.critical_retention_days", 365)
        log_level = self.config.get("logging.log_level", "INFO")

        self.logger = ExecutionLogger(
            logs_dir=logs_dir,
            retention_days=retention_days,
            critical_retention_days=critical_retention_days,
            log_level=log_level
        )

        # Initialize atomic counter for execution depth tracking
        state_file = PROJECT_ROOT / self.config.get("paths.state_file", ".state/global_counter.json")
        lock_file = PROJECT_ROOT / self.config.get("paths.lock_file", "locks/dispatcher.lock")

        self.counter = AtomicCounter(state_file, lock_file)

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        self.logger.info("Dispatcher service initialized (Phase 1-2 Complete)")
        print("✅ Dispatcher service initialized")

    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        print(f"\n🛑 Received shutdown signal ({signum})")
        self.logger.info(f"Shutdown signal received: {signum}")
        self.running = False

    def start(self) -> NoReturn:
        """
        Start the dispatcher service.

        Currently runs as a placeholder service until User Stories are implemented.
        """
        self.running = True

        print("🚀 Skill Dispatcher Service Started")
        print("=" * 50)
        print("Status: Phase 1-2 Complete (Foundational Infrastructure)")
        print("Next: Implement User Story 1 (Error Detection & Triggering)")
        print("")
        print("Configuration:")
        print(f"  - Max Concurrent Dispatches: {self.config.get('dispatcher.max_concurrent_dispatches')}")
        print(f"  - Recursion Depth Limit: {self.config.get('dispatcher.recursion_depth_limit')}")
        print(f"  - Debounce Window: {self.config.get('dispatcher.debounce_window_seconds')}s")
        print(f"  - Allowed Skills: {len(self.config.get_allowed_skills())}")
        print(f"  - Event Triggers: {len(self.config.get_event_triggers())}")
        print("")
        print("Logs: logs/dispatcher/dispatcher.log")
        print("State: .state/global_counter.json")
        print("")
        print("Press Ctrl+C to stop...")
        print("=" * 50)

        self.logger.info("Dispatcher service started - monitoring mode")

        # Main service loop (placeholder until User Story 1 is implemented)
        heartbeat_count = 0
        while self.running:
            try:
                # Heartbeat logging every 60 seconds
                if heartbeat_count % 60 == 0:
                    self.logger.info(
                        f"Service heartbeat - uptime: {heartbeat_count}s, "
                        f"kill_switch: {self.counter.is_kill_switch_active()}"
                    )

                    # Cleanup old logs daily (roughly)
                    if heartbeat_count % 86400 == 0:
                        print("🧹 Cleaning up old logs...")
                        self.logger.cleanup_old_logs()

                time.sleep(1)
                heartbeat_count += 1

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                print(f"⚠️  Error: {e}")
                time.sleep(5)  # Back off on errors

        self._shutdown()

    def _shutdown(self):
        """Perform graceful shutdown."""
        print("\n🛑 Shutting down dispatcher service...")
        self.logger.info("Dispatcher service shutting down")

        # Reset state on clean shutdown
        self.counter.reset()

        print("✅ Dispatcher service stopped cleanly")
        self.logger.info("Dispatcher service stopped")


def main():
    """Main entry point."""
    # Configuration directory
    config_dir = PROJECT_ROOT / "config"

    if not config_dir.exists():
        print(f"❌ Error: Config directory not found at {config_dir}")
        sys.exit(1)

    # Create and start service
    try:
        service = SkillDispatcherService(config_dir)
        service.start()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
