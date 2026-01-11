"""
Main entry point for the Autonomous Skill Dispatcher
"""

import sys
import signal
import logging
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager
from .logger import ExecutionLogger
from .event_detector import EventDetector
from .skill_dispatcher import SkillDispatcher
from .debouncer import Debouncer
from .event_hasher import EventHasher
from .kill_switch import KillSwitch
from .exceptions import ConfigurationError


class DispatcherMain:
    """
    Main dispatcher orchestrator that coordinates all components
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.running = False
        
        # Components (initialized in setup)
        self.config_manager: Optional[ConfigManager] = None
        self.execution_logger: Optional[ExecutionLogger] = None
        self.debouncer: Optional[Debouncer] = None
        self.event_hasher: Optional[EventHasher] = None
        self.event_detector: Optional[EventDetector] = None
        self.skill_dispatcher: Optional[SkillDispatcher] = None
        self.kill_switch: Optional[KillSwitch] = None
        
        # Setup logging
        self.logger = self._setup_basic_logging()
    
    def _setup_basic_logging(self) -> logging.Logger:
        """Setup basic logging before ExecutionLogger is available"""
        logger = logging.getLogger("dispatcher.main")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def setup(self):
        """Initialize all dispatcher components"""
        try:
            self.logger.info("Initializing Autonomous Skill Dispatcher...")
            
            # Load configuration
            self.config_manager = ConfigManager(config_dir=self.config_dir)
            self.logger.info("Configuration loaded successfully")
            
            # Setup execution logger
            log_config = self.config_manager.dispatcher_config.get("logging", {})
            self.execution_logger = ExecutionLogger(
                retention_days=log_config.get("retention_days", 90),
                critical_retention_days=log_config.get("critical_retention_days", 365),
                max_file_size_mb=log_config.get("max_file_size_mb", 100)
            )
            self.logger.info("Execution logger initialized")
            
            # Setup kill-switch
            self.kill_switch = KillSwitch(logger=self.logger)
            self.logger.info("Kill-switch initialized")
            
            # Setup debouncer
            debounce_config = self.config_manager.dispatcher_config.get("debouncing", {})
            self.debouncer = Debouncer(
                time_window_seconds=debounce_config.get("time_window_seconds", 30),
                cache_size_limit=debounce_config.get("cache_size_limit", 1000)
            )
            self.logger.info("Debouncer initialized")
            
            # Setup event hasher
            self.event_hasher = EventHasher()
            self.logger.info("Event hasher initialized")
            
            # Setup event detector
            self.event_detector = EventDetector(
                config_manager=self.config_manager,
                debouncer=self.debouncer,
                event_hasher=self.event_hasher,
                logger=self.logger
            )
            self.logger.info(
                f"Event detector initialized with {len(self.event_detector.get_active_patterns())} patterns"
            )
            
            # Setup skill dispatcher
            self.skill_dispatcher = SkillDispatcher(
                config_manager=self.config_manager,
                execution_logger=self.execution_logger,
                event_hasher=self.event_hasher,
                logger=self.logger
            )
            self.logger.info("Skill dispatcher initialized")
            
            self.logger.info("✓ Dispatcher initialization complete")
            
        except ConfigurationError as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize dispatcher: {e}")
            raise
    
    def process_log_line(self, log_line: str, source_file: str = "") -> int:
        """
        Process a single log line and dispatch any matching skills
        
        Args:
            log_line: The log line to process
            source_file: Optional source file path
            
        Returns:
            Number of skills dispatched
        """
        if not self.event_detector or not self.skill_dispatcher:
            raise RuntimeError("Dispatcher not initialized - call setup() first")
        
        # Check kill-switch first
        if self.kill_switch and self.kill_switch.is_active():
            self.logger.info("Kill-switch active - skipping event processing")
            return 0
        
        # Detect events
        dispatch_requests = self.event_detector.detect_events(log_line, source_file)
        
        if not dispatch_requests:
            return 0
        
        # Dispatch skills
        dispatched_count = 0
        for request in dispatch_requests:
            try:
                record = self.skill_dispatcher.dispatch(request)
                dispatched_count += 1
                
                self.logger.info(
                    f"Dispatched: {request['skill_name']} (status: {record.status})"
                )
                
            except Exception as e:
                self.logger.error(
                    f"Failed to dispatch skill '{request['skill_name']}': {e}"
                )
        
        return dispatched_count
    
    def run(self):
        """
        Run the dispatcher in continuous mode (placeholder for integration)
        
        This will be integrated with the Workspace Observer in Phase 9
        """
        self.logger.info("Dispatcher running in standalone mode...")
        self.logger.info("Waiting for log events (integrate with Observer for full functionality)")
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Keep running until interrupted
        try:
            while self.running:
                # In production, this will receive events from the Observer
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Dispatcher interrupted by user")
        finally:
            self.shutdown()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def shutdown(self):
        """Gracefully shutdown the dispatcher"""
        self.logger.info("Shutting down dispatcher...")
        
        # Cleanup components
        if self.execution_logger:
            self.execution_logger.compress_old_logs()
            self.execution_logger.cleanup_old_logs()
        
        self.logger.info("Dispatcher shutdown complete")


def main():
    """CLI entry point"""
    dispatcher = DispatcherMain()
    
    try:
        dispatcher.setup()
        dispatcher.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
