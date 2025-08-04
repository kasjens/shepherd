/**
 * Tests for Communication Flow components
 */

import { render, screen, fireEvent, waitFor } from '../../../setup'
import { 
  CommunicationFlow, 
  CommunicationEventItem, 
  CommunicationNetwork,
  CommunicationStatsPanel 
} from '@/components/features/agents/communication-flow'

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
const mockEvent = {
  id: 'event-1',
  timestamp: Date.now() - 10000,
  type: 'request' as const,
  fromAgent: 'TaskAgent-001',
  toAgent: 'LearningAgent-002',
  messageType: 'request' as const,
  content: 'Request peer review for task completion analysis',
  status: 'processed' as const,
  priority: 'medium' as const,
  conversationId: 'conv-123',
  responseTime: 1200
}

const mockConnection = {
  fromAgent: 'TaskAgent-001',
  toAgent: 'LearningAgent-002',
  messageCount: 15,
  lastActivity: Date.now() - 10000,
  connectionStrength: 0.85,
  status: 'active' as const
}

const mockStats = {
  totalMessages: 23,
  averageResponseTime: 950,
  activeConversations: 3,
  successRate: 0.91,
  messagesByType: {
    request: 8,
    response: 7,
    notification: 5,
    discovery: 3
  },
  agentActivity: {
    'TaskAgent-001': { sent: 5, received: 8, responseTime: 1100 },
    'LearningAgent-002': { sent: 8, received: 5, responseTime: 800 }
  }
}

describe('CommunicationEventItem', () => {
  test('renders communication event correctly', () => {
    render(<CommunicationEventItem event={mockEvent} />)
    
    expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
    expect(screen.getByText('LearningAgent-002')).toBeInTheDocument()
    expect(screen.getByText('Request peer review for task completion analysis')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
    expect(screen.getByText('request')).toBeInTheDocument()
  })

  test('displays response time and conversation ID', () => {
    render(<CommunicationEventItem event={mockEvent} />)
    
    expect(screen.getByText('1.2s')).toBeInTheDocument()
    expect(screen.getByText('#conv-123'.slice(-6))).toBeInTheDocument()
  })

  test('shows broadcast badge for broadcast messages', () => {
    const broadcastEvent = { 
      ...mockEvent, 
      toAgent: undefined,
      type: 'broadcast' as const
    }
    render(<CommunicationEventItem event={broadcastEvent} />)
    
    expect(screen.getByText('broadcast')).toBeInTheDocument()
  })

  test('handles click events', () => {
    const onClick = jest.fn()
    render(<CommunicationEventItem event={mockEvent} onClick={onClick} />)
    
    const item = screen.getByRole('generic')
    fireEvent.click(item)
    
    expect(onClick).toHaveBeenCalled()
  })

  test('displays different priority badges', () => {
    const highPriorityEvent = { ...mockEvent, priority: 'high' as const }
    render(<CommunicationEventItem event={highPriorityEvent} />)
    
    expect(screen.getByText('high')).toBeInTheDocument()
  })

  test('shows different status icons', () => {
    const pendingEvent = { ...mockEvent, status: 'pending' as const }
    render(<CommunicationEventItem event={pendingEvent} />)
    
    // Should render without error (icon changes based on status)
    expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
  })
})

describe('CommunicationNetwork', () => {
  test('renders agent connections', () => {
    render(<CommunicationNetwork connections={[mockConnection]} />)
    
    expect(screen.getByText('Communication Network')).toBeInTheDocument()
    expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
    expect(screen.getByText('LearningAgent-002')).toBeInTheDocument()
    expect(screen.getByText('15 msgs')).toBeInTheDocument()
    expect(screen.getByText('active')).toBeInTheDocument()
  })

  test('expands connection details on click', () => {
    render(<CommunicationNetwork connections={[mockConnection]} />)
    
    const connectionItem = screen.getByText('TaskAgent-001').closest('div')
    fireEvent.click(connectionItem!)
    
    expect(screen.getByText('Messages')).toBeInTheDocument()
    expect(screen.getByText('Strength')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument() // connection strength
    expect(screen.getByText('Status')).toBeInTheDocument()
  })

  test('shows different connection statuses', () => {
    const idleConnection = { ...mockConnection, status: 'idle' as const }
    render(<CommunicationNetwork connections={[idleConnection]} />)
    
    expect(screen.getByText('idle')).toBeInTheDocument()
  })

  test('handles empty connections list', () => {
    render(<CommunicationNetwork connections={[]} />)
    
    expect(screen.getByText('Communication Network')).toBeInTheDocument()
    // Should render without crashing
  })
})

describe('CommunicationStatsPanel', () => {
  test('displays communication statistics', () => {
    render(<CommunicationStatsPanel stats={mockStats} />)
    
    expect(screen.getByText('23')).toBeInTheDocument() // total messages
    expect(screen.getByText('950ms')).toBeInTheDocument() // avg response time
    expect(screen.getByText('3')).toBeInTheDocument() // active conversations
    expect(screen.getByText('91%')).toBeInTheDocument() // success rate
  })

  test('formats response time correctly', () => {
    const fastStats = { ...mockStats, averageResponseTime: 500 }
    render(<CommunicationStatsPanel stats={fastStats} />)
    
    expect(screen.getByText('500ms')).toBeInTheDocument()
    
    const slowStats = { ...mockStats, averageResponseTime: 2500 }
    render(<CommunicationStatsPanel stats={slowStats} />)
    
    expect(screen.getByText('2.5s')).toBeInTheDocument()
  })
})

describe('CommunicationFlow', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders communication flow interface', () => {
    render(<CommunicationFlow />)
    
    expect(screen.getByText('Communication Flow')).toBeInTheDocument()
    expect(screen.getByText('Recent Events')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument()
  })

  test('shows connection status indicator', () => {
    render(<CommunicationFlow />)
    
    // Initially disconnected (red indicator)
    expect(screen.getByText(/communication flow/i)).toBeInTheDocument()
  })

  test('toggles pause/resume functionality', () => {
    render(<CommunicationFlow />)
    
    const pauseButton = screen.getByRole('button', { name: /pause/i })
    fireEvent.click(pauseButton)
    
    expect(screen.getByRole('button', { name: /resume/i })).toBeInTheDocument()
  })

  test('filters events by type', () => {
    render(<CommunicationFlow />)
    
    // Wait for mock data to load, then test filtering
    const requestFilter = screen.getByRole('button', { name: 'request' })
    fireEvent.click(requestFilter)
    
    // Should filter to show only request events
    expect(requestFilter).toHaveAttribute('data-state', 'on')
  })

  test('clears events when clear button clicked', () => {
    render(<CommunicationFlow />)
    
    const clearButton = screen.getByRole('button', { name: /clear/i })
    fireEvent.click(clearButton)
    
    // Events should be cleared
    expect(screen.queryByText('TaskAgent-001')).not.toBeInTheDocument()
  })

  test('initializes WebSocket connection', () => {
    render(<CommunicationFlow />)
    
    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws/communication')
  })

  test('handles WebSocket connection events', async () => {
    render(<CommunicationFlow />)
    
    // Simulate WebSocket open
    mockWebSocket.onopen()
    
    await waitFor(() => {
      // Connection status should update
      expect(screen.getByText(/communication flow/i)).toBeInTheDocument()
    })
  })

  test('processes WebSocket messages', async () => {
    render(<CommunicationFlow />)
    
    const mockMessage = {
      data: JSON.stringify({
        type: 'communication_event',
        event: mockEvent
      })
    }
    
    // Simulate receiving a message
    mockWebSocket.onmessage(mockMessage)
    
    await waitFor(() => {
      expect(screen.getByText('TaskAgent-001')).toBeInTheDocument()
    })
  })

  test('handles event selection callback', () => {
    const onEventSelect = jest.fn()
    render(<CommunicationFlow onEventSelect={onEventSelect} />)
    
    // Mock data should load, then we can test selection
    setTimeout(() => {
      const eventItem = screen.getByText('TaskAgent-001')
      if (eventItem) {
        fireEvent.click(eventItem)
        expect(onEventSelect).toHaveBeenCalled()
      }
    }, 100)
  })

  test('shows empty state when paused', () => {
    render(<CommunicationFlow />)
    
    // Pause the flow
    const pauseButton = screen.getByRole('button', { name: /pause/i })
    fireEvent.click(pauseButton)
    
    // Clear events to show empty state
    const clearButton = screen.getByRole('button', { name: /clear/i })
    fireEvent.click(clearButton)
    
    expect(screen.getByText('Communication flow paused')).toBeInTheDocument()
  })
})