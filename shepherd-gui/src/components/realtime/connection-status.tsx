'use client'

import React, { useState, useEffect } from 'react'
import { 
  Wifi, 
  WifiOff, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Signal,
  Zap,
  Globe,
  Server,
  RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useWebSocket, UseWebSocketReturn } from '@/hooks/use-websocket'

export interface ConnectionStatusProps {
  compact?: boolean
  showLatency?: boolean
  showUptime?: boolean
  showRetry?: boolean
  className?: string
  onRetry?: () => void
}

export function ConnectionStatus({
  compact = false,
  showLatency = true,
  showUptime = true,
  showRetry = true,
  className,
  onRetry
}: ConnectionStatusProps) {
  const ws = useWebSocket()
  const [latency, setLatency] = useState<number>(0)
  const [isRetrying, setIsRetrying] = useState(false)

  // Ping for latency measurement
  useEffect(() => {
    if (!ws.isConnected) return

    const interval = setInterval(async () => {
      try {
        const pingLatency = await ws.ping()
        setLatency(pingLatency)
      } catch (error) {
        console.warn('Ping failed:', error)
      }
    }, 30000) // Ping every 30 seconds

    return () => clearInterval(interval)
  }, [ws.isConnected, ws])

  const handleRetry = async () => {
    if (isRetrying) return
    
    setIsRetrying(true)
    try {
      await ws.connect()
      onRetry?.()
    } catch (error) {
      console.error('Retry failed:', error)
    } finally {
      setIsRetrying(false)
    }
  }

  const getStatusIcon = () => {
    switch (ws.connectionState) {
      case 'connected':
        return <Wifi className="w-4 h-4 text-green-500" />
      case 'connecting':
      case 'reconnecting':
        return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />
      case 'disconnected':
        return <WifiOff className="w-4 h-4 text-gray-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <WifiOff className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = () => {
    switch (ws.connectionState) {
      case 'connected':
        return 'text-green-600 bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800'
      case 'connecting':
      case 'reconnecting':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800'
      case 'disconnected':
        return 'text-gray-600 bg-gray-50 border-gray-200 dark:bg-gray-900 dark:border-gray-700'
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200 dark:bg-gray-900 dark:border-gray-700'
    }
  }

  const getStatusText = () => {
    switch (ws.connectionState) {
      case 'connected':
        return 'Connected'
      case 'connecting':
        return 'Connecting...'
      case 'reconnecting':
        return `Reconnecting... (${ws.stats.reconnectAttempts})`
      case 'disconnected':
        return 'Disconnected'
      case 'error':
        return 'Connection Error'
      default:
        return 'Unknown'
    }
  }

  const formatUptime = (ms: number) => {
    if (ms < 1000) return '< 1s'
    if (ms < 60000) return `${Math.floor(ms / 1000)}s`
    if (ms < 3600000) return `${Math.floor(ms / 60000)}m`
    return `${Math.floor(ms / 3600000)}h ${Math.floor((ms % 3600000) / 60000)}m`
  }

  const getLatencyColor = (lat: number) => {
    if (lat < 100) return 'text-green-600'
    if (lat < 300) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (compact) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        {getStatusIcon()}
        <span className="text-sm font-medium">{getStatusText()}</span>
        {showLatency && ws.isConnected && latency > 0 && (
          <span className={cn('text-xs', getLatencyColor(latency))}>
            {latency}ms
          </span>
        )}
      </div>
    )
  }

  return (
    <div className={cn('p-4 border rounded-lg', getStatusColor(), className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <div className="font-medium text-sm">{getStatusText()}</div>
            <div className="text-xs opacity-75 mt-1">
              WebSocket Connection
            </div>
          </div>
        </div>

        {showRetry && ws.connectionState === 'disconnected' && (
          <button
            onClick={handleRetry}
            disabled={isRetrying}
            className={cn(
              'px-3 py-1.5 text-xs rounded-md border',
              'hover:bg-white/50 dark:hover:bg-black/10',
              isRetrying && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isRetrying ? 'Retrying...' : 'Retry'}
          </button>
        )}
      </div>

      {/* Statistics */}
      <div className="mt-3 grid grid-cols-2 gap-4 text-xs">
        {showLatency && (
          <div className="flex items-center gap-2">
            <Signal className="w-3 h-3" />
            <span>Latency:</span>
            <span className={cn('font-medium', getLatencyColor(latency))}>
              {latency > 0 ? `${latency}ms` : 'N/A'}
            </span>
          </div>
        )}

        {showUptime && ws.stats.connectedAt && (
          <div className="flex items-center gap-2">
            <Clock className="w-3 h-3" />
            <span>Uptime:</span>
            <span className="font-medium">
              {formatUptime(ws.stats.uptime)}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Zap className="w-3 h-3" />
          <span>Messages:</span>
          <span className="font-medium">
            ↓{ws.stats.messagesReceived} ↑{ws.stats.messagesSent}
          </span>
        </div>

        {ws.stats.reconnectAttempts > 0 && (
          <div className="flex items-center gap-2">
            <RefreshCw className="w-3 h-3" />
            <span>Reconnects:</span>
            <span className="font-medium">
              {ws.stats.reconnectAttempts}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

// Global Connection Status Bar
export function GlobalConnectionStatus() {
  const ws = useWebSocket()

  // Don't show when connected
  if (ws.connectionState === 'connected') {
    return null
  }

  return (
    <div className={cn(
      'fixed top-0 left-0 right-0 z-50 py-2 px-4 text-center text-sm font-medium',
      ws.connectionState === 'connecting' || ws.connectionState === 'reconnecting'
        ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
        : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
    )}>
      <div className="flex items-center justify-center gap-2">
        {ws.connectionState === 'connecting' || ws.connectionState === 'reconnecting' ? (
          <>
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>
              {ws.connectionState === 'reconnecting' 
                ? `Reconnecting to server... (attempt ${ws.stats.reconnectAttempts})`
                : 'Connecting to server...'
              }
            </span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            <span>Connection lost. Real-time features are unavailable.</span>
          </>
        )}
      </div>
    </div>
  )
}

// Network Status Monitor
export function NetworkStatusMonitor() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [networkType, setNetworkType] = useState<string>('')
  const ws = useWebSocket()

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Network Information API (experimental)
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      setNetworkType(connection?.effectiveType || '')
      
      const handleChange = () => {
        setNetworkType(connection?.effectiveType || '')
      }
      
      connection?.addEventListener('change', handleChange)
      
      return () => {
        window.removeEventListener('online', handleOnline)
        window.removeEventListener('offline', handleOffline)
        connection?.removeEventListener('change', handleChange)
      }
    }

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div className="text-xs text-gray-500 space-y-1">
      <div className="flex items-center gap-2">
        <Globe className="w-3 h-3" />
        <span>Network: {isOnline ? 'Online' : 'Offline'}</span>
        {networkType && <span>({networkType})</span>}
      </div>
      
      <div className="flex items-center gap-2">
        <Server className="w-3 h-3" />
        <span>WebSocket: {ws.connectionState}</span>
      </div>
    </div>
  )
}

// Connection Health Component
interface ConnectionHealthProps {
  showDetails?: boolean
  className?: string
}

export function ConnectionHealth({ showDetails = false, className }: ConnectionHealthProps) {
  const ws = useWebSocket()
  
  const getHealthScore = () => {
    let score = 0
    
    // Connection status (40 points)
    if (ws.connectionState === 'connected') score += 40
    else if (ws.connectionState === 'connecting' || ws.connectionState === 'reconnecting') score += 20
    
    // Latency (30 points)
    if (ws.stats.latency < 100) score += 30
    else if (ws.stats.latency < 300) score += 20
    else if (ws.stats.latency < 500) score += 10
    
    // Uptime (20 points)
    if (ws.stats.uptime > 300000) score += 20 // 5+ minutes
    else if (ws.stats.uptime > 60000) score += 15 // 1+ minute
    else if (ws.stats.uptime > 10000) score += 10 // 10+ seconds
    
    // Reconnection stability (10 points)
    if (ws.stats.reconnectAttempts === 0) score += 10
    else if (ws.stats.reconnectAttempts < 3) score += 5
    
    return Math.min(score, 100)
  }

  const healthScore = getHealthScore()
  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getHealthLabel = (score: number) => {
    if (score >= 90) return 'Excellent'
    if (score >= 80) return 'Good'
    if (score >= 60) return 'Fair'
    if (score >= 40) return 'Poor'
    return 'Critical'
  }

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2">
        <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Connection Health
        </div>
        <div className={cn('text-sm font-bold', getHealthColor(healthScore))}>
          {healthScore}% ({getHealthLabel(healthScore)})
        </div>
      </div>
      
      {/* Health Bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className={cn(
            'h-2 rounded-full transition-all duration-300',
            healthScore >= 80 ? 'bg-green-500' :
            healthScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
          )}
          style={{ width: `${healthScore}%` }}
        />
      </div>
      
      {showDetails && (
        <div className="text-xs text-gray-500 space-y-1">
          <div>Status: {ws.connectionState}</div>
          <div>Latency: {ws.stats.latency}ms</div>
          <div>Uptime: {Math.floor(ws.stats.uptime / 1000)}s</div>
          <div>Reconnects: {ws.stats.reconnectAttempts}</div>
          <div>Messages: ↓{ws.stats.messagesReceived} ↑{ws.stats.messagesSent}</div>
        </div>
      )}
    </div>
  )
}

// Offline Mode Handler
interface OfflineModeProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  showBanner?: boolean
}

export function OfflineMode({ children, fallback, showBanner = true }: OfflineModeProps) {
  const ws = useWebSocket()
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const isOffline = !isOnline || ws.connectionState === 'disconnected' || ws.connectionState === 'error'

  return (
    <>
      {showBanner && isOffline && (
        <div className="bg-gray-100 dark:bg-gray-800 border-l-4 border-l-gray-500 p-4 mb-4">
          <div className="flex items-center gap-2">
            <WifiOff className="w-5 h-5 text-gray-500" />
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                Offline Mode
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Real-time features are unavailable. Changes will sync when connection is restored.
              </div>
            </div>
          </div>
        </div>
      )}
      
      {isOffline && fallback ? fallback : children}
    </>
  )
}