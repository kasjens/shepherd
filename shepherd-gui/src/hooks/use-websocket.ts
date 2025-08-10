'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { WebSocketManager, WebSocketConnectionState, ConnectionStats, getWebSocketManager, createWebSocketManager } from '../lib/websocket-manager'

export interface UseWebSocketOptions {
  url?: string
  protocols?: string[]
  maxReconnectAttempts?: number
  reconnectInterval?: number
  autoConnect?: boolean
  onConnect?: () => void
  onDisconnect?: (event: any) => void
  onError?: (error: any) => void
  onMessage?: (message: any) => void
}

export interface UseWebSocketReturn {
  connectionState: WebSocketConnectionState
  isConnected: boolean
  stats: ConnectionStats
  connect: () => Promise<void>
  disconnect: () => void
  send: (type: string, data: any, expectResponse?: boolean) => Promise<any>
  subscribe: (type: string, handler: (data: any) => void) => () => void
  ping: () => Promise<number>
}

const DEFAULT_WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    url = DEFAULT_WS_URL,
    protocols,
    maxReconnectAttempts = 5,
    reconnectInterval = 3000,
    autoConnect = true,
    onConnect,
    onDisconnect,
    onError,
    onMessage
  } = options

  const [connectionState, setConnectionState] = useState<WebSocketConnectionState>('disconnected')
  const [stats, setStats] = useState<ConnectionStats>({
    reconnectAttempts: 0,
    messagesReceived: 0,
    messagesSent: 0,
    latency: 0,
    uptime: 0
  })

  const wsManagerRef = useRef<WebSocketManager | null>(null)
  const statsIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Initialize WebSocket manager
  useEffect(() => {
    let manager = getWebSocketManager()
    
    if (!manager) {
      manager = createWebSocketManager({
        url,
        protocols,
        maxReconnectAttempts,
        reconnectInterval,
        heartbeatInterval: 30000,
        messageTimeout: 10000,
        autoReconnect: true
      })
    }

    wsManagerRef.current = manager

    // Set up event listeners
    const handleStateChange = ({ current }: { current: WebSocketConnectionState }) => {
      setConnectionState(current)
    }

    const handleConnect = () => {
      onConnect?.()
    }

    const handleDisconnect = (event: any) => {
      onDisconnect?.(event)
    }

    const handleError = (error: any) => {
      onError?.(error)
    }

    const handleMessage = (message: any) => {
      onMessage?.(message)
    }

    manager.on('stateChange', handleStateChange)
    manager.on('connected', handleConnect)
    manager.on('disconnected', handleDisconnect)
    manager.on('error', handleError)
    manager.on('message', handleMessage)

    // Update stats periodically
    statsIntervalRef.current = setInterval(() => {
      if (wsManagerRef.current) {
        setStats(wsManagerRef.current.getStats())
      }
    }, 1000)

    // Auto-connect if enabled
    if (autoConnect) {
      manager.connect().catch(error => {
        console.error('Auto-connect failed:', error)
      })
    }

    return () => {
      manager?.off('stateChange', handleStateChange)
      manager?.off('connected', handleConnect)
      manager?.off('disconnected', handleDisconnect)
      manager?.off('error', handleError)
      manager?.off('message', handleMessage)

      if (statsIntervalRef.current) {
        clearInterval(statsIntervalRef.current)
      }
    }
  }, [url, protocols, maxReconnectAttempts, reconnectInterval, autoConnect, onConnect, onDisconnect, onError, onMessage])

  const connect = useCallback(async () => {
    if (wsManagerRef.current) {
      await wsManagerRef.current.connect()
    }
  }, [])

  const disconnect = useCallback(() => {
    if (wsManagerRef.current) {
      wsManagerRef.current.disconnect()
    }
  }, [])

  const send = useCallback(async (type: string, data: any, expectResponse: boolean = false) => {
    if (wsManagerRef.current) {
      return await wsManagerRef.current.send(type, data, expectResponse)
    }
    throw new Error('WebSocket manager not initialized')
  }, [])

  const subscribe = useCallback((type: string, handler: (data: any) => void) => {
    if (wsManagerRef.current) {
      return wsManagerRef.current.subscribe(type, handler)
    }
    return () => {} // No-op unsubscribe function
  }, [])

  const ping = useCallback(async () => {
    if (wsManagerRef.current) {
      return await wsManagerRef.current.ping()
    }
    throw new Error('WebSocket manager not initialized')
  }, [])

  return {
    connectionState,
    isConnected: connectionState === 'connected',
    stats,
    connect,
    disconnect,
    send,
    subscribe,
    ping
  }
}

// Specialized hooks for specific message types
export function useWebSocketSubscription<T = any>(
  messageType: string,
  handler: (data: T) => void,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const ws = useWebSocket(options)

  useEffect(() => {
    if (ws.isConnected) {
      const unsubscribe = ws.subscribe(messageType, handler)
      return unsubscribe
    }
  }, [ws, messageType, handler])

  return ws
}

// Hook for sending periodic messages (e.g., heartbeat, status updates)
export function useWebSocketInterval(
  messageType: string,
  getData: () => any,
  interval: number,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const ws = useWebSocket(options)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (ws.isConnected) {
      intervalRef.current = setInterval(() => {
        const data = getData()
        ws.send(messageType, data).catch(error => {
          console.error(`Failed to send ${messageType}:`, error)
        })
      }, interval)

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
      }
    }
  }, [ws, messageType, getData, interval])

  return ws
}

// Hook for managing presence/online status
export function usePresence(
  userId: string,
  userInfo: any = {},
  options: UseWebSocketOptions = {}
): UseWebSocketReturn & {
  onlineUsers: Map<string, any>
  updatePresence: (info: any) => void
} {
  const [onlineUsers, setOnlineUsers] = useState(new Map<string, any>())
  
  const ws = useWebSocket({
    ...options,
    onConnect: () => {
      // Send initial presence
      ws.send('presence:join', { userId, ...userInfo }).catch(console.error)
      options.onConnect?.()
    },
    onDisconnect: (event) => {
      // Clear online users on disconnect
      setOnlineUsers(new Map())
      options.onDisconnect?.(event)
    }
  })

  // Subscribe to presence updates
  useEffect(() => {
    if (ws.isConnected) {
      const unsubscribeJoin = ws.subscribe('presence:user_joined', (data) => {
        setOnlineUsers(prev => new Map(prev.set(data.userId, data)))
      })

      const unsubscribeLeave = ws.subscribe('presence:user_left', (data) => {
        setOnlineUsers(prev => {
          const next = new Map(prev)
          next.delete(data.userId)
          return next
        })
      })

      const unsubscribeUpdate = ws.subscribe('presence:user_updated', (data) => {
        setOnlineUsers(prev => new Map(prev.set(data.userId, data)))
      })

      const unsubscribeList = ws.subscribe('presence:user_list', (data) => {
        const userMap = new Map()
        data.users.forEach((user: any) => {
          userMap.set(user.userId, user)
        })
        setOnlineUsers(userMap)
      })

      return () => {
        unsubscribeJoin()
        unsubscribeLeave()
        unsubscribeUpdate()
        unsubscribeList()
      }
    }
  }, [ws])

  const updatePresence = useCallback((info: any) => {
    ws.send('presence:update', { userId, ...userInfo, ...info }).catch(console.error)
  }, [ws, userId, userInfo])

  // Send leave message on unmount
  useEffect(() => {
    return () => {
      if (ws.isConnected) {
        ws.send('presence:leave', { userId }).catch(console.error)
      }
    }
  }, [ws, userId])

  return {
    ...ws,
    onlineUsers,
    updatePresence
  }
}