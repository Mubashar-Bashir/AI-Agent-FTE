#!/usr/bin/env python3
"""
Dispatcher CLI Commands (T032 - User Story 2)

Command-line interface for managing dispatcher operations:
- Approve/reject approval requests
- List pending approvals
- Kill-switch operations
"""

import sys
import argparse
from pathlib import Path
from typing import NoReturn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.dispatcher.hitl_approval_manager import HITLApprovalManager
from src.dispatcher.atomic_counter import AtomicCounter
from src.dispatcher.lock_manager import LockManager


class DispatcherCLI:
    """CLI for dispatcher operations."""

    def __init__(self):
        """Initialize CLI."""
        self.approval_manager = HITLApprovalManager()
        self.state_file = PROJECT_ROOT / ".state/global_counter.json"
        self.lock_file = PROJECT_ROOT / "locks/dispatcher.lock"
        self.counter = AtomicCounter(self.state_file, self.lock_file)

    def list_approvals(self) -> NoReturn:
        """List all pending approval requests."""
        pending = self.approval_manager.list_pending_requests()

        if not pending:
            print("✅ No pending approval requests")
            sys.exit(0)

        print(f"\n📋 Pending Approval Requests ({len(pending)}):")
        print("=" * 80)

        for request in pending:
            print(f"\n🆔 Request ID: {request.request_id}")
            print(f"   Skill: {request.skill_to_invoke}")
            print(f"   Risk Level: {request.risk_level.upper()}")
            print(f"   Trigger: {request.trigger_event.get('type', 'unknown')}")
            print(f"   Created: {request.timestamp}")
            print(f"   Expires: {request.expires_at}")
            print(f"   Recommended: {request.recommended_action.upper()}")
            print(f"   Reasoning: {request.reasoning}")
            print(f"\n   To approve: dispatcher approve {request.request_id}")
            print(f"   To reject:  dispatcher reject {request.request_id}")
            print("-" * 80)

        sys.exit(0)

    def approve_request(self, request_id: str, user: str, comment: str = None) -> NoReturn:
        """Approve an approval request."""
        try:
            self.approval_manager.approve_request(request_id, user, comment)
            print(f"✅ Approved request {request_id}")
            print(f"   User: {user}")
            if comment:
                print(f"   Comment: {comment}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error approving request: {e}")
            sys.exit(1)

    def reject_request(self, request_id: str, user: str, reason: str = None) -> NoReturn:
        """Reject an approval request."""
        try:
            self.approval_manager.reject_request(request_id, user, reason)
            print(f"❌ Rejected request {request_id}")
            print(f"   User: {user}")
            if reason:
                print(f"   Reason: {reason}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error rejecting request: {e}")
            sys.exit(1)

    def kill_switch_activate(self, user: str, reason: str = None) -> NoReturn:
        """Activate kill-switch."""
        try:
            self.counter.update_kill_switch(True)
            print("🚨 KILL-SWITCH ACTIVATED")
            print(f"   User: {user}")
            if reason:
                print(f"   Reason: {reason}")
            print("\n   All skill dispatches are now BLOCKED")
            print("   To deactivate: dispatcher kill-switch deactivate")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error activating kill-switch: {e}")
            sys.exit(1)

    def kill_switch_deactivate(self, user: str) -> NoReturn:
        """Deactivate kill-switch."""
        try:
            self.counter.update_kill_switch(False)
            print("✅ Kill-switch deactivated")
            print(f"   User: {user}")
            print("\n   Skill dispatches are now ENABLED")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error deactivating kill-switch: {e}")
            sys.exit(1)

    def kill_switch_status(self) -> NoReturn:
        """Show kill-switch status."""
        try:
            is_active = self.counter.is_kill_switch_active()
            state = self.counter.get_state()

            print("\n📊 Kill-Switch Status:")
            print("=" * 80)
            print(f"   Active: {'🚨 YES (BLOCKING ALL DISPATCHES)' if is_active else '✅ NO (NORMAL OPERATION)'}")
            print(f"   Current Execution Depth: {state.global_execution_depth}")
            print(f"   Active Instances: {len(state.instances)}")
            print(f"   Last Updated: {state.last_updated}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error checking kill-switch status: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dispatcher CLI - Manage approval requests and kill-switch"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List pending approval requests")

    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve a request")
    approve_parser.add_argument("request_id", help="Request ID to approve")
    approve_parser.add_argument("--user", required=True, help="Your username/identity")
    approve_parser.add_argument("--comment", help="Optional approval comment")

    # Reject command
    reject_parser = subparsers.add_parser("reject", help="Reject a request")
    reject_parser.add_argument("request_id", help="Request ID to reject")
    reject_parser.add_argument("--user", required=True, help="Your username/identity")
    reject_parser.add_argument("--reason", help="Rejection reason")

    # Kill-switch command
    killswitch_parser = subparsers.add_parser("kill-switch", help="Manage kill-switch")
    killswitch_parser.add_argument(
        "action",
        choices=["activate", "deactivate", "status"],
        help="Kill-switch action"
    )
    killswitch_parser.add_argument("--user", help="Your username/identity (required for activate/deactivate)")
    killswitch_parser.add_argument("--reason", help="Reason for activation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = DispatcherCLI()

    # Execute command
    if args.command == "list":
        cli.list_approvals()

    elif args.command == "approve":
        cli.approve_request(args.request_id, args.user, args.comment)

    elif args.command == "reject":
        cli.reject_request(args.request_id, args.user, args.reason)

    elif args.command == "kill-switch":
        if args.action == "status":
            cli.kill_switch_status()
        elif args.action == "activate":
            if not args.user:
                print("❌ Error: --user required for activate")
                sys.exit(1)
            cli.kill_switch_activate(args.user, args.reason)
        elif args.action == "deactivate":
            if not args.user:
                print("❌ Error: --user required for deactivate")
                sys.exit(1)
            cli.kill_switch_deactivate(args.user)


if __name__ == "__main__":
    main()
