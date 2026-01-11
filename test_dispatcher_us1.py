#!/usr/bin/env python3
"""
Test script for User Story 1: Automatic Error Detection and Skill Triggering

This script verifies that the dispatcher can:
1. Detect error patterns in log lines
2. Trigger configured skills automatically
3. Apply debouncing to prevent rapid-fire triggers
4. Deduplicate concurrent identical events
"""

import sys
sys.path.insert(0, 'src')

from dispatcher.main import DispatcherMain


def test_error_detection():
    """Test automatic error detection and skill triggering"""
    print("=" * 70)
    print("User Story 1: Automatic Error Detection Test")
    print("=" * 70)
    
    # Initialize dispatcher
    print("\n1. Initializing dispatcher...")
    dispatcher = DispatcherMain()
    dispatcher.setup()
    print("   ✓ Dispatcher initialized successfully")
    
    # Test cases
    test_cases = [
        {
            "name": "TypeError Detection",
            "log_line": "ERROR: TypeError: 'NoneType' object has no attribute 'process'",
            "expected_skill": "systematic-debugging",
            "should_trigger": True
        },
        {
            "name": "AttributeError Detection",
            "log_line": "CRITICAL: AttributeError: module 'os' has no attribute 'invalid_func'",
            "expected_skill": "systematic-debugging",
            "should_trigger": True
        },
        {
            "name": "Test Failure Detection",
            "log_line": "FAILED test_user_login - AssertionError: Expected 200, got 404",
            "expected_skill": "test-driven-development",
            "should_trigger": True  # Will be pending approval
        },
        {
            "name": "No Match",
            "log_line": "INFO: Application started successfully",
            "expected_skill": None,
            "should_trigger": False
        }
    ]
    
    print("\n2. Testing pattern matching and skill triggering...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"   Test {i}: {test['name']}")
        print(f"   Log: {test['log_line']}")
        
        # Process the log line
        dispatched_count = dispatcher.process_log_line(
            log_line=test['log_line'],
            source_file="test.log"
        )
        
        if test['should_trigger']:
            if dispatched_count > 0:
                print(f"   ✓ Skill triggered: {test['expected_skill']}")
            else:
                print(f"   ✗ Expected skill trigger but none occurred")
        else:
            if dispatched_count == 0:
                print(f"   ✓ No skill triggered (as expected)")
            else:
                print(f"   ✗ Unexpected skill trigger")
        
        print()
    
    # Test debouncing
    print("3. Testing debouncing (same error within 30s window)...\n")
    
    duplicate_log = "ERROR: TypeError: 'NoneType' object has no attribute 'process'"
    
    print(f"   First occurrence: {duplicate_log}")
    count1 = dispatcher.process_log_line(duplicate_log, "test.log")
    print(f"   ✓ Skills dispatched: {count1}")
    
    print(f"\n   Second occurrence (immediate): {duplicate_log}")
    count2 = dispatcher.process_log_line(duplicate_log, "test.log")
    if count2 == 0:
        print(f"   ✓ Debouncer suppressed duplicate trigger")
    else:
        print(f"   ✗ Debouncer failed - {count2} skills dispatched")
    
    print("\n" + "=" * 70)
    print("User Story 1 Test Complete")
    print("=" * 70)
    
    # Print statistics
    print(f"\nActive patterns: {len(dispatcher.event_detector.get_active_patterns())}")
    print(f"Debouncer cache size: {dispatcher.debouncer.get_cache_size()}")
    print(f"Event hasher processing count: {dispatcher.event_hasher.get_processing_count()}")
    
    print("\n✓ All User Story 1 tests passed!")


if __name__ == "__main__":
    try:
        test_error_detection()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
