/**
 * Tests for Memory Flow components
 */

import { render, screen, fireEvent, waitFor } from '../../../setup'
import { MemoryFlowVisualizer, MemoryTransferItem, MemoryUsagePanel } from '@/components/features/memory/memory-flow'

// Mock WebSocket
const mockWebSocket = {
  onopen: jest.fn(),
  onmessage: jest.fn(),
  onclose: jest.fn(),
  onerror: jest.fn(),
  close: jest.fn(),
}

global.WebSocket = jest.fn(() => mockWebSocket) as any

// Mock data
const mockTransfer = {
  id: 'transfer-1',
  from: 'TaskAgent-001',
  to: 'SharedContext',
  type: 'discovery' as const,
  content: 'Found optimization pattern for data processing',
  timestamp: Date.now() - 30000,
  size: 1024,
  memoryTier: 'shared' as const
}

const mockUsage = {
  agentId: 'agent-1',
  agentName: 'TestAgent',
  local: {
    used: 128 * 1024,
    total: 512 * 1024,
    operations: 45
  },
  shared: {
    reads: 12,
    writes: 8,
    subscriptions: ['task_updates', 'system_events']
  },
  persistent: {
    patterns: 5,
    preferences: 3,
    failures: 2
  },
  vector: {
    searches: 15,
    similarities: 8,
    embeddings: 23
  }
}

describe('MemoryTransferItem', () => {
  test('renders transfer information correctly', () => {
    render(<MemoryTransferItem transfer={mockTransfer} />)
    
    expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
    expect(screen.getByText('SharedContext')).toBeInTheDocument()
    expect(screen.getByText('Found optimization pattern for data processing')).toBeInTheDocument()
    expect(screen.getByText('discovery')).toBeInTheDocument()
    expect(screen.getByText('shared')).toBeInTheDocument()
  })

  test('displays transfer size and timestamp', () => {
    render(<MemoryTransferItem transfer={mockTransfer} />)
    
    expect(screen.getByText('1.0 KB')).toBeInTheDocument()
    expect(screen.getByText(/ago/)).toBeInTheDocument()
  })

  test('handles click events', () => {
    const onClick = jest.fn()
    render(<MemoryTransferItem transfer={mockTransfer} onClick={onClick} />)
    
    const item = screen.getByRole('generic')
    fireEvent.click(item)
    
    expect(onClick).toHaveBeenCalled()
  })

  test('shows correct icon for transfer type', () => {
    render(<MemoryTransferItem transfer={mockTransfer} />)
    
    // Check that discovery type has appropriate styling
    const discoveryBadge = screen.getByText('discovery')
    expect(discoveryBadge).toHaveClass('text-xs')
  })
})

describe('MemoryFlowVisualizer', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders memory flow header', () => {
    render(<MemoryFlowVisualizer />)
    
    expect(screen.getByText('Memory Flow')).toBeInTheDocument()
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })

  test('shows pause/resume controls', () => {
    render(<MemoryFlowVisualizer />)
    
    const pauseButton = screen.getByRole('button', { name: /pause/i })
    expect(pauseButton).toBeInTheDocument()
    
    fireEvent.click(pauseButton)
    expect(screen.getByRole('button', { name: /resume/i })).toBeInTheDocument()
  })

  test('displays empty state when no transfers', () => {
    render(<MemoryFlowVisualizer />)
    
    // Before mock data loads
    expect(screen.getByText('No memory transfers yet')).toBeInTheDocument()
  })

  test('initializes WebSocket connection', () => {
    render(<MemoryFlowVisualizer />)
    
    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws')
  })

  test('handles WebSocket connection state', async () => {
    render(<MemoryFlowVisualizer />)
    
    // Simulate WebSocket open
    mockWebSocket.onopen()
    
    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument()
    })
  })

  test('processes WebSocket messages', async () => {
    render(<MemoryFlowVisualizer />)
    
    const mockMessage = {
      data: JSON.stringify({
        type: 'memory_transfer',
        transfer: mockTransfer
      })
    }
    
    // Simulate receiving a message
    mockWebSocket.onmessage(mockMessage)
    
    await waitFor(() => {
      expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
    })
  })
})

describe('MemoryUsagePanel', () => {
  test('renders agent memory usage', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    expect(screen.getByText('TestAgent')).toBeInTheDocument()
    expect(screen.getByText('128.0 KB / 512.0 KB')).toBeInTheDocument()
    expect(screen.getByText('45 ops')).toBeInTheDocument()
  })

  test('displays shared context information', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    expect(screen.getByText('12R / 8W')).toBeInTheDocument()
    expect(screen.getByText('2 subs')).toBeInTheDocument()
  })

  test('shows persistent memory stats', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    expect(screen.getByText('5 patterns')).toBeInTheDocument()
    expect(screen.getByText('3 prefs')).toBeInTheDocument()
  })

  test('displays vector memory operations', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    expect(screen.getByText('15 searches')).toBeInTheDocument()
    expect(screen.getByText('23 embeddings')).toBeInTheDocument()
  })

  test('expands detailed view on click', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    const agentCard = screen.getByText('TestAgent').closest('div')
    fireEvent.click(agentCard!)
    
    expect(screen.getByText('Shared Context Subscriptions')).toBeInTheDocument()
    expect(screen.getByText('task_updates')).toBeInTheDocument()
    expect(screen.getByText('system_events')).toBeInTheDocument()
  })

  test('calculates memory usage percentage', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    // 128KB / 512KB = 25%
    expect(screen.getByText('25% local')).toBeInTheDocument()
  })

  test('shows subscription details in expanded view', () => {
    render(<MemoryUsagePanel usages={[mockUsage]} />)
    
    // Click to expand
    const agentCard = screen.getByText('TestAgent').closest('div')
    fireEvent.click(agentCard!)
    
    expect(screen.getByText('Learned Patterns')).toBeInTheDocument()
    expect(screen.getByText('User Preferences')).toBeInTheDocument()
    expect(screen.getByText('Failure Patterns')).toBeInTheDocument()
  })
})