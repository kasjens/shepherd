/**
 * Tests for Agent Status components
 */

import { render, screen, fireEvent } from '../../../setup'
import { AgentStatus, AgentStatusCard, AgentStatusPanel } from '@/components/features/agents/agent-status'

// Mock data
const mockAgent: AgentStatus = {
  id: 'agent-1',
  name: 'TestAgent',
  type: 'task',
  status: 'working',
  currentTask: 'Processing data analysis',
  progress: 75,
  performance: {
    tasksCompleted: 12,
    averageResponseTime: 1200,
    successRate: 0.92,
    efficiency: 0.85
  },
  resources: {
    cpuUsage: 45.2,
    memoryUsage: 128 * 1024 * 1024,
    memoryLimit: 512 * 1024 * 1024
  },
  connections: [
    {
      targetAgent: 'agent-2',
      strength: 0.8,
      lastActivity: Date.now() - 30000
    }
  ],
  tools: ['calculator', 'web_search'],
  capabilities: ['data_analysis', 'report_generation'],
  startTime: Date.now() - 3600000,
  lastActivity: Date.now() - 5000
}

const mockAgents: AgentStatus[] = [
  mockAgent,
  {
    ...mockAgent,
    id: 'agent-2',
    name: 'AnalysisAgent',
    type: 'system',
    status: 'idle',
    currentTask: undefined,
    progress: 0
  }
]

describe('AgentStatusCard', () => {
  test('renders agent information correctly', () => {
    render(<AgentStatusCard agent={mockAgent} />)
    
    expect(screen.getByText('TestAgent')).toBeInTheDocument()
    expect(screen.getByText('task')).toBeInTheDocument()
    expect(screen.getByText('working')).toBeInTheDocument()
    expect(screen.getByText('Processing data analysis')).toBeInTheDocument()
  })

  test('displays progress bar for working agent', () => {
    render(<AgentStatusCard agent={mockAgent} />)
    
    const progressText = screen.getByText('75%')
    expect(progressText).toBeInTheDocument()
  })

  test('shows idle status for non-working agent', () => {
    const idleAgent = { ...mockAgent, status: 'idle' as const, currentTask: undefined }
    render(<AgentStatusCard agent={idleAgent} />)
    
    expect(screen.getByText('idle')).toBeInTheDocument()
    expect(screen.getByText('Waiting for tasks')).toBeInTheDocument()
  })

  test('displays performance metrics', () => {
    render(<AgentStatusCard agent={mockAgent} />)
    
    expect(screen.getByText('12')).toBeInTheDocument() // tasks completed
    expect(screen.getByText('1.2s')).toBeInTheDocument() // response time
    expect(screen.getByText('92%')).toBeInTheDocument() // success rate
  })

  test('shows resource usage', () => {
    render(<AgentStatusCard agent={mockAgent} />)
    
    expect(screen.getByText('45.2%')).toBeInTheDocument() // CPU usage
    expect(screen.getByText('128.0 MB')).toBeInTheDocument() // memory usage
  })

  test('handles click events', () => {
    const onSelect = jest.fn()
    render(<AgentStatusCard agent={mockAgent} onSelect={onSelect} />)
    
    const card = screen.getByRole('button')
    fireEvent.click(card)
    
    expect(onSelect).toHaveBeenCalledWith('agent-1')
  })
})

describe('AgentStatusPanel', () => {
  test('renders multiple agents', () => {
    render(<AgentStatusPanel agents={mockAgents} />)
    
    expect(screen.getByText('TestAgent')).toBeInTheDocument()
    expect(screen.getByText('AnalysisAgent')).toBeInTheDocument()
  })

  test('filters agents by status', () => {
    render(<AgentStatusPanel agents={mockAgents} />)
    
    // Click on "idle" filter
    const idleFilter = screen.getByRole('button', { name: /idle/i })
    fireEvent.click(idleFilter)
    
    expect(screen.getByText('AnalysisAgent')).toBeInTheDocument()
    expect(screen.queryByText('TestAgent')).not.toBeInTheDocument()
  })

  test('filters agents by type', () => {
    render(<AgentStatusPanel agents={mockAgents} />)
    
    // Click on "system" filter
    const systemFilter = screen.getByRole('button', { name: /system/i })
    fireEvent.click(systemFilter)
    
    expect(screen.getByText('AnalysisAgent')).toBeInTheDocument()
    expect(screen.queryByText('TestAgent')).not.toBeInTheDocument()
  })

  test('shows empty state when no agents match filter', () => {
    const workingAgents = [mockAgent]
    render(<AgentStatusPanel agents={workingAgents} />)
    
    // Filter to idle agents (none exist)
    const idleFilter = screen.getByRole('button', { name: /idle/i })
    fireEvent.click(idleFilter)
    
    expect(screen.getByText('No agents found')).toBeInTheDocument()
  })

  test('displays agent count correctly', () => {
    render(<AgentStatusPanel agents={mockAgents} />)
    
    expect(screen.getByText('2 agents')).toBeInTheDocument()
  })
})

describe('AgentDetailView', () => {
  test('renders detailed agent information', () => {
    render(<AgentStatusCard agent={mockAgent} showDetails />)
    
    expect(screen.getByText('Tools')).toBeInTheDocument()
    expect(screen.getByText('calculator')).toBeInTheDocument()
    expect(screen.getByText('web_search')).toBeInTheDocument()
    
    expect(screen.getByText('Capabilities')).toBeInTheDocument()
    expect(screen.getByText('data_analysis')).toBeInTheDocument()
    expect(screen.getByText('report_generation')).toBeInTheDocument()
  })

  test('shows connection information', () => {
    render(<AgentStatusCard agent={mockAgent} showDetails />)
    
    expect(screen.getByText('Connections')).toBeInTheDocument()
    expect(screen.getByText('agent-2')).toBeInTheDocument()
    expect(screen.getByText('80%')).toBeInTheDocument() // connection strength
  })

  test('displays uptime', () => {
    render(<AgentStatusCard agent={mockAgent} showDetails />)
    
    expect(screen.getByText('Uptime')).toBeInTheDocument()
    expect(screen.getByText('1h 0m')).toBeInTheDocument()
  })

  test('shows memory usage details', () => {
    render(<AgentStatusCard agent={mockAgent} showDetails />)
    
    expect(screen.getByText('Memory')).toBeInTheDocument()
    expect(screen.getByText('128.0 MB / 512.0 MB')).toBeInTheDocument()
  })
})