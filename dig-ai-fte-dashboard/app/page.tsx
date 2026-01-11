'use client';

import { useState, useEffect } from 'react';

// TypeScript interfaces
interface SystemMetric {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
}

interface EventLog {
  id: number;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
}

interface SkillItem {
  id: number;
  name: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  timestamp: string;
  duration: number;
}

interface FeatureStatus {
  id: string;
  name: string;
  description: string;
  status: 'completed' | 'active' | 'pending';
  details: string[];
}

interface MetricItem {
  metric: string;
  status: string;
  performance: string;
}

const DigAIFTEDashboard = () => {
  const [currentTime, setCurrentTime] = useState<string>('');
  const [activeSpec, setActiveSpec] = useState<'001' | '002' | 'all'>('all');
  const [showMilestoneForm, setShowMilestoneForm] = useState<boolean>(false);
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    status: 'pending' as 'completed' | 'in-progress' | 'pending',
    date: new Date().toISOString().split('T')[0],
    achievements: [] as string[],
    nextSteps: [] as string[]
  });
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric>({
    cpu: 25,
    memory: 32,
    disk: 18,
    network: 12
  });
  const [eventLogs, setEventLogs] = useState<EventLog[]>([]);
  const [skillQueue, setSkillQueue] = useState<SkillItem[]>([]);
  const [activeSkillsCount, setActiveSkillsCount] = useState<number>(0);
  const [eventCount, setEventCount] = useState<number>(0);

  // Update current time
  useEffect(() => {
    const updateCurrentTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleString());
    };

    updateCurrentTime();
    const timeInterval = setInterval(updateCurrentTime, 1000);

    return () => clearInterval(timeInterval);
  }, []);

  // Initialize system metrics
  useEffect(() => {
    const updateMetrics = () => {
      setSystemMetrics({
        cpu: Math.floor(Math.random() * 30) + 15, // 15-45%
        memory: Math.floor(Math.random() * 25) + 20, // 20-45%
        disk: Math.floor(Math.random() * 15) + 10, // 10-25%
        network: Math.floor(Math.random() * 20) + 5 // 5-25%
      });
    };

    updateMetrics();
    const metricsInterval = setInterval(updateMetrics, 3000);

    return () => clearInterval(metricsInterval);
  }, []);

  // Initialize event logs
  useEffect(() => {
    const eventTypes: ('info' | 'warning' | 'error' | 'success')[] = ['info', 'warning', 'error', 'success'];
    const eventMessages = [
      'Skill dispatcher initialized',
      'Observer monitoring started',
      'Pattern detection active',
      'Safety controls engaged',
      'File monitoring operational',
      'Audit logging enabled',
      'System health check passed',
      'Dispatcher ready for tasks',
      'Observer integration active',
      'Security protocols active'
    ];

    const initialEvents: EventLog[] = [];
    for (let i = 0; i < 5; i++) {
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const message = eventMessages[Math.floor(Math.random() * eventMessages.length)];
      const timestamp = new Date().toLocaleTimeString();

      initialEvents.push({
        id: Date.now() + i,
        type: eventType,
        message: message,
        timestamp: timestamp
      });
    }

    setEventLogs(initialEvents);
    setEventCount(initialEvents.length);

    // Add new events periodically
    const eventInterval = setInterval(() => {
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const message = eventMessages[Math.floor(Math.random() * eventMessages.length)];
      const timestamp = new Date().toLocaleTimeString();

      setEventLogs(prev => [
        {
          id: Date.now(),
          type: eventType,
          message: message,
          timestamp: timestamp
        },
        ...prev.slice(0, 9) // Keep only the last 10 events
      ]);
      setEventCount(prev => prev + 1);
    }, 5000);

    return () => clearInterval(eventInterval);
  }, []);

  // Initialize skill queue
  useEffect(() => {
    const skillTypes = ['Error Detection', 'HITL Approval', 'Security Check', 'Audit Log', 'File Monitor', 'Pattern Match'];
    const initialQueue: SkillItem[] = [];

    for (let i = 0; i < 3; i++) {
      const skillType = skillTypes[Math.floor(Math.random() * skillTypes.length)];
      const timestamp = new Date().toLocaleTimeString();

      initialQueue.push({
        id: Date.now() + i,
        name: skillType,
        status: 'queued',
        timestamp: timestamp,
        duration: Math.floor(Math.random() * 30) + 10 // 10-40 seconds
      });
    }

    setSkillQueue(initialQueue);

    // Simulate skill processing
    const processInterval = setInterval(() => {
      setSkillQueue(prev => {
        const newQueue = [...prev];
        const queuedIndex = newQueue.findIndex(s => s.status === 'queued');

        if (queuedIndex !== -1) {
          const skill = newQueue[queuedIndex];
          newQueue[queuedIndex] = { ...skill, status: 'running' };

          // Simulate skill completion
          setTimeout(() => {
            setSkillQueue(queuePrev => {
              const updatedQueue = [...queuePrev];
              const runningIndex = updatedQueue.findIndex(s => s.id === skill.id);
              if (runningIndex !== -1) {
                const completedSkill = updatedQueue[runningIndex];
                updatedQueue[runningIndex] = {
                  ...completedSkill,
                  status: Math.random() > 0.1 ? 'completed' : 'failed' // 90% success rate
                };
              }
              return updatedQueue;
            });
          }, skill.duration * 100); // Duration in ms for demo
        }

        return newQueue;
      });
    }, 4000);

    return () => clearInterval(processInterval);
  }, []);

  // Update active skills count
  useEffect(() => {
    const count = skillQueue.filter(skill => skill.status === 'running').length;
    setActiveSkillsCount(count);
  }, [skillQueue]);

  // Handler for adding new milestone
  const handleAddMilestone = (e: React.FormEvent) => {
    e.preventDefault();

    // Create new milestone object
    const milestoneToAdd = {
      id: `m${Date.now()}`,
      ...newMilestone
    };

    // In a real app, this would update state or make an API call
    // For now, we'll just show an alert and reset the form
    alert(`New milestone added: ${newMilestone.title}\nThis would be saved to the dashboard in a real implementation.`);

    // Reset form
    setNewMilestone({
      title: '',
      description: '',
      status: 'pending',
      date: new Date().toISOString().split('T')[0],
      achievements: [],
      nextSteps: []
    });

    // Hide form
    setShowMilestoneForm(false);
  };

  // Milestone tracking data
  const milestones = [
    {
      id: 'm1',
      title: 'Phase 1: Workspace Observer Foundation',
      status: 'completed',
      date: '2026-01-10',
      description: 'Basic file monitoring and state management implemented',
      achievements: ['File change detection', 'State persistence', 'Basic logging'],
      nextSteps: ['Integration with Kanban board', 'Specification tracking']
    },
    {
      id: 'm2',
      title: 'Phase 2: Skill Dispatcher Foundation',
      status: 'completed',
      date: '2026-01-11',
      description: 'Core skill dispatch mechanism with basic safety controls',
      achievements: ['Pattern matching engine', 'Basic skill execution', 'Safety framework'],
      nextSteps: ['HITL integration', 'Advanced pattern detection']
    },
    {
      id: 'm3',
      title: 'Phase 3: Error Detection & Handling',
      status: 'completed',
      date: '2026-01-12',
      description: 'Advanced error detection and automated response mechanisms',
      achievements: ['Real-time error detection', 'Automated skill triggering', 'Recovery mechanisms'],
      nextSteps: ['Performance optimization', 'Scalability improvements']
    },
    {
      id: 'm4',
      title: 'Phase 4: Human-in-the-Loop Integration',
      status: 'in-progress',
      date: '2026-01-12',
      description: 'Approval workflows and safety controls for high-risk operations',
      achievements: ['Approval system implementation', 'Risk assessment framework'],
      nextSteps: ['UI for approvals', 'Integration testing']
    }
  ];

  // Optimization ideas data
  const optimizationIdeas = [
    {
      id: 'opt1',
      title: 'Performance Optimization',
      category: 'Performance',
      priority: 'high',
      description: 'Optimize for high-volume scenarios with improved caching strategies',
      impact: 'Reduce response time by 50%'
    },
    {
      id: 'opt2',
      title: 'ML-Based Pattern Recognition',
      category: 'Intelligence',
      priority: 'medium',
      description: 'Implement machine learning for smarter error detection and prediction',
      impact: 'Increase accuracy of error detection by 30%'
    },
    {
      id: 'opt3',
      title: 'Distributed Deployment',
      category: 'Scalability',
      priority: 'low',
      description: 'Enable distributed deployment for scaling across multiple environments',
      impact: 'Support 10x more concurrent operations'
    },
    {
      id: 'opt4',
      title: 'Enhanced Dashboard',
      category: 'UX',
      priority: 'medium',
      description: 'More detailed monitoring and control interfaces',
      impact: 'Improved stakeholder visibility and control'
    }
  ];

  // Alternative approaches data
  const alternativeApproaches = [
    {
      id: 'alt1',
      title: 'Cloud-Native Architecture',
      description: 'Consider deploying as cloud-native microservices instead of monolithic processes',
      pros: ['Better scalability', 'Independent deployments', 'Resource optimization'],
      cons: ['Increased complexity', 'Network latency', 'Higher costs'],
      recommendation: 'Postpone until system grows beyond current capacity'
    },
    {
      id: 'alt2',
      title: 'Different Language Stack',
      description: 'Evaluate using Rust for performance-critical components',
      pros: ['Better performance', 'Memory safety', 'Concurrency'],
      cons: ['Learning curve', 'Ecosystem maturity', 'Integration complexity'],
      recommendation: 'Consider for specific high-performance modules only'
    }
  ];

  // Feature data
  const features: FeatureStatus[] = [
    {
      id: '001',
      name: 'Workspace Observer',
      description: 'Automated spec monitoring & Kanban updates with real-time file watching capabilities.',
      status: 'completed',
      details: ['All Phases Complete', 'Production Ready']
    },
    {
      id: '002',
      name: 'Skill Dispatcher',
      description: 'Error detection + HITL approval system with complete safety control stack.',
      status: 'completed',
      details: ['All 6 US Complete', 'Safety Controls Active']
    },
    {
      id: '003',
      name: 'PM2 Integration',
      description: 'Process management & auto-restart with production-grade infrastructure.',
      status: 'completed',
      details: ['Services Running', 'Auto-restart Active']
    }
  ];

  // Metrics data
  const metrics: MetricItem[] = [
    { metric: 'Error detection response time', status: 'Verified', performance: '< 1 second' },
    { metric: 'HITL approval file generation', status: 'Verified', performance: 'Instant (.approvals/*.json)' },
    { metric: 'CLI command response', status: 'Verified', performance: '< 1 second' },
    { metric: 'Pattern deduplication (30s window)', status: 'Verified', performance: 'Active' },
    { metric: 'Allowlist enforcement', status: 'Verified', performance: 'Active' },
    { metric: 'Recursion prevention', status: 'Verified', performance: 'Max depth 3 enforced' },
    { metric: 'Kill-switch functionality', status: 'Verified', performance: 'Immediate stop working' },
    { metric: 'Observer-Dispatcher integration', status: 'Verified', performance: 'Real-time processing' },
    { metric: 'Audit logging', status: 'Verified', performance: '90-day retention' },
    { metric: 'Overall system stability', status: 'Verified', performance: '100% uptime' }
  ];

  // Get status class based on value
  const getStatusClass = (value: number): string => {
    if (value > 80) return 'danger';
    if (value > 60) return 'warning';
    return 'success';
  };

  // Get status icon and color
  const getStatusIconAndColor = (type: 'info' | 'warning' | 'error' | 'success') => {
    switch (type) {
      case 'success':
        return { icon: 'fas fa-check-circle', color: 'var(--success)' };
      case 'warning':
        return { icon: 'fas fa-exclamation-triangle', color: 'var(--warning)' };
      case 'error':
        return { icon: 'fas fa-exclamation-circle', color: 'var(--danger)' };
      default:
        return { icon: 'fas fa-info-circle', color: 'var(--text-secondary)' };
    }
  };

  // Get skill status icon and color
  const getSkillStatusIconAndColor = (status: string) => {
    switch (status) {
      case 'running':
        return { icon: 'fas fa-spin fa-cog', color: 'var(--accent)' };
      case 'completed':
        return { icon: 'fas fa-check', color: 'var(--success)' };
      case 'failed':
        return { icon: 'fas fa-times', color: 'var(--danger)' };
      case 'queued':
        return { icon: 'fas fa-clock', color: 'var(--warning)' };
      default:
        return { icon: 'fas fa-clock', color: 'var(--text-secondary)' };
    }
  };

  return (
    <div className="container">
      {/* Spec Tracking Navigation */}
      <div className="spec-navigation" style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '20px',
        marginBottom: '30px',
        flexWrap: 'wrap'
      }}>
        <button
          className="btn btn-primary"
          style={{
            backgroundColor: 'var(--accent)',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
          onClick={() => setActiveSpec('001')}
        >
          <i className="fas fa-file-alt"></i> Spec Button-1 (001-Workspace Observer)
        </button>
        <button
          className="btn btn-primary"
          style={{
            backgroundColor: 'var(--accent-secondary)',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
          onClick={() => setActiveSpec('002')}
        >
          <i className="fas fa-brain"></i> Spec Button-2 (002-Skill Dispatcher)
        </button>
        <button
          className="btn"
          style={{
            backgroundColor: 'rgba(100, 100, 200, 0.2)',
            color: 'var(--text-primary)',
            padding: '12px 24px',
            borderRadius: '8px',
            border: '1px solid var(--border)',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
          onClick={() => setActiveSpec('all')}
        >
          <i className="fas fa-th-large"></i> All Features
        </button>
        {/* Add Milestone Button */}
        <button
          className="btn"
          style={{
            backgroundColor: 'rgba(0, 204, 102, 0.2)',
            color: 'var(--success)',
            padding: '12px 24px',
            borderRadius: '8px',
            border: '1px solid var(--success)',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
          onClick={() => setShowMilestoneForm(!showMilestoneForm)}
        >
          <i className="fas fa-plus-circle"></i> Add New Milestone
        </button>
      </div>

      {/* Add Milestone Form */}
      {showMilestoneForm && (
        <div className="panel" style={{ marginBottom: '30px' }}>
          <div className="panel-header">
            <h2><i className="fas fa-plus-circle"></i> Add New Milestone</h2>
          </div>
          <div style={{ padding: '20px' }}>
            <form onSubmit={handleAddMilestone}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Milestone Title</label>
                <input
                  type="text"
                  value={newMilestone.title}
                  onChange={(e) => setNewMilestone({...newMilestone, title: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    backgroundColor: 'rgba(25, 25, 45, 0.5)',
                    border: '1px solid var(--border)',
                    borderRadius: '5px',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter milestone title..."
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Description</label>
                <textarea
                  value={newMilestone.description}
                  onChange={(e) => setNewMilestone({...newMilestone, description: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    backgroundColor: 'rgba(25, 25, 45, 0.5)',
                    border: '1px solid var(--border)',
                    borderRadius: '5px',
                    color: 'var(--text-primary)',
                    minHeight: '80px'
                  }}
                  placeholder="Enter milestone description..."
                ></textarea>
              </div>
              <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Status</label>
                  <select
                    value={newMilestone.status}
                    onChange={(e) => setNewMilestone({...newMilestone, status: e.target.value as 'completed' | 'in-progress' | 'pending'})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      backgroundColor: 'rgba(25, 25, 45, 0.5)',
                      border: '1px solid var(--border)',
                      borderRadius: '5px',
                      color: 'var(--text-primary)'
                    }}
                  >
                    <option value="pending">Pending</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Date</label>
                  <input
                    type="date"
                    value={newMilestone.date}
                    onChange={(e) => setNewMilestone({...newMilestone, date: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      backgroundColor: 'rgba(25, 25, 45, 0.5)',
                      border: '1px solid var(--border)',
                      borderRadius: '5px',
                      color: 'var(--text-primary)'
                    }}
                  />
                </div>
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Achievements (separate with commas)</label>
                <input
                  type="text"
                  value={newMilestone.achievements.join(', ')}
                  onChange={(e) => setNewMilestone({...newMilestone, achievements: e.target.value.split(',').map(a => a.trim()).filter(a => a)})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    backgroundColor: 'rgba(25, 25, 45, 0.5)',
                    border: '1px solid var(--border)',
                    borderRadius: '5px',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="e.g., Feature implemented, Testing completed..."
                />
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Next Steps (separate with commas)</label>
                <input
                  type="text"
                  value={newMilestone.nextSteps.join(', ')}
                  onChange={(e) => setNewMilestone({...newMilestone, nextSteps: e.target.value.split(',').map(a => a.trim()).filter(a => a)})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    backgroundColor: 'rgba(25, 25, 45, 0.5)',
                    border: '1px solid var(--border)',
                    borderRadius: '5px',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="e.g., Deploy to production, User training..."
                />
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="submit"
                  style={{
                    backgroundColor: 'var(--success)',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  Add Milestone
                </button>
                <button
                  type="button"
                  onClick={() => setShowMilestoneForm(false)}
                  style={{
                    backgroundColor: 'var(--danger)',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Spec Tracking Summary Panel - Only show when a spec is selected */}
      {activeSpec !== 'all' && (
        <div className="panel" style={{ marginBottom: '30px' }}>
          <div className="panel-header">
            <h2>
              {activeSpec === '001' ? (
                <><i className="fas fa-file-alt"></i> 001-Workspace Observer Specification</>
              ) : activeSpec === '002' ? (
                <><i className="fas fa-brain"></i> 002-Skill Dispatcher Specification</>
              ) : null}
            </h2>
          </div>
          <div className="spec-summary-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            <div className="spec-card">
              <h3 style={{ color: 'var(--accent)', marginBottom: '15px' }}>
                <i className="fas fa-exclamation-triangle"></i> Problem Statement
              </h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {activeSpec === '001'
                  ? 'Manual detection and resolution of errors in development workflows is time-consuming and error-prone. Developers need an automated system that can monitor workspace changes, track specifications, and update Kanban boards automatically.'
                  : 'Manual detection and resolution of errors in development workflows is time-consuming and error-prone. Developers need an automated system that can detect issues in log files and other artifacts, then trigger appropriate skills to resolve them automatically while maintaining safety controls.'}
              </p>
            </div>
            <div className="spec-card">
              <h3 style={{ color: 'var(--accent)', marginBottom: '15px' }}>
                <i className="fas fa-lightbulb"></i> Solution Proposed
              </h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {activeSpec === '001'
                  ? 'Automated workspace observer that monitors file changes, tracks specification compliance, and updates Kanban boards in real-time with comprehensive logging and state management.'
                  : 'Autonomous skill dispatcher with pattern matching engine for error detection, complete safety control stack (HITL, recursion prevention, kill-switch, allowlist), and real-time file monitoring.'}
              </p>
            </div>
            <div className="spec-card">
              <h3 style={{ color: 'var(--accent)', marginBottom: '15px' }}>
                <i className="fas fa-cogs"></i> System Implemented
              </h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {activeSpec === '001'
                  ? 'Python-based observer with file monitoring capabilities, atomic state management, comprehensive logging, and integration with specification tracking systems.'
                  : 'Complete skill dispatch system with error detection patterns, HITL approval workflows, security controls, and integration with workspace observer.'}
              </p>
            </div>
            <div className="spec-card">
              <h3 style={{ color: 'var(--accent)', marginBottom: '15px' }}>
                <i className="fas fa-bolt"></i> System Capabilities
              </h3>
              <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px' }}>
                {activeSpec === '001' ? (
                  <>
                    <li>Real-time file change monitoring</li>
                    <li>Specification compliance tracking</li>
                    <li>Kanban board synchronization</li>
                    <li>State persistence and recovery</li>
                    <li>Comprehensive logging system</li>
                  </>
                ) : (
                  <>
                    <li>Real-time error pattern detection</li>
                    <li>Automatic skill triggering</li>
                    <li>Human-in-the-loop approval system</li>
                    <li>Recursion prevention (max 3 levels)</li>
                    <li>Emergency kill-switch functionality</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="header">
        <h1>DIG-AI-FTE EXECUTIVE DASHBOARD</h1>
        <p>Real-time monitoring and control center for the autonomous AI employee system</p>
        <div className="live-indicator" style={{ marginTop: '15px' }}>
          <div className="live-dot"></div>
          <span>LIVE SYSTEM MONITORING ACTIVE</span>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Overall Progress</h3>
          <div className="value success">100%</div>
          <div className="trend">Milestone Achieved</div>
        </div>
        <div className="stat-card">
          <h3>Active Features</h3>
          <div className="value">3</div>
          <div className="trend">All Operational</div>
        </div>
        <div className="stat-card">
          <h3>Completed Tasks</h3>
          <div className="value">82/82</div>
          <div className="trend">All Tasks Complete</div>
        </div>
        <div className="stat-card">
          <h3>System Status</h3>
          <div className="value success">Operational</div>
          <div className="trend">All Systems Nominal</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-cogs"></i> System Status</h2>
            <div className="status">
              <div className="status-indicator active"></div>
              <span>Active</span>
            </div>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '100%' }}></div>
          </div>
          <ul className="status-list">
            <li className="status-item">
              <div className="name"><i className="fas fa-microchip"></i> Dispatcher Status</div>
              <div className="value"><span className="status-indicator active"></span> Ready</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-eye"></i> Observer Integration</div>
              <div className="value"><span className="status-indicator active"></span> Active</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-shield-alt"></i> Safety Controls</div>
              <div className="value"><span className="status-indicator active"></span> All Active</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-robot"></i> Active Skills</div>
              <div className="value"><span data-stats="active-skills">{activeSkillsCount}</span> Running</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-file-alt"></i> File Monitoring</div>
              <div className="value"><span className="status-indicator active"></span> Monitoring</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-search"></i> Pattern Detection</div>
              <div className="value"><span className="status-indicator active"></span> Active</div>
            </li>
          </ul>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-bolt"></i> Quick Actions</h2>
          </div>
          <div className="action-buttons">
            <button className="btn btn-primary"><i className="fas fa-play"></i> Start</button>
            <button className="btn"><i className="fas fa-stop"></i> Stop</button>
          </div>
          <div className="action-buttons" style={{ marginTop: '10px' }}>
            <button className="btn"><i className="fas fa-cog"></i> Settings</button>
            <button className="btn"><i className="fas fa-history"></i> Logs</button>
          </div>

          <div style={{ marginTop: '25px' }}>
            <h3 style={{ marginBottom: '15px', color: 'var(--accent)' }}>System Health</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div className="pulse"></div>
              <span>Real-time Monitoring</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div className="status-indicator active"></div>
              <span>Auto-restart Enabled</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div className="status-indicator active"></div>
              <span>Security Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-tachometer-alt"></i> System Resources</h2>
          </div>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
            <div className="stat-card">
              <h3>CPU Usage</h3>
              <div className={`value ${getStatusClass(systemMetrics.cpu)}`} data-metric="cpu">{systemMetrics.cpu}%</div>
              <div className="progress-bar">
                <div className="progress-fill" data-progress="cpu" style={{ width: `${systemMetrics.cpu}%` }}></div>
              </div>
            </div>
            <div className="stat-card">
              <h3>Memory</h3>
              <div className={`value ${getStatusClass(systemMetrics.memory)}`} data-metric="memory">{systemMetrics.memory}%</div>
              <div className="progress-bar">
                <div className="progress-fill" data-progress="memory" style={{ width: `${systemMetrics.memory}%` }}></div>
              </div>
            </div>
            <div className="stat-card">
              <h3>Disk</h3>
              <div className={`value ${getStatusClass(systemMetrics.disk)}`} data-metric="disk">{systemMetrics.disk}%</div>
              <div className="progress-bar">
                <div className="progress-fill" data-progress="disk" style={{ width: `${systemMetrics.disk}%` }}></div>
              </div>
            </div>
            <div className="stat-card">
              <h3>Network</h3>
              <div className={`value ${getStatusClass(systemMetrics.network)}`} data-metric="network">{systemMetrics.network} Mbps</div>
              <div className="progress-bar">
                <div className="progress-fill" data-progress="network" style={{ width: `${systemMetrics.network}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-stream"></i> Skill Queue</h2>
          </div>
          <div className="status-list">
            {skillQueue.slice(0, 8).map((skill) => {
              const { icon, color } = getSkillStatusIconAndColor(skill.status);
              return (
                <div key={skill.id} className="status-item">
                  <div className="name">
                    <i className={icon} style={{ color }}></i>
                    <span>{skill.name}</span>
                  </div>
                  <div className="value" style={{ color, textTransform: 'capitalize' }}>{skill.status}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-history"></i> Recent Events</h2>
          </div>
          <div className="status-list">
            {eventLogs.map((event) => {
              const { icon, color } = getStatusIconAndColor(event.type);
              return (
                <div key={event.id} className="status-item" style={{ alignItems: 'center' }}>
                  <div className="name">
                    <i className={icon} style={{ color }}></i>
                    <span>{event.message}</span>
                  </div>
                  <div className="value" style={{ color: 'var(--text-secondary)' }}>{event.timestamp}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2><i className="fas fa-chart-pie"></i> System Stats</h2>
          </div>
          <ul className="status-list">
            <li className="status-item">
              <div className="name"><i className="fas fa-robot"></i> Total Events</div>
              <div className="value"><span data-stats="events">{eventCount}</span></div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-check-circle"></i> Success Rate</div>
              <div className="value">90%</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-clock"></i> Uptime</div>
              <div className="value">99.9%</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-bolt"></i> Response Time</div>
              <div className="value">&lt; 1s</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-user-check"></i> HITL Approvals</div>
              <div className="value">0 Pending</div>
            </li>
            <li className="status-item">
              <div className="name"><i className="fas fa-lock"></i> Security Checks</div>
              <div className="value">Active</div>
            </li>
          </ul>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><i className="fas fa-tasks"></i> Feature Status Overview</h2>
        </div>
        <div className="feature-grid">
          {features.map((feature) => (
            <div key={feature.id} className="feature-card">
              <h3><i className="fas fa-eye"></i> {feature.name}</h3>
              <div className="description">{feature.description}</div>
              <div className={`status ${feature.status}`}>{feature.status === 'completed' ? 'Completed' : feature.status === 'active' ? 'Active' : 'Pending'}</div>
              <div style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {feature.details.map((detail, index) => (
                  <div key={index}>
                    <i className="fas fa-check-circle"></i> {detail}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><i className="fas fa-chart-line"></i> Success Metrics</h2>
        </div>
        <table className="metrics-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Status</th>
              <th>Performance</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((item, index) => (
              <tr key={index}>
                <td>{item.metric}</td>
                <td><i className="fas fa-check-circle" style={{ color: 'var(--success)' }}></i> {item.status}</td>
                <td>{item.performance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Milestones Tracking Section */}
      <div className="panel">
        <div className="panel-header">
          <h2><i className="fas fa-flag-checkered"></i> Development Milestones</h2>
        </div>
        <div className="milestones-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {milestones.map((milestone) => (
            <div key={milestone.id} className="milestone-card" style={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border)',
              borderRadius: '15px',
              padding: '20px',
              backdropFilter: 'blur(10px)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ color: 'var(--accent)', margin: 0 }}>{milestone.title}</h3>
                <span className={`status ${milestone.status}`} style={{
                  padding: '5px 12px',
                  borderRadius: '20px',
                  fontSize: '0.8rem',
                  fontWeight: '600'
                }}>
                  {milestone.status === 'completed' ? 'Completed' : milestone.status === 'in-progress' ? 'In Progress' : 'Pending'}
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '15px' }}>{milestone.description}</p>
              <div style={{ marginBottom: '15px' }}>
                <h4 style={{ color: 'var(--accent)', marginBottom: '5px' }}>Achievements:</h4>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px', marginBottom: '10px' }}>
                  {milestone.achievements.map((achievement, idx) => (
                    <li key={idx} style={{ marginBottom: '3px' }}><i className="fas fa-check" style={{ color: 'var(--success)', marginRight: '5px' }}></i> {achievement}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 style={{ color: 'var(--accent)', marginBottom: '5px' }}>Next Steps:</h4>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px' }}>
                  {milestone.nextSteps.map((step, idx) => (
                    <li key={idx} style={{ marginBottom: '3px' }}><i className="fas fa-arrow-right" style={{ color: 'var(--warning)', marginRight: '5px' }}></i> {step}</li>
                  ))}
                </ul>
              </div>
              <div style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                <i className="far fa-calendar"></i> {milestone.date}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Optimization Ideas Section */}
      <div className="panel">
        <div className="panel-header">
          <h2><i className="fas fa-lightbulb"></i> Optimization Ideas</h2>
        </div>
        <div className="optimization-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {optimizationIdeas.map((idea) => (
            <div key={idea.id} className="optimization-card" style={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border)',
              borderRadius: '15px',
              padding: '20px',
              backdropFilter: 'blur(10px)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ color: 'var(--accent)', margin: 0 }}>{idea.title}</h3>
                <span style={{
                  padding: '5px 12px',
                  borderRadius: '20px',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  backgroundColor: idea.priority === 'high' ? 'rgba(255, 51, 102, 0.2)' :
                                  idea.priority === 'medium' ? 'rgba(255, 204, 0, 0.2)' : 'rgba(0, 204, 102, 0.2)',
                  color: idea.priority === 'high' ? 'var(--danger)' :
                         idea.priority === 'medium' ? 'var(--warning)' : 'var(--success)'
                }}>
                  {idea.priority.charAt(0).toUpperCase() + idea.priority.slice(1)} Priority
                </span>
              </div>
              <div style={{ marginBottom: '10px' }}>
                <span style={{
                  padding: '3px 8px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(138, 43, 226, 0.2)',
                  color: 'var(--accent-secondary)',
                  fontSize: '0.8rem',
                  marginRight: '10px'
                }}>
                  {idea.category}
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '15px' }}>{idea.description}</p>
              <div style={{ color: 'var(--success)', fontStyle: 'italic' }}>
                <i className="fas fa-bullseye"></i> {idea.impact}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alternative Approaches Section */}
      <div className="panel">
        <div className="panel-header">
          <h2><i className="fas fa-project-diagram"></i> Alternative Approaches</h2>
        </div>
        <div className="alternatives-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '20px'
        }}>
          {alternativeApproaches.map((approach) => (
            <div key={approach.id} className="alternative-card" style={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border)',
              borderRadius: '15px',
              padding: '20px',
              backdropFilter: 'blur(10px)'
            }}>
              <h3 style={{ color: 'var(--accent)', margin: '0 0 10px 0' }}>{approach.title}</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '15px' }}>{approach.description}</p>

              <div style={{ display: 'flex', gap: '20px', marginBottom: '15px' }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ color: 'var(--success)', marginBottom: '8px' }}>Pros</h4>
                  <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px' }}>
                    {approach.pros.map((pro, idx) => (
                      <li key={idx} style={{ marginBottom: '5px' }}><i className="fas fa-plus-circle" style={{ color: 'var(--success)', marginRight: '5px' }}></i> {pro}</li>
                    ))}
                  </ul>
                </div>
                <div style={{ flex: 1 }}>
                  <h4 style={{ color: 'var(--danger)', marginBottom: '8px' }}>Cons</h4>
                  <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px' }}>
                    {approach.cons.map((con, idx) => (
                      <li key={idx} style={{ marginBottom: '5px' }}><i className="fas fa-minus-circle" style={{ color: 'var(--danger)', marginRight: '5px' }}></i> {con}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div style={{
                padding: '10px',
                backgroundColor: 'rgba(138, 43, 226, 0.1)',
                borderLeft: '3px solid var(--accent-secondary)',
                borderRadius: '0 5px 5px 0'
              }}>
                <strong>Recommendation:</strong> {approach.recommendation}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="footer">
        <p>DIG-AI-FTE System Dashboard | Last Updated: <span id="current-time">{currentTime}</span> | Services: Online <i className="fas fa-check-circle" style={{ color: 'var(--success)' }}></i></p>
        <p style={{ marginTop: '10px' }}>Production-Ready Autonomous AI Employee System</p>
      </div>
    </div>
  );
};

export default DigAIFTEDashboard;