/**
 * PM2 Process Management Configuration
 * For DIG-AI-FTE Factory Tracking Engine
 *
 * Services:
 * - workspace-observer: Monitors /specs and updates Kanban boards
 * - skill-dispatcher: Detects errors and dispatches skills with HITL approval
 */

module.exports = {
  apps: [
    {
      name: 'workspace-observer',
      script: 'python3',
      args: 'src/observer/main.py',
      cwd: '/home/mubashar/code/Hackathon-0/Dig-AI-FTE',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
        OBSERVER_LOG_LEVEL: 'INFO'
      },
      error_file: 'logs/observer/pm2-error.log',
      out_file: 'logs/observer/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000
    },
    {
      name: 'skill-dispatcher',
      script: 'python3',
      args: 'src/dispatcher/main.py',
      cwd: '/home/mubashar/code/Hackathon-0/Dig-AI-FTE',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
        DISPATCHER_LOG_LEVEL: 'INFO',
        DISPATCHER_ADMIN_TOKEN: process.env.DISPATCHER_ADMIN_TOKEN || 'change-me-in-production'
      },
      error_file: 'logs/dispatcher/pm2-error.log',
      out_file: 'logs/dispatcher/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000
    }
  ]
};
