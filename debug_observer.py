#!/usr/bin/env python3
"""
Debug script to test observer imports
"""
import sys
import os
from pathlib import Path

print("Setting up environment...")
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
os.chdir(Path(__file__).parent)

print("Attempting imports...")
try:
    from observer.monitor import SpecMonitor
    print("✓ SpecMonitor imported successfully")
except Exception as e:
    print(f"✗ Error importing SpecMonitor: {e}")
    import traceback
    traceback.print_exc()

try:
    from observer.utils import setup_logger
    print("✓ setup_logger imported successfully")
except Exception as e:
    print(f"✗ Error importing setup_logger: {e}")
    import traceback
    traceback.print_exc()

try:
    from observer.processor import SpecProcessor
    print("✓ SpecProcessor imported successfully")
except Exception as e:
    print(f"✗ Error importing SpecProcessor: {e}")
    import traceback
    traceback.print_exc()

print("Environment setup and imports completed.")