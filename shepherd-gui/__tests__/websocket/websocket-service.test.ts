import { WebSocketService } from '@/lib/websocket-service'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  public readyState: number = MockWebSocket.CONNECTING
  public onopen: ((event: Event) => void) | null = null
  public onclose: ((event: CloseEvent) => void) | null = null
  public onmessage: ((event: MessageEvent) => void) | null = null
  public onerror: ((event: Event) => void) | null = null

  constructor(public url: string) {
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 10)
  }

  send(data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open')
    }
    // Mock successful send
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code: code || 1000, reason }))
    }
  }

  // Helper methods for testing
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { 
        data: JSON.stringify(data) 
      }))
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'))
    }
  }

  simulateClose(code = 1006) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code }))
    }
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket as any

// Mock React Query
jest.mock('@/lib/react-query', () => ({
  queryClient: {
    invalidateQueries: jest.fn(),
  },
  invalidateQueries: {
    conversation: jest.fn(),
    agents: jest.fn(),
    workflows: jest.fn(),
    analytics: jest.fn(),
  },
}))

// Mock performance utilities
jest.mock('@/lib/performance', () => ({
  debounce: (fn: Function, delay: number) => fn,
  throttle: (fn: Function, delay: number) => fn,
}))

describe('WebSocket Service', () => {
  let wsService: WebSocketService
  let mockWebSocket: MockWebSocket

  beforeEach(() => {
    wsService = new WebSocketService({
      url: 'ws://localhost:8000/ws',
      reconnectInterval: 100,
      maxReconnectAttempts: 3,
      heartbeatInterval: 1000,
      batchInterval: 50,
      maxBatchSize: 5,
    })

    // Clear all timers and mocks
    jest.clearAllTimers()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wsService.destroy()
  })

  describe('Connection Management', () => {
    test('connects successfully', async () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      wsService.connect()

      // Should start as connecting
      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ state: 'connecting' })
      )

      // Wait for connection
      await new Promise(resolve => setTimeout(resolve, 20))

      // Should be connected
      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ 
          state: 'connected',
          reconnectAttempts: 0,
          lastConnected: expect.any(Date)
        })
      )
    })

    test('handles connection failure', async () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      // Mock WebSocket constructor to throw
      global.WebSocket = jest.fn(() => {
        throw new Error('Connection failed')
      }) as any

      wsService.connect()

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ state: 'failed' })
      )
    })

    test('disconnects cleanly', async () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))

      wsService.disconnect()

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ 
          state: 'disconnected',
          reconnectAttempts: 0 
        })
      )
    })

    test('prevents multiple simultaneous connections', () => {
      const originalWebSocket = global.WebSocket
      const webSocketSpy = jest.fn().mockImplementation(() => new MockWebSocket('ws://test'))
      global.WebSocket = webSocketSpy as any

      wsService.connect()
      wsService.connect()
      wsService.connect()

      // Should only create one WebSocket instance
      expect(webSocketSpy).toHaveBeenCalledTimes(1)

      global.WebSocket = originalWebSocket
    })
  })

  describe('Message Handling', () => {
    beforeEach(async () => {
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))
      mockWebSocket = (wsService as any).ws as MockWebSocket
    })

    test('sends single messages', () => {
      const sendSpy = jest.spyOn(mockWebSocket, 'send')

      wsService.send({
        type: 'test_message',
        payload: { data: 'test' },
        timestamp: Date.now()
      })

      expect(sendSpy).toHaveBeenCalledWith(
        expect.stringContaining('"type":"test_message"')
      )
    })

    test('batches multiple messages', async () => {
      const sendSpy = jest.spyOn(mockWebSocket, 'send')

      // Send multiple messages quickly
      for (let i = 0; i < 3; i++) {
        wsService.send({
          type: 'batch_test',
          payload: { index: i },
          timestamp: Date.now()
        })
      }

      // Wait for batch timeout
      await new Promise(resolve => setTimeout(resolve, 60))

      expect(sendSpy).toHaveBeenCalledWith(
        expect.stringContaining('"type":"batch"')
      )
    })

    test('flushes batch when reaching max size', () => {
      const sendSpy = jest.spyOn(mockWebSocket, 'send')

      // Send max batch size messages
      for (let i = 0; i < 5; i++) {
        wsService.send({
          type: 'max_batch_test',
          payload: { index: i },
          timestamp: Date.now()
        })
      }

      // Should send immediately when reaching max batch size
      expect(sendSpy).toHaveBeenCalledWith(
        expect.stringContaining('"type":"batch"')
      )
    })

    test('queues messages when disconnected', () => {
      wsService.disconnect()

      wsService.send({
        type: 'queued_message',
        payload: { data: 'queued' },
        timestamp: Date.now()
      })

      // Message should be queued
      expect((wsService as any).messageQueue).toHaveLength(1)
    })

    test('flushes queued messages on reconnection', async () => {
      wsService.disconnect()

      // Queue some messages
      wsService.send({ type: 'queued1', payload: {}, timestamp: Date.now() })
      wsService.send({ type: 'queued2', payload: {}, timestamp: Date.now() })

      expect((wsService as any).messageQueue).toHaveLength(2)

      // Reconnect
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))

      // Messages should be sent
      expect((wsService as any).messageQueue).toHaveLength(0)
    })

    test('routes messages to handlers', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()

      wsService.on('test_type', handler1)
      wsService.on('other_type', handler2)

      mockWebSocket.simulateMessage({
        type: 'test_type',
        payload: { data: 'test' },
        timestamp: Date.now()
      })

      expect(handler1).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'test_type',
          payload: { data: 'test' }
        })
      )
      expect(handler2).not.toHaveBeenCalled()
    })

    test('handles batch messages', () => {
      const handler = jest.fn()
      wsService.on('batch_item', handler)

      mockWebSocket.simulateMessage({
        type: 'batch',
        payload: [
          { type: 'batch_item', payload: { id: 1 } },
          { type: 'batch_item', payload: { id: 2 } },
          { type: 'other_type', payload: { id: 3 } }
        ],
        timestamp: Date.now()
      })

      expect(handler).toHaveBeenCalledTimes(2)
      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ payload: { id: 1 } })
      )
      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ payload: { id: 2 } })
      )
    })

    test('unsubscribes handlers correctly', () => {
      const handler = jest.fn()
      const unsubscribe = wsService.on('test_unsubscribe', handler)

      mockWebSocket.simulateMessage({
        type: 'test_unsubscribe',
        payload: {},
        timestamp: Date.now()
      })

      expect(handler).toHaveBeenCalledTimes(1)

      unsubscribe()

      mockWebSocket.simulateMessage({
        type: 'test_unsubscribe',
        payload: {},
        timestamp: Date.now()
      })

      expect(handler).toHaveBeenCalledTimes(1) // Still only called once
    })
  })

  describe('Reconnection Logic', () => {
    beforeEach(async () => {
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))
      mockWebSocket = (wsService as any).ws as MockWebSocket
    })

    test('reconnects after unexpected close', async () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      // Simulate unexpected close
      mockWebSocket.simulateClose(1006)

      await new Promise(resolve => setTimeout(resolve, 50))

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ state: 'disconnected' })
      )

      // Wait for reconnection attempt
      await new Promise(resolve => setTimeout(resolve, 150))

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ 
          state: 'reconnecting',
          reconnectAttempts: 1
        })
      )
    })

    test('stops reconnecting after max attempts', async () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      // Mock WebSocket to always fail
      global.WebSocket = jest.fn(() => {
        const mock = new MockWebSocket('ws://test')
        setTimeout(() => mock.simulateClose(1006), 1)
        return mock
      }) as any

      // Trigger initial failure
      mockWebSocket.simulateClose(1006)

      // Wait for all reconnection attempts
      await new Promise(resolve => setTimeout(resolve, 1000))

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ state: 'failed' })
      )
    })

    test('does not reconnect on normal close', () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      // Simulate normal close (code 1000)
      mockWebSocket.simulateClose(1000)

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ state: 'disconnected' })
      )

      // Should not attempt reconnection
      expect(statusHandler).not.toHaveBeenCalledWith(
        expect.objectContaining({ state: 'reconnecting' })
      )
    })
  })

  describe('Heartbeat System', () => {
    beforeEach(async () => {
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))
      mockWebSocket = (wsService as any).ws as MockWebSocket
    })

    test('sends periodic heartbeats', async () => {
      const sendSpy = jest.spyOn(mockWebSocket, 'send')
      
      // Enable fake timers for heartbeat testing
      jest.useFakeTimers()

      // Fast-forward past heartbeat interval
      jest.advanceTimersByTime(1000)

      expect(sendSpy).toHaveBeenCalledWith(
        expect.stringContaining('"type":"heartbeat"')
      )

      jest.useRealTimers()
    })

    test('calculates latency from heartbeat response', () => {
      const statusHandler = jest.fn()
      wsService.onStatus(statusHandler)

      // Mock performance.now for consistent timing
      const performanceSpy = jest.spyOn(performance, 'now')
        .mockReturnValueOnce(1000)
        .mockReturnValueOnce(1050)

      // Simulate sending heartbeat and receiving response
      ;(wsService as any).lastHeartbeat = 1000

      mockWebSocket.simulateMessage({
        type: 'heartbeat_response',
        payload: { timestamp: Date.now() },
        timestamp: Date.now()
      })

      expect(statusHandler).toHaveBeenCalledWith(
        expect.objectContaining({ latency: 50 })
      )

      performanceSpy.mockRestore()
    })
  })

  describe('Cache Integration', () => {
    beforeEach(async () => {
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))
      mockWebSocket = (wsService as any).ws as MockWebSocket
    })

    test('invalidates cache on conversation updates', () => {
      const { invalidateQueries } = require('@/lib/react-query')

      mockWebSocket.simulateMessage({
        type: 'conversation_updated',
        payload: { id: 'conv1' },
        timestamp: Date.now()
      })

      expect(invalidateQueries.conversation).toHaveBeenCalledWith('conv1')
    })

    test('invalidates cache on agent status changes', () => {
      const { invalidateQueries } = require('@/lib/react-query')

      mockWebSocket.simulateMessage({
        type: 'agent_status_changed',
        payload: { agentId: 'agent1', status: 'active' },
        timestamp: Date.now()
      })

      expect(invalidateQueries.agents).toHaveBeenCalled()
    })

    test('handles cache invalidation commands', () => {
      const { queryClient } = require('@/lib/react-query')

      mockWebSocket.simulateMessage({
        type: 'invalidate_cache',
        payload: { queryKey: ['conversations', 'list'] },
        timestamp: Date.now()
      })

      expect(queryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['conversations', 'list']
      })
    })
  })

  describe('Error Handling', () => {
    test('handles message parsing errors gracefully', () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()

      wsService.connect()

      // Simulate invalid JSON message
      const mockWS = (wsService as any).ws as MockWebSocket
      if (mockWS.onmessage) {
        mockWS.onmessage(new MessageEvent('message', { data: 'invalid json' }))
      }

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to parse WebSocket message:',
        expect.any(Error)
      )

      consoleErrorSpy.mockRestore()
    })

    test('handles handler errors gracefully', () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()
      
      const faultyHandler = jest.fn().mockImplementation(() => {
        throw new Error('Handler error')
      })

      wsService.on('error_test', faultyHandler)

      const mockWS = (wsService as any).ws as MockWebSocket
      mockWS.simulateMessage({
        type: 'error_test',
        payload: {},
        timestamp: Date.now()
      })

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error in WebSocket message handler for error_test:',
        expect.any(Error)
      )

      consoleErrorSpy.mockRestore()
    })
  })

  describe('Status and Utilities', () => {
    test('reports connection status correctly', () => {
      expect(wsService.isConnected()).toBe(false)
      expect(wsService.getStatus().state).toBe('disconnected')

      wsService.connect()
      expect(wsService.getStatus().state).toBe('connecting')
    })

    test('provides latency information', async () => {
      wsService.connect()
      await new Promise(resolve => setTimeout(resolve, 20))

      const status = wsService.getStatus()
      expect(wsService.getLatency()).toBe(status.latency || 0)
    })

    test('generates unique message IDs', () => {
      const id1 = (wsService as any).generateMessageId()
      const id2 = (wsService as any).generateMessageId()

      expect(id1).not.toBe(id2)
      expect(id1).toMatch(/^msg_\d+_[a-z0-9]+$/)
    })
  })

  describe('Cleanup', () => {
    test('cleans up resources on destroy', () => {
      const statusHandler = jest.fn()
      const messageHandler = jest.fn()

      wsService.onStatus(statusHandler)
      wsService.on('test', messageHandler)

      wsService.destroy()

      expect(wsService.isConnected()).toBe(false)
      expect((wsService as any).messageHandlers.size).toBe(0)
      expect((wsService as any).statusHandlers.size).toBe(0)
      expect((wsService as any).messageQueue).toHaveLength(0)
    })

    test('clears all timers on cleanup', () => {
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout')
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval')

      wsService.connect()
      wsService.destroy()

      expect(clearTimeoutSpy).toHaveBeenCalled()
      expect(clearIntervalSpy).toHaveBeenCalled()

      clearTimeoutSpy.mockRestore()
      clearIntervalSpy.mockRestore()
    })
  })
})