"""
CLI commands for the Autonomous Skill Dispatcher
"""

import argparse
import sys
import os
from typing import Optional

from .hitl_approval_manager import HITLApprovalManager
from .kill_switch import KillSwitch


def setup_cli():
    """Setup command line interface for dispatcher"""
    parser = argparse.ArgumentParser(description="Autonomous Skill Dispatcher CLI")
    parser.add_argument("--config-dir", default="config", help="Configuration directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve a skill execution")
    approve_parser.add_argument("request_id", help="Approval request ID to approve")
    approve_parser.add_argument("--comment", help="Optional comment")
    
    # Reject command
    reject_parser = subparsers.add_parser("reject", help="Reject a skill execution")
    reject_parser.add_argument("request_id", help="Approval request ID to reject")
    reject_parser.add_argument("--reason", help="Reason for rejection")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show dispatcher status")
    
    # Kill-switch commands
    killswitch_parser = subparsers.add_parser("kill-switch", help="Manage kill-switch")
    killswitch_subparsers = killswitch_parser.add_subparsers(dest="killswitch_command")
    
    activate_parser = killswitch_subparsers.add_parser("activate", help="Activate kill-switch")
    activate_parser.add_argument("--reason", help="Reason for activation")
    
    deactivate_parser = killswitch_subparsers.add_parser("deactivate", help="Deactivate kill-switch")
    deactivate_parser.add_argument("--reason", help="Reason for deactivation")
    
    status_parser = killswitch_subparsers.add_parser("status", help="Show kill-switch status")
    
    return parser


def handle_approve(args):
    """Handle approve command"""
    approval_manager = HITLApprovalManager()
    user_identity = os.getenv("USER", "unknown")
    
    success = approval_manager.approve_request(
        request_id=args.request_id,
        user_identity=user_identity,
        comment=args.comment
    )
    
    if success:
        print(f"✓ Approved request: {args.request_id}")
    else:
        print(f"✗ Failed to approve request: {args.request_id}")
        sys.exit(1)


def handle_reject(args):
    """Handle reject command"""
    approval_manager = HITLApprovalManager()
    user_identity = os.getenv("USER", "unknown")
    
    success = approval_manager.reject_request(
        request_id=args.request_id,
        user_identity=user_identity,
        reason=args.reason
    )
    
    if success:
        print(f"✓ Rejected request: {args.request_id}")
    else:
        print(f"✗ Failed to reject request: {args.request_id}")
        sys.exit(1)


def handle_status(args):
    """Handle status command"""
    approval_manager = HITLApprovalManager()
    pending_requests = approval_manager.list_pending_requests()
    
    print("Dispatcher Status:")
    print(f"Pending approval requests: {len(pending_requests)}")
    
    if pending_requests:
        print("\nPending Requests:")
        for req in pending_requests:
            print(f"  - {req['request_id']}: {req['skill_to_invoke']}")


def handle_killswitch(args):
    """Handle kill-switch commands"""
    kill_switch = KillSwitch()
    
    if args.killswitch_command == "activate":
        try:
            kill_switch.activate(reason=args.reason)
            print("✓ Kill-switch activated")
        except Exception as e:
            print(f"✗ Failed to activate kill-switch: {e}")
            sys.exit(1)
    
    elif args.killswitch_command == "deactivate":
        try:
            kill_switch.deactivate(reason=args.reason)
            print("✓ Kill-switch deactivated")
        except Exception as e:
            print(f"✗ Failed to deactivate kill-switch: {e}")
            sys.exit(1)
    
    elif args.killswitch_command == "status":
        active = kill_switch.is_active()
        print(f"Kill-switch status: {'ACTIVE' if active else 'INACTIVE'}")
    
    else:
        print("✗ No kill-switch subcommand specified")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = setup_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "approve":
        handle_approve(args)
    elif args.command == "reject":
        handle_reject(args)
    elif args.command == "status":
        handle_status(args)
    elif args.command == "kill-switch":
        handle_killswitch(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
