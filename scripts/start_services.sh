#!/bin/bash
# Start DIG-AI-FTE Services with PM2
# This script starts both the Workspace Observer and Skill Dispatcher

set -e

PROJECT_DIR="/home/mubashar/code/Hackathon-0/Dig-AI-FTE"

echo "🚀 Starting DIG-AI-FTE Services..."
echo "=================================="

# Navigate to project directory
cd "$PROJECT_DIR"

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 not found. Installing PM2..."
    npm install -g pm2
fi

# Stop any existing instances
echo "🔄 Stopping existing instances..."
pm2 delete workspace-observer 2>/dev/null || true
pm2 delete skill-dispatcher 2>/dev/null || true

# Start services using ecosystem config
echo "✅ Starting services from ecosystem.config.js..."
pm2 start ecosystem.config.js

# Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save

# Setup PM2 startup (optional - for system reboot)
echo "🔧 Setting up PM2 startup script..."
pm2 startup || echo "⚠️  PM2 startup setup requires sudo - skipping for now"

# Show status
echo ""
echo "📊 Service Status:"
pm2 list

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📝 Useful PM2 Commands:"
echo "  pm2 list              - Show all services"
echo "  pm2 logs              - Show logs for all services"
echo "  pm2 logs workspace-observer - Show observer logs"
echo "  pm2 logs skill-dispatcher   - Show dispatcher logs"
echo "  pm2 restart all       - Restart all services"
echo "  pm2 stop all          - Stop all services"
echo "  pm2 monit             - Live monitoring dashboard"
