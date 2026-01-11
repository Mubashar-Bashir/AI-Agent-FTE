#!/usr/bin/env python3
"""
Test Dispatcher Workflow

Demonstrates complete error detection → HITL approval → skill dispatch workflow.

This test:
1. Creates a mock error log with TypeError
2. Uses EventDetector to scan for patterns
3. Generates HITL approval request for high-risk skill
4. Shows approval file in .approvals/ directory
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.dispatcher.config_manager import ConfigManager
from src.dispatcher.logger import ExecutionLogger
from src.dispatcher.event_detector import EventDetector
from src.dispatcher.skill_dispatcher import SkillDispatcher
from src.dispatcher.hitl_approval_manager import HITLApprovalManager
from src.dispatcher.exceptions import ApprovalRequiredError


def main():
    """Run test workflow."""
    print("\n" + "=" * 80)
    print("🧪 DISPATCHER WORKFLOW TEST")
    print("=" * 80)

    # Initialize components
    print("\n📋 Step 1: Initializing components...")
    config_dir = PROJECT_ROOT / "config"
    logs_dir = PROJECT_ROOT / "logs/dispatcher"

    config = ConfigManager(config_dir)
    logger = ExecutionLogger(logs_dir)
    detector = EventDetector(config)
    dispatcher = SkillDispatcher(config, logger)
    approval_manager = HITLApprovalManager()

    print("✅ Components initialized")
    print(f"   - Loaded {len(config.get_event_triggers())} event triggers")
    print(f"   - Loaded {len(config.get_allowed_skills())} allowed skills")

    # Create mock error log
    print("\n📋 Step 2: Creating mock error log...")
    mock_log = """
    2026-01-11 23:00:15 ERROR [application] Request processing failed
    Traceback (most recent call last):
      File "app.py", line 42, in process_request
        result = user.process()
    TypeError: 'NoneType' object has no attribute 'process'

    Stack trace shows user object was None during processing.
    This needs immediate debugging!
    """

    print("✅ Mock error log created:")
    print(mock_log[:200] + "...")

    # Detect events
    print("\n📋 Step 3: Detecting error patterns...")
    triggered_events = detector.detect_events(mock_log)

    if not triggered_events:
        print("❌ No events detected!")
        sys.exit(1)

    print(f"✅ Detected {len(triggered_events)} event(s):")
    for event in triggered_events:
        print(f"   - Type: {event.event_type}")
        print(f"   - Pattern: {event.pattern}")
        print(f"   - Skill: {event.skill_to_invoke}")
        print(f"   - Risk: {event.risk_level.value}")

    # Try to dispatch skill
    print("\n📋 Step 4: Attempting to dispatch skill...")
    trigger = triggered_events[0]

    try:
        # This will raise ApprovalRequiredError for high-risk skills
        record = dispatcher.dispatch_skill(
            trigger=trigger,
            context={"log_content": mock_log},
            execution_depth=0
        )
        print(f"✅ Skill dispatched: {record.id}")

    except ApprovalRequiredError as e:
        print(f"⚠️  Approval required: {e}")

        # Create approval request
        print("\n📋 Step 5: Creating HITL approval request...")

        skill_config = config.get_skill_config(trigger.skill_to_invoke)

        approval_request = approval_manager.create_approval_request(
            trigger_event={
                "type": trigger.event_type,
                "pattern": trigger.pattern,
                "log_excerpt": mock_log[:200]
            },
            skill_to_invoke=trigger.skill_to_invoke,
            risk_level=skill_config.risk_level.value,
            risk_assessment={
                "impact": "Code modification possible",
                "reversibility": "Changes can be reverted via git",
                "data_access": "Read-only file access",
                "network": "No network calls"
            },
            recommended_action="approve",
            reasoning=(
                f"TypeError detected in user processing logic. "
                f"Systematic debugging skill can help identify root cause. "
                f"Risk is controlled as changes are code-only and reversible."
            ),
            timeout_seconds=300,
            auto_approve_on_timeout=False
        )

        print("✅ HITL Approval Request Created!")
        print(f"   Request ID: {approval_request.request_id}")
        print(f"   Skill: {approval_request.skill_to_invoke}")
        print(f"   Risk Level: {approval_request.risk_level}")
        print(f"   Status: {approval_request.status}")
        print(f"   Expires: {approval_request.expires_at}")

        # Show approval file location
        approval_file = PROJECT_ROOT / ".approvals" / f"pending_{approval_request.request_id}.json"
        print(f"\n📁 Approval file created at:")
        print(f"   {approval_file}")

        # Show CLI commands
        print(f"\n📝 Next Steps:")
        print(f"   1. Review approval request:")
        print(f"      python3 src/dispatcher/cli_commands.py list")
        print(f"   ")
        print(f"   2. Approve the request:")
        print(f"      python3 src/dispatcher/cli_commands.py approve {approval_request.request_id} --user mubashar")
        print(f"   ")
        print(f"   3. Or reject it:")
        print(f"      python3 src/dispatcher/cli_commands.py reject {approval_request.request_id} --user mubashar --reason 'Not needed'")

        # Show stats
        print("\n📊 Detector Statistics:")
        stats = detector.get_stats()
        for key, value in stats.items():
            print(f"   - {key}: {value}")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE - HITL Workflow Demonstrated!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
