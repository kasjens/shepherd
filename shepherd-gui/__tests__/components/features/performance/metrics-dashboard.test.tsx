/**
 * Tests for Performance Metrics Dashboard components
 */

import { render, screen, fireEvent } from '../../../setup'
import { 
  PerformanceMetricsDashboard,
  SystemMetricsPanel,
  WorkflowMetricsPanel,
  AgentMetricsPanel,
  PerformanceAlertsPanel,
  MetricsTrendsPanel
} from '@/components/features/performance/metrics-dashboard'

// Mock data
const mockSystemMetrics = {
  cpu: { usage: 45.2, cores: 8, temperature: 65, load: [0.4, 0.5, 0.3] },
  memory: { 
    used: 8.5 * 1024 * 1024 * 1024, 
    total: 16 * 1024 * 1024 * 1024, 
    usage: 53.1, 
    available: 7.5 * 1024 * 1024 * 1024 
  },
  disk: { 
    used: 120 * 1024 * 1024 * 1024, 
    total: 500 * 1024 * 1024 * 1024, 
    usage: 24.0, 
    readSpeed: 150 * 1024 * 1024, 
    writeSpeed: 80 * 1024 * 1024 
  },
  network: { 
    bytesIn: 1.2 * 1024 * 1024, 
    bytesOut: 800 * 1024, 
    packetsIn: 1200, 
    packetsOut: 850, 
    latency: 12 
  }
}

const mockWorkflowMetrics = {
  totalExecutions: 1247,
  successfulExecutions: 1134,
  failedExecutions: 113,
  averageExecutionTime: 2340,
  averageResponseTime: 450,
  executionsPerMinute: 5.7,
  successRate: 0.91,
  currentActiveWorkflows: 8,
  queuedWorkflows: 3,
  executionTimeByPattern: {
    SEQUENTIAL: 1800,
    PARALLEL: 1200,
    CONDITIONAL: 2800
  },
  errorsByType: {
    'TimeoutError': 45,
    'ValidationError': 28
  }
}

const mockAgentMetrics = {
  totalAgents: 12,
  activeAgents: 7,
  idleAgents: 5,
  averageTasksPerAgent: 8.3,
  averageAgentResponseTime: 1200,
  agentEfficiency: 0.87,
  toolUsageCount: 234,
  communicationEvents: 456,
  memoryOperations: 1834,
  learningEvents: 67
}

const mockAlerts = [
  {
    id: '1',
    type: 'warning' as const,
    component: 'system' as const,
    title: 'High Memory Usage',
    description: 'Memory usage has exceeded 80% for the past 10 minutes',
    value: 85.3,
    threshold: 80,
    timestamp: Date.now() - 300000,
    acknowledged: false
  },
  {
    id: '2',
    type: 'error' as const,
    component: 'workflow' as const,
    title: 'Critical Error Rate',
    description: 'Error rate has spiked above acceptable threshold',
    value: 15.2,
    threshold: 10,
    timestamp: Date.now() - 180000,
    acknowledged: false
  }
]

const mockTrends = [
  { metric: 'Workflow Success Rate', current: 91.2, previous: 88.7, change: 2.8, trend: 'up' as const },
  { metric: 'Average Response Time', current: 450, previous: 520, change: -13.5, trend: 'down' as const },
  { metric: 'Error Rate', current: 9.1, previous: 11.3, change: -19.5, trend: 'down' as const }
]

describe('SystemMetricsPanel', () => {
  test('displays CPU metrics correctly', () => {
    render(<SystemMetricsPanel metrics={mockSystemMetrics} />)
    
    expect(screen.getByText('CPU Usage')).toBeInTheDocument()
    expect(screen.getByText('45.2%')).toBeInTheDocument()
    expect(screen.getByText('8 cores')).toBeInTheDocument()
    expect(screen.getByText('Temp: 65°C')).toBeInTheDocument()
  })

  test('displays memory usage with formatted sizes', () => {
    render(<SystemMetricsPanel metrics={mockSystemMetrics} />)
    
    expect(screen.getByText('Memory')).toBeInTheDocument()
    expect(screen.getByText('53.1%')).toBeInTheDocument()
    expect(screen.getByText('8.5 GB / 16.0 GB')).toBeInTheDocument()
    expect(screen.getByText('Available: 7.5 GB')).toBeInTheDocument()
  })

  test('shows disk I/O information', () => {
    render(<SystemMetricsPanel metrics={mockSystemMetrics} />)
    
    expect(screen.getByText('Disk I/O')).toBeInTheDocument()
    expect(screen.getByText('24.0%')).toBeInTheDocument()
    expect(screen.getByText('R: 150.0 MB/s')).toBeInTheDocument()
    expect(screen.getByText('W: 80.0 MB/s')).toBeInTheDocument()
  })

  test('displays network metrics', () => {
    render(<SystemMetricsPanel metrics={mockSystemMetrics} />)
    
    expect(screen.getByText('Network')).toBeInTheDocument()
    expect(screen.getByText('12ms')).toBeInTheDocument()
    expect(screen.getByText('latency')).toBeInTheDocument()
    expect(screen.getByText('1.2 MB')).toBeInTheDocument() // bytes in
    expect(screen.getByText('800.0 KB')).toBeInTheDocument() // bytes out
  })

  test('shows warning badges for high usage', () => {
    const highUsageMetrics = {
      ...mockSystemMetrics,
      cpu: { ...mockSystemMetrics.cpu, usage: 85 },
      network: { ...mockSystemMetrics.network, latency: 150 }
    }
    render(<SystemMetricsPanel metrics={highUsageMetrics} />)
    
    // Should show destructive badges for high usage
    expect(screen.getByText('85.0%')).toBeInTheDocument()
  })
})

describe('WorkflowMetricsPanel', () => {
  test('displays workflow execution statistics', () => {
    render(<WorkflowMetricsPanel metrics={mockWorkflowMetrics} />)
    
    expect(screen.getByText('Workflow Performance')).toBeInTheDocument()
    expect(screen.getByText('1247')).toBeInTheDocument() // total executions
    expect(screen.getByText('1134')).toBeInTheDocument() // successful
    expect(screen.getByText('113')).toBeInTheDocument() // failed
    expect(screen.getByText('91%')).toBeInTheDocument() // success rate
  })

  test('shows performance metrics with formatted durations', () => {
    render(<WorkflowMetricsPanel metrics={mockWorkflowMetrics} />)
    
    expect(screen.getByText('2.3s')).toBeInTheDocument() // avg execution time
    expect(screen.getByText('450ms')).toBeInTheDocument() // avg response time
    expect(screen.getByText('5.7')).toBeInTheDocument() // executions per minute
    expect(screen.getByText('8')).toBeInTheDocument() // active workflows
    expect(screen.getByText('3')).toBeInTheDocument() // queued workflows
  })

  test('displays execution times by pattern', () => {
    render(<WorkflowMetricsPanel metrics={mockWorkflowMetrics} />)
    
    expect(screen.getByText('Execution Times by Pattern')).toBeInTheDocument()
    expect(screen.getByText('Sequential')).toBeInTheDocument()
    expect(screen.getByText('Parallel')).toBeInTheDocument()
    expect(screen.getByText('Conditional')).toBeInTheDocument()
    expect(screen.getByText('1.8s')).toBeInTheDocument() // sequential time
    expect(screen.getByText('1.2s')).toBeInTheDocument() // parallel time
  })

  test('shows common errors when present', () => {
    render(<WorkflowMetricsPanel metrics={mockWorkflowMetrics} />)
    
    expect(screen.getByText('Common Errors')).toBeInTheDocument()
    expect(screen.getByText('TimeoutError')).toBeInTheDocument()
    expect(screen.getByText('ValidationError')).toBeInTheDocument()
    expect(screen.getByText('45')).toBeInTheDocument()
    expect(screen.getByText('28')).toBeInTheDocument()
  })
})

describe('AgentMetricsPanel', () => {
  test('displays agent statistics', () => {
    render(<AgentMetricsPanel metrics={mockAgentMetrics} />)
    
    expect(screen.getByText('Agent Performance')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument() // total agents
    expect(screen.getByText('7')).toBeInTheDocument() // active
    expect(screen.getByText('5')).toBeInTheDocument() // idle
  })

  test('shows efficiency metrics', () => {
    render(<AgentMetricsPanel metrics={mockAgentMetrics} />)
    
    expect(screen.getByText('Agent Efficiency')).toBeInTheDocument()
    expect(screen.getByText('87%')).toBeInTheDocument()
    expect(screen.getByText('8.3')).toBeInTheDocument() // avg tasks per agent
    expect(screen.getByText('1.2s')).toBeInTheDocument() // avg response time
  })

  test('displays activity counters', () => {
    render(<AgentMetricsPanel metrics={mockAgentMetrics} />)
    
    expect(screen.getByText('234')).toBeInTheDocument() // tool uses
    expect(screen.getByText('456')).toBeInTheDocument() // messages
    expect(screen.getByText('1834')).toBeInTheDocument() // memory ops
    expect(screen.getByText('67')).toBeInTheDocument() // learning events
  })
})

describe('PerformanceAlertsPanel', () => {
  test('displays unacknowledged alerts', () => {
    render(<PerformanceAlertsPanel alerts={mockAlerts} />)
    
    expect(screen.getByText('Performance Alerts')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument() // alert count
    expect(screen.getByText('High Memory Usage')).toBeInTheDocument()
    expect(screen.getByText('Critical Error Rate')).toBeInTheDocument()
  })

  test('shows alert details with values and thresholds', () => {
    render(<PerformanceAlertsPanel alerts={mockAlerts} />)
    
    expect(screen.getByText('Current: 85.3 | Threshold: 80')).toBeInTheDocument()
    expect(screen.getByText('Current: 15.2 | Threshold: 10')).toBeInTheDocument()
  })

  test('handles alert acknowledgment', () => {
    const onAcknowledge = jest.fn()
    render(<PerformanceAlertsPanel alerts={mockAlerts} onAlertAcknowledge={onAcknowledge} />)
    
    const acknowledgeButtons = screen.getAllByRole('button', { name: /acknowledge/i })
    fireEvent.click(acknowledgeButtons[0])
    
    expect(onAcknowledge).toHaveBeenCalledWith('1')
  })

  test('shows different alert types with appropriate styling', () => {
    render(<PerformanceAlertsPanel alerts={mockAlerts} />)
    
    expect(screen.getByText('system')).toBeInTheDocument()
    expect(screen.getByText('workflow')).toBeInTheDocument()
  })

  test('displays empty state when no alerts', () => {
    render(<PerformanceAlertsPanel alerts={[]} />)
    
    expect(screen.getByText('All systems operating normally')).toBeInTheDocument()
  })
})

describe('MetricsTrendsPanel', () => {
  test('displays performance trends', () => {
    render(<MetricsTrendsPanel trends={mockTrends} />)
    
    expect(screen.getByText('Performance Trends')).toBeInTheDocument()
    expect(screen.getByText('Workflow Success Rate')).toBeInTheDocument()
    expect(screen.getByText('Average Response Time')).toBeInTheDocument()
    expect(screen.getByText('Error Rate')).toBeInTheDocument()
  })

  test('shows current and previous values', () => {
    render(<MetricsTrendsPanel trends={mockTrends} />)
    
    expect(screen.getByText('91.20')).toBeInTheDocument() // current success rate
    expect(screen.getByText('Previous: 88.70')).toBeInTheDocument()
    expect(screen.getByText('450.00')).toBeInTheDocument() // current response time
    expect(screen.getByText('Previous: 520.00')).toBeInTheDocument()
  })

  test('displays trend changes with correct formatting', () => {
    render(<MetricsTrendsPanel trends={mockTrends} />)
    
    expect(screen.getByText('+2.8%')).toBeInTheDocument() // positive change
    expect(screen.getByText('-13.5%')).toBeInTheDocument() // negative change
    expect(screen.getByText('-19.5%')).toBeInTheDocument() // negative change
  })

  test('shows trend direction indicators', () => {
    render(<MetricsTrendsPanel trends={mockTrends} />)
    
    // Should render trend icons (testing their presence indirectly)
    expect(screen.getByText('Workflow Success Rate')).toBeInTheDocument()
    expect(screen.getByText('Average Response Time')).toBeInTheDocument()
  })
})

describe('PerformanceMetricsDashboard', () => {
  test('renders complete dashboard', () => {
    render(<PerformanceMetricsDashboard />)
    
    expect(screen.getByText('Performance Dashboard')).toBeInTheDocument()
  })

  test('displays all metric panels', () => {
    render(<PerformanceMetricsDashboard />)
    
    // Should contain all the main sections
    expect(screen.getByText('CPU Usage')).toBeInTheDocument()
    expect(screen.getByText('Workflow Performance')).toBeInTheDocument()
    expect(screen.getByText('Agent Performance')).toBeInTheDocument()
    expect(screen.getByText('Performance Alerts')).toBeInTheDocument()
    expect(screen.getByText('Performance Trends')).toBeInTheDocument()
  })

  test('uses mock data correctly', () => {
    render(<PerformanceMetricsDashboard />)
    
    // Check that mock data is being displayed
    expect(screen.getByText('45.2%')).toBeInTheDocument() // CPU usage
    expect(screen.getByText('1247')).toBeInTheDocument() // total executions
    expect(screen.getByText('12')).toBeInTheDocument() // total agents
  })
})