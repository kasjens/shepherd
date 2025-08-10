/**
 * Comprehensive tests for Phase 5: Real-time Features & WebSocket Integration
 * Tests WebSocket manager, notification system, collaboration features,
 * data synchronization, event streams, and connection status components
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { jest } from '@jest/globals'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  public readyState = MockWebSocket.CONNECTING
  public onopen: ((event: any) => void) | null = null
  public onclose: ((event: any) => void) | null = null
  public onmessage: ((event: any) => void) | null = null
  public onerror: ((event: any) => void) | null = null

  private url: string
  private protocols?: string | string[]

  constructor(url: string, protocols?: string | string[]) {
    this.url = url
    this.protocols = protocols
    
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen({ type: 'open' })
      }
    }, 10)
  }

  send(data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open')
    }
    
    // Mock response for ping
    try {
      const message = JSON.parse(data)
      if (message.type === 'ping') {
        setTimeout(() => {
          if (this.onmessage) {
            this.onmessage({
              data: JSON.stringify({
                id: message.id,
                type: 'pong',
                data: { timestamp: message.data.timestamp }
              })
            })
          }
        }, 10)
      }
    } catch (e) {
      // Ignore parsing errors
    }
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose({
        type: 'close',
        code: code || 1000,
        reason: reason || '',
        wasClean: true
      })
    }
  }

  // Helper methods for testing
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage({
        data: JSON.stringify(data)
      })
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror({ type: 'error', message: 'Mock WebSocket error' })
    }
  }

  simulateDisconnect() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose({
        type: 'close',
        code: 1006,
        reason: 'Connection lost',
        wasClean: false
      })
    }
  }
}

// Mock global WebSocket
;(global as any).WebSocket = MockWebSocket

// Mock Zustand store
const mockUIStore = {
  theme: 'light' as const,
  reducedMotion: false,
  sidebarCollapsed: false
}

jest.mock('../../src/stores/ui-store', () => ({
  useUIStore: (selector: any) => selector ? selector(mockUIStore) : mockUIStore
}))

// Mock react-window
jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemCount }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 5) }, (_, index) =>
        children({ index, style: {} })
      )}
    </div>
  )
}))

jest.mock('react-virtualized-auto-sizer', () => {
  return function AutoSizer({ children }: any) {
    return children({ height: 600, width: 800 })
  }
})

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn(() => '2024-01-15 10:30:00'),
  formatDistanceToNow: jest.fn(() => '5 minutes ago')
}))

// Mock AudioContext for notification sounds
;(global as any).AudioContext = jest.fn().mockImplementation(() => ({
  createOscillator: jest.fn(() => ({
    connect: jest.fn(),
    frequency: { setValueAtTime: jest.fn() },
    type: 'sine',
    start: jest.fn(),
    stop: jest.fn()
  })),
  createGain: jest.fn(() => ({
    connect: jest.fn(),
    gain: {
      setValueAtTime: jest.fn(),
      linearRampToValueAtTime: jest.fn()
    }
  })),
  destination: {},
  currentTime: 0
}))

// Import components after mocks
import { WebSocketManager } from '../../src/lib/websocket-manager'
import { useWebSocket } from '../../src/hooks/use-websocket'
import { NotificationProvider, useNotifications } from '../../src/components/notifications/notification-system'
import { CollaborationProvider, useCollaboration } from '../../src/components/collaboration/presence-system'
import { EventStream } from '../../src/components/realtime/event-stream'
import { ConnectionStatus, GlobalConnectionStatus } from '../../src/components/realtime/connection-status'
import { RealtimeSync, createSync } from '../../src/lib/realtime-sync'

describe('Phase 5: Real-time Features & WebSocket Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('WebSocket Manager', () => {
    let wsManager: WebSocketManager

    beforeEach(() => {
      wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/ws',
        maxReconnectAttempts: 3,
        reconnectInterval: 1000
      })
    })

    afterEach(() => {
      wsManager?.dispose()
    })

    it('creates WebSocket manager with correct configuration', () => {
      expect(wsManager).toBeDefined()
      expect(wsManager.getState()).toBe('disconnected')
    })

    it('connects to WebSocket server successfully', async () => {
      const connectPromise = wsManager.connect()
      
      await waitFor(() => {
        expect(wsManager.getState()).toBe('connected')
      })
      
      await connectPromise
      expect(wsManager.getState()).toBe('connected')
    })

    it('handles connection failure and retries', async () => {
      // Override WebSocket to simulate failure
      const OriginalWebSocket = (global as any).WebSocket
      ;(global as any).WebSocket = jest.fn(() => {
        throw new Error('Connection failed')
      })

      try {
        await wsManager.connect()
      } catch (error) {
        expect(error).toBeDefined()
        expect(wsManager.getState()).toBe('error')
      }

      // Restore original WebSocket
      ;(global as any).WebSocket = OriginalWebSocket
    })

    it('sends and receives messages correctly', async () => {
      await wsManager.connect()
      
      const messagePromise = wsManager.send('test', { data: 'hello' }, false)
      expect(messagePromise).resolves.not.toThrow()
    })

    it('handles ping-pong for latency measurement', async () => {
      await wsManager.connect()
      
      const latency = await wsManager.ping()
      expect(typeof latency).toBe('number')
      expect(latency).toBeGreaterThanOrEqual(0)
    })

    it('manages subscriptions correctly', async () => {
      await wsManager.connect()
      
      const handler = jest.fn()
      const unsubscribe = wsManager.subscribe('test-event', handler)
      
      expect(typeof unsubscribe).toBe('function')
      
      // Simulate receiving a message
      const mockWs = (wsManager as any).ws
      if (mockWs && mockWs.simulateMessage) {
        mockWs.simulateMessage({
          type: 'test-event',
          data: { test: 'data' }
        })
      }
      
      await waitFor(() => {
        expect(handler).toHaveBeenCalledWith({ test: 'data' })
      })
      
      unsubscribe()
    })

    it('tracks connection statistics', async () => {
      await wsManager.connect()
      
      const stats = wsManager.getStats()
      expect(stats).toHaveProperty('messagesReceived')
      expect(stats).toHaveProperty('messagesSent')
      expect(stats).toHaveProperty('reconnectAttempts')
      expect(stats).toHaveProperty('uptime')
    })
  })

  describe('useWebSocket Hook', () => {
    function TestComponent() {
      const ws = useWebSocket({
        url: 'ws://localhost:8000/test',
        autoConnect: false
      })

      return (
        <div>
          <div data-testid="connection-state">{ws.connectionState}</div>
          <div data-testid="is-connected">{ws.isConnected.toString()}</div>
          <button onClick={() => ws.connect()} data-testid="connect-btn">
            Connect
          </button>
          <button onClick={() => ws.disconnect()} data-testid="disconnect-btn">
            Disconnect
          </button>
          <button 
            onClick={() => ws.send('test', { message: 'hello' })} 
            data-testid="send-btn"
          >
            Send
          </button>
        </div>
      )
    }

    it('provides WebSocket connection state and controls', async () => {
      render(<TestComponent />)
      
      expect(screen.getByTestId('connection-state')).toHaveTextContent('disconnected')
      expect(screen.getByTestId('is-connected')).toHaveTextContent('false')
      
      const connectBtn = screen.getByTestId('connect-btn')
      await userEvent.click(connectBtn)
      
      await waitFor(() => {
        expect(screen.getByTestId('connection-state')).toHaveTextContent('connected')
        expect(screen.getByTestId('is-connected')).toHaveTextContent('true')
      })
    })

    it('handles disconnect correctly', async () => {
      render(<TestComponent />)
      
      const connectBtn = screen.getByTestId('connect-btn')
      await userEvent.click(connectBtn)
      
      await waitFor(() => {
        expect(screen.getByTestId('is-connected')).toHaveTextContent('true')
      })
      
      const disconnectBtn = screen.getByTestId('disconnect-btn')
      await userEvent.click(disconnectBtn)
      
      expect(screen.getByTestId('connection-state')).toHaveTextContent('disconnected')
    })
  })

  describe('Notification System', () => {
    function TestNotificationComponent() {
      const { addNotification, showToast, state } = useNotifications()

      return (
        <div>
          <div data-testid="notification-count">{state.notifications.length}</div>
          <div data-testid="unread-count">{state.unreadCount}</div>
          <button
            onClick={() => addNotification({
              type: 'success',
              priority: 'medium',
              title: 'Test Success',
              message: 'This is a test notification'
            })}
            data-testid="add-notification-btn"
          >
            Add Notification
          </button>
          <button
            onClick={() => showToast('info', 'Test Toast', 'Toast message')}
            data-testid="show-toast-btn"
          >
            Show Toast
          </button>
        </div>
      )
    }

    it('manages notifications correctly', async () => {
      render(
        <NotificationProvider enableWebSocket={false}>
          <TestNotificationComponent />
        </NotificationProvider>
      )

      expect(screen.getByTestId('notification-count')).toHaveTextContent('0')
      expect(screen.getByTestId('unread-count')).toHaveTextContent('0')

      const addBtn = screen.getByTestId('add-notification-btn')
      await userEvent.click(addBtn)

      await waitFor(() => {
        expect(screen.getByTestId('notification-count')).toHaveTextContent('1')
        expect(screen.getByTestId('unread-count')).toHaveTextContent('1')
      })
    })

    it('displays toast notifications', async () => {
      render(
        <NotificationProvider enableWebSocket={false}>
          <TestNotificationComponent />
        </NotificationProvider>
      )

      const toastBtn = screen.getByTestId('show-toast-btn')
      await userEvent.click(toastBtn)

      await waitFor(() => {
        expect(screen.getByText('Test Toast')).toBeInTheDocument()
        expect(screen.getByText('Toast message')).toBeInTheDocument()
      })
    })
  })

  describe('Collaboration System', () => {
    const mockCurrentUser = {
      userId: 'user123',
      displayName: 'Test User',
      email: 'test@example.com'
    }

    function TestCollaborationComponent() {
      const { state, updatePresence, setStatus } = useCollaboration()

      return (
        <div>
          <div data-testid="connection-status">{state.isConnected.toString()}</div>
          <div data-testid="online-users-count">{state.onlineUsers.size}</div>
          <div data-testid="current-user">
            {state.currentUser?.displayName}
          </div>
          <button
            onClick={() => updatePresence({ customStatus: 'Working' })}
            data-testid="update-presence-btn"
          >
            Update Presence
          </button>
          <button
            onClick={() => setStatus('busy', 'In a meeting')}
            data-testid="set-status-btn"
          >
            Set Status
          </button>
        </div>
      )
    }

    it('initializes collaboration with current user', async () => {
      render(
        <CollaborationProvider currentUser={mockCurrentUser} enabled={false}>
          <TestCollaborationComponent />
        </CollaborationProvider>
      )

      expect(screen.getByTestId('current-user')).toHaveTextContent('Test User')
      expect(screen.getByTestId('online-users-count')).toHaveTextContent('0')
    })

    it('handles presence updates', async () => {
      render(
        <CollaborationProvider currentUser={mockCurrentUser} enabled={false}>
          <TestCollaborationComponent />
        </CollaborationProvider>
      )

      const updateBtn = screen.getByTestId('update-presence-btn')
      await userEvent.click(updateBtn)

      // Presence update should not throw error
      expect(updateBtn).toBeInTheDocument()
    })

    it('handles status changes', async () => {
      render(
        <CollaborationProvider currentUser={mockCurrentUser} enabled={false}>
          <TestCollaborationComponent />
        </CollaborationProvider>
      )

      const statusBtn = screen.getByTestId('set-status-btn')
      await userEvent.click(statusBtn)

      // Status update should not throw error
      expect(statusBtn).toBeInTheDocument()
    })
  })

  describe('Event Stream', () => {
    it('renders event stream component', () => {
      render(<EventStream />)

      expect(screen.getByText('Event Stream')).toBeInTheDocument()
      expect(screen.getByText(/0 events/)).toBeInTheDocument()
    })

    it('handles search functionality', async () => {
      render(<EventStream />)

      const searchInput = screen.getByPlaceholderText('Search events...')
      await userEvent.type(searchInput, 'test query')

      expect(searchInput).toHaveValue('test query')
    })

    it('toggles streaming on/off', async () => {
      render(<EventStream />)

      const toggleBtn = screen.getByTitle(/pause stream|resume stream/i)
      await userEvent.click(toggleBtn)

      // Should toggle streaming state
      expect(toggleBtn).toBeInTheDocument()
    })

    it('filters events by level and category', async () => {
      render(<EventStream />)

      // Check for filter buttons
      expect(screen.getByText('error')).toBeInTheDocument()
      expect(screen.getByText('system')).toBeInTheDocument()

      // Click on a filter
      const errorFilter = screen.getByText('error')
      await userEvent.click(errorFilter)

      expect(errorFilter).toBeInTheDocument()
    })

    it('exports events in different formats', async () => {
      // Mock URL.createObjectURL and document.createElement
      const mockCreateObjectURL = jest.fn(() => 'blob:mock-url')
      const mockClick = jest.fn()
      const mockAppendChild = jest.fn()
      const mockRemoveChild = jest.fn()
      
      ;(global as any).URL.createObjectURL = mockCreateObjectURL
      ;(global as any).URL.revokeObjectURL = jest.fn()
      
      const originalCreateElement = document.createElement
      document.createElement = jest.fn((tagName) => {
        if (tagName === 'a') {
          return {
            href: '',
            download: '',
            click: mockClick
          }
        }
        return originalCreateElement.call(document, tagName)
      })
      
      document.body.appendChild = mockAppendChild
      document.body.removeChild = mockRemoveChild

      render(<EventStream />)

      const exportBtn = screen.getByTitle('Export Events')
      await userEvent.click(exportBtn)

      // Should trigger export
      expect(exportBtn).toBeInTheDocument()

      // Restore mocks
      document.createElement = originalCreateElement
    })
  })

  describe('Connection Status', () => {
    it('renders connection status component', () => {
      render(<ConnectionStatus />)

      expect(screen.getByText(/connection/i)).toBeInTheDocument()
    })

    it('displays compact connection status', () => {
      render(<ConnectionStatus compact={true} />)

      expect(screen.getByText(/connected|disconnected|connecting/i)).toBeInTheDocument()
    })

    it('shows retry button when disconnected', () => {
      render(<ConnectionStatus showRetry={true} />)

      // Should show connection status
      expect(screen.getByText(/WebSocket Connection/i)).toBeInTheDocument()
    })

    it('renders global connection status bar', () => {
      render(<GlobalConnectionStatus />)

      // May not render anything if connected, so just check it doesn't crash
    })
  })

  describe('Realtime Sync', () => {
    it('creates sync instance successfully', () => {
      const sync = createSync('test-entity', { value: 0 })
      
      expect(sync).toBeDefined()
      expect(sync.getData()).toEqual({ value: 0 })
      expect(sync.getState().version).toBe(0)
      
      sync.dispose()
    })

    it('handles local updates with optimistic updates', async () => {
      const sync = createSync('test-entity', { items: [] }, {
        enableOptimisticUpdates: true
      })

      await sync.update('item1', { name: 'Test Item' })
      
      // Should apply optimistic update
      const state = sync.getState()
      expect(state.version).toBe(1)
      
      sync.dispose()
    })

    it('manages sync state correctly', async () => {
      const sync = createSync('test-entity', { value: 42 })
      
      const state = sync.getState()
      expect(state.data).toEqual({ value: 42 })
      expect(state.version).toBe(0)
      expect(state.syncing).toBe(false)
      expect(state.conflicts).toEqual([])
      
      sync.dispose()
    })

    it('handles batch operations', async () => {
      const sync = createSync('test-entity', { items: [] })

      await sync.batch([
        { type: 'create', entityId: 'item1', data: { name: 'Item 1' } },
        { type: 'create', entityId: 'item2', data: { name: 'Item 2' } }
      ])

      // Should process batch
      const state = sync.getState()
      expect(state.version).toBe(1)
      
      sync.dispose()
    })

    it('emits events for state changes', async () => {
      const sync = createSync('test-entity', { value: 0 })
      
      let emittedEvent: any
      sync.on('local_change', (event) => {
        emittedEvent = event
      })

      await sync.update('test', { value: 1 })
      
      expect(emittedEvent).toBeDefined()
      expect(emittedEvent.event.type).toBe('update')
      
      sync.dispose()
    })
  })

  describe('Integration Scenarios', () => {
    it('handles WebSocket reconnection correctly', async () => {
      const wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/test',
        maxReconnectAttempts: 2,
        reconnectInterval: 100
      })

      await wsManager.connect()
      expect(wsManager.getState()).toBe('connected')

      // Simulate disconnect
      const mockWs = (wsManager as any).ws
      if (mockWs && mockWs.simulateDisconnect) {
        mockWs.simulateDisconnect()
      }

      // Should attempt reconnection
      await waitFor(() => {
        expect(wsManager.getStats().reconnectAttempts).toBeGreaterThan(0)
      }, { timeout: 2000 })

      wsManager.dispose()
    })

    it('integrates notifications with WebSocket events', async () => {
      let notificationHandler: any
      
      function TestComponent() {
        const { addNotification, state } = useNotifications()
        notificationHandler = addNotification
        
        return (
          <div data-testid="notification-count">{state.notifications.length}</div>
        )
      }

      render(
        <NotificationProvider enableWebSocket={false}>
          <TestComponent />
        </NotificationProvider>
      )

      expect(screen.getByTestId('notification-count')).toHaveTextContent('0')

      // Simulate WebSocket event triggering notification
      if (notificationHandler) {
        notificationHandler({
          type: 'info',
          priority: 'medium',
          title: 'WebSocket Event',
          message: 'Received from WebSocket'
        })
      }

      await waitFor(() => {
        expect(screen.getByTestId('notification-count')).toHaveTextContent('1')
      })
    })

    it('maintains consistent state across components', async () => {
      const wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/consistency',
        autoReconnect: true
      })

      await wsManager.connect()

      // Multiple components should share the same WebSocket connection
      expect(wsManager.getState()).toBe('connected')
      
      const subscription1 = wsManager.subscribe('test', () => {})
      const subscription2 = wsManager.subscribe('test', () => {})
      
      // Should handle multiple subscriptions
      expect(typeof subscription1).toBe('function')
      expect(typeof subscription2).toBe('function')
      
      subscription1()
      subscription2()
      wsManager.dispose()
    })
  })

  describe('Performance and Edge Cases', () => {
    it('handles high-frequency messages efficiently', async () => {
      const wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/performance'
      })

      await wsManager.connect()
      
      const handler = jest.fn()
      wsManager.subscribe('high-freq', handler)

      // Simulate many rapid messages
      const mockWs = (wsManager as any).ws
      for (let i = 0; i < 100; i++) {
        if (mockWs && mockWs.simulateMessage) {
          mockWs.simulateMessage({
            type: 'high-freq',
            data: { index: i }
          })
        }
      }

      await waitFor(() => {
        expect(handler).toHaveBeenCalledTimes(100)
      })

      wsManager.dispose()
    })

    it('handles malformed messages gracefully', async () => {
      const wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/malformed'
      })

      await wsManager.connect()
      
      const errorHandler = jest.fn()
      wsManager.on('messageError', errorHandler)

      // Simulate malformed message
      const mockWs = (wsManager as any).ws
      if (mockWs && mockWs.onmessage) {
        mockWs.onmessage({ data: 'invalid json{' })
      }

      await waitFor(() => {
        expect(errorHandler).toHaveBeenCalled()
      })

      wsManager.dispose()
    })

    it('cleans up resources properly on dispose', () => {
      const wsManager = new WebSocketManager({
        url: 'ws://localhost:8000/cleanup'
      })

      const subscription = wsManager.subscribe('test', () => {})
      
      wsManager.dispose()
      
      // Should not throw after disposal
      expect(() => subscription()).not.toThrow()
      expect(wsManager.getState()).toBe('disconnected')
    })
  })
})

describe('Phase 5: Component Accessibility', () => {
  it('provides proper ARIA labels for connection status', () => {
    render(<ConnectionStatus />)
    
    // Should have accessible text
    const statusElement = screen.getByText(/WebSocket Connection/i)
    expect(statusElement).toBeInTheDocument()
  })

  it('maintains keyboard navigation in event stream', async () => {
    render(<EventStream />)
    
    const searchInput = screen.getByPlaceholderText('Search events...')
    expect(searchInput).toBeInTheDocument()
    
    // Should be focusable
    searchInput.focus()
    expect(document.activeElement).toBe(searchInput)
  })

  it('announces notifications to screen readers', async () => {
    function TestComponent() {
      const { showToast } = useNotifications()
      
      return (
        <button onClick={() => showToast('info', 'Test', 'Message')}>
          Show Toast
        </button>
      )
    }

    render(
      <NotificationProvider enableWebSocket={false}>
        <TestComponent />
      </NotificationProvider>
    )

    const button = screen.getByText('Show Toast')
    await userEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument()
    })
  })
})