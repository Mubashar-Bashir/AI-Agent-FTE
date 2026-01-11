#!/bin/bash
# Restart DIG-AI-FTE Services
# This script restarts both the Workspace Observer and Skill Dispatcher

set -e

echo "🔄 Restarting DIG-AI-FTE Services..."
echo "===================================="

# Restart services
pm2 restart workspace-observer skill-dispatcher

# Show status
echo ""
echo "📊 Service Status:"
pm2 list

echo ""
echo "✅ Services restarted successfully!"
echo ""
echo "📝 View logs with:"
echo "  pm2 logs workspace-observer"
echo "  pm2 logs skill-dispatcher"
