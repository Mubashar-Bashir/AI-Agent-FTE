#!/bin/bash
# Stop DIG-AI-FTE Services
# This script stops both the Workspace Observer and Skill Dispatcher

set -e

echo "🛑 Stopping DIG-AI-FTE Services..."
echo "=================================="

# Stop services
pm2 stop workspace-observer skill-dispatcher

# Show status
echo ""
echo "📊 Service Status:"
pm2 list

echo ""
echo "✅ Services stopped successfully!"
