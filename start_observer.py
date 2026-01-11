#!/usr/bin/env python3
"""
Wrapper script for the Workspace Observer to run with PM2
"""
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to the project directory to ensure relative imports work correctly
os.chdir(Path(__file__).parent)

# Import and run the observer
from observer.main import run_observer

if __name__ == "__main__":
    # Run the observer with the default spec directory
    spec_dir = "./specs"
    pid_file = ".observer.pid"

    # Override with command line args if provided
    if len(sys.argv) > 1:
        spec_dir = sys.argv[1]
    if len(sys.argv) > 2:
        pid_file = sys.argv[2]

    run_observer(spec_dir=spec_dir, pid_file=pid_file)