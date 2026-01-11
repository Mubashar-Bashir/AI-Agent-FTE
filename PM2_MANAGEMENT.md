# PM2 Process Management Guide

## DIG-AI-FTE Services

This project uses PM2 for professional-grade process management of two critical services:

1. **workspace-observer** - Monitors /specs directory and auto-updates Kanban boards
2. **skill-dispatcher** - Detects errors and dispatches skills with HITL approval

## Quick Start

### Start All Services
```bash
./scripts/start_services.sh
```

### Stop All Services
```bash
./scripts/stop_services.sh
```

### Restart All Services
```bash
./scripts/restart_services.sh
```

## PM2 Commands Reference

### Service Management

```bash
# Start services
pm2 start ecosystem.config.js

# Stop all services
pm2 stop all

# Restart all services
pm2 restart all

# Delete all services
pm2 delete all

# Start only one service
pm2 start workspace-observer
pm2 start skill-dispatcher

# Restart individual service
pm2 restart workspace-observer
pm2 restart skill-dispatcher
```

### Monitoring

```bash
# List all services with status
pm2 list

# Show real-time monitoring dashboard
pm2 monit

# View logs for all services
pm2 logs

# View logs for specific service
pm2 logs workspace-observer
pm2 logs skill-dispatcher

# Clear logs
pm2 flush
```

### Advanced Operations

```bash
# Show detailed service info
pm2 show workspace-observer
pm2 show skill-dispatcher

# Save current PM2 configuration
pm2 save

# Resurrect saved configuration
pm2 resurrect

# Setup PM2 to start on system boot
pm2 startup
pm2 save
```

## Service Configuration

Services are configured in `ecosystem.config.js`:

- **workspace-observer**:
  - Script: `src/observer/main.py`
  - Max Memory: 200MB
  - Auto-restart: Yes
  - Logs: `logs/observer/pm2-*.log`

- **skill-dispatcher**:
  - Script: `src/dispatcher/main.py`
  - Max Memory: 200MB
  - Auto-restart: Yes
  - Logs: `logs/dispatcher/pm2-*.log`

## Environment Variables

Set these before starting services:

```bash
# Dispatcher admin token for kill-switch
export DISPATCHER_ADMIN_TOKEN="your-secure-token-here"

# Optional: Override log levels
export OBSERVER_LOG_LEVEL="INFO"
export DISPATCHER_LOG_LEVEL="INFO"
```

## Troubleshooting

### Service won't start
1. Check logs: `pm2 logs <service-name>`
2. Verify Python environment: `which python3`
3. Check file permissions: `ls -la src/*/main.py`
4. Test script manually: `python3 src/observer/main.py`

### Service keeps restarting
1. Check error logs: `pm2 logs <service-name> --err`
2. Review service status: `pm2 show <service-name>`
3. Check for port conflicts or missing dependencies

### High memory usage
- Monitor with: `pm2 monit`
- PM2 will auto-restart if service exceeds 200MB (configurable in ecosystem.config.js)

## Log Files

PM2 logs are separate from application logs:

- **PM2 logs**: `logs/{observer,dispatcher}/pm2-*.log`
- **Application logs**: `logs/{observer,dispatcher}/*.log`

Both are important for troubleshooting!

## Best Practices

1. Always use `pm2 save` after making changes
2. Monitor services regularly with `pm2 monit`
3. Review logs periodically: `pm2 logs`
4. Use `pm2 restart` instead of `pm2 stop` + `pm2 start` for updates
5. Keep ecosystem.config.js under version control

## Integration with Workspace Observer

The workspace-observer automatically updates:
- `30_Specifications/SDD_Tracker.md`
- `30_Specifications/Factory_Board.md`

When spec files in `/specs` change. This provides real-time project tracking for the CEO Automation system.

## Production Deployment

For production deployment:

1. Set strong DISPATCHER_ADMIN_TOKEN
2. Configure PM2 startup: `pm2 startup`
3. Save configuration: `pm2 save`
4. Setup log rotation (PM2 Plus)
5. Configure monitoring alerts
6. Document recovery procedures

---

**Status**: Phase 1-2 Complete
**Next**: Implement User Story 1 (Error Detection) for skill-dispatcher
