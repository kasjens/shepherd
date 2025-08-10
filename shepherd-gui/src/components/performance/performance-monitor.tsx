'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { 
  Activity, 
  Cpu, 
  MemoryStick, 
  Zap, 
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Settings,
  Pause,
  Play,
  RotateCcw
} from 'lucide-react'
import { cn } from '@/lib/utils'

export interface PerformanceMetrics {
  timestamp: Date
  // Runtime Performance
  fps: number
  renderTime: number
  scriptTime: number
  layoutTime: number
  paintTime: number
  
  // Memory Usage
  jsHeapSizeLimit: number
  totalJSHeapSize: number
  usedJSHeapSize: number
  
  // DOM Performance
  domNodes: number
  domDepth: number
  eventListeners: number
  
  // Network Performance
  requestCount: number
  totalTransferSize: number
  totalEncodedSize: number
  
  // Custom Metrics
  componentRenders: number
  webSocketMessages: number
  storeUpdates: number
  chartRedraws: number
}

export interface PerformanceAlert {
  id: string
  type: 'warning' | 'error' | 'critical'
  metric: keyof PerformanceMetrics
  value: number
  threshold: number
  message: string
  timestamp: Date
  resolved: boolean
}

interface PerformanceMonitorProps {
  onAlert?: (alert: PerformanceAlert) => void
  maxDataPoints?: number
  updateInterval?: number
  className?: string
}

export function PerformanceMonitor({ 
  onAlert, 
  maxDataPoints = 100,
  updateInterval = 1000,
  className 
}: PerformanceMonitorProps) {
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([])
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([])
  const [isMonitoring, setIsMonitoring] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<keyof PerformanceMetrics>('fps')
  const [showOptimizations, setShowOptimizations] = useState(false)
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const performanceObserverRef = useRef<PerformanceObserver | null>(null)
  const customMetricsRef = useRef({
    componentRenders: 0,
    webSocketMessages: 0,
    storeUpdates: 0,
    chartRedraws: 0
  })

  // Performance thresholds
  const thresholds = {
    fps: { warning: 30, error: 20, critical: 15 },
    renderTime: { warning: 16.67, error: 33.33, critical: 50 },
    scriptTime: { warning: 50, error: 100, critical: 200 },
    usedJSHeapSize: { warning: 50 * 1024 * 1024, error: 100 * 1024 * 1024, critical: 200 * 1024 * 1024 },
    domNodes: { warning: 1500, error: 3000, critical: 5000 }
  }

  // Collect performance metrics
  const collectMetrics = useCallback((): PerformanceMetrics => {
    const now = performance.now()
    
    // Get memory info (if available)
    const memory = (performance as any).memory || {
      jsHeapSizeLimit: 0,
      totalJSHeapSize: 0,
      usedJSHeapSize: 0
    }
    
    // Calculate FPS from requestAnimationFrame
    let fps = 60 // Default assumption
    if ((window as any).lastFrameTime) {
      fps = Math.min(60, 1000 / (now - (window as any).lastFrameTime))
    }
    ;(window as any).lastFrameTime = now
    
    // Get DOM statistics
    const domNodes = document.getElementsByTagName('*').length
    const domDepth = getMaxDOMDepth(document.body)
    const eventListeners = getEventListenerCount()
    
    // Get navigation timing for render metrics
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const renderTime = navigation ? navigation.loadEventEnd - navigation.responseStart : 0
    
    return {
      timestamp: new Date(),
      fps,
      renderTime: renderTime || performance.now() - now,
      scriptTime: getScriptExecutionTime(),
      layoutTime: getLayoutTime(),
      paintTime: getPaintTime(),
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      totalJSHeapSize: memory.totalJSHeapSize,
      usedJSHeapSize: memory.usedJSHeapSize,
      domNodes,
      domDepth,
      eventListeners,
      requestCount: getNetworkRequestCount(),
      totalTransferSize: getTotalTransferSize(),
      totalEncodedSize: getTotalEncodedSize(),
      ...customMetricsRef.current
    }
  }, [])

  // Helper functions for metrics collection
  const getMaxDOMDepth = useCallback((element: Element, depth = 0): number => {
    let maxDepth = depth
    for (const child of element.children) {
      maxDepth = Math.max(maxDepth, getMaxDOMDepth(child, depth + 1))
    }
    return maxDepth
  }, [])

  const getEventListenerCount = useCallback((): number => {
    // Approximation - count elements with common event attributes
    const eventAttrs = ['onclick', 'onchange', 'onsubmit', 'onload']
    let count = 0
    eventAttrs.forEach(attr => {
      count += document.querySelectorAll(`[${attr}]`).length
    })
    return count
  }, [])

  const getScriptExecutionTime = useCallback((): number => {
    // Use performance API to get script timing
    const entries = performance.getEntriesByType('measure')
    return entries.reduce((total, entry) => total + entry.duration, 0)
  }, [])

  const getLayoutTime = useCallback((): number => {
    const entries = performance.getEntriesByName('layout')
    return entries.reduce((total, entry) => total + entry.duration, 0)
  }, [])

  const getPaintTime = useCallback((): number => {
    const paintEntries = performance.getEntriesByType('paint')
    const firstPaint = paintEntries.find(entry => entry.name === 'first-paint')
    return firstPaint ? firstPaint.startTime : 0
  }, [])

  const getNetworkRequestCount = useCallback((): number => {
    return performance.getEntriesByType('resource').length
  }, [])

  const getTotalTransferSize = useCallback((): number => {
    return performance.getEntriesByType('resource')
      .reduce((total, entry: any) => total + (entry.transferSize || 0), 0)
  }, [])

  const getTotalEncodedSize = useCallback((): number => {
    return performance.getEntriesByType('resource')
      .reduce((total, entry: any) => total + (entry.encodedBodySize || 0), 0)
  }, [])

  // Check for performance alerts
  const checkAlerts = useCallback((newMetrics: PerformanceMetrics) => {
    Object.entries(thresholds).forEach(([metricName, threshold]) => {
      const value = newMetrics[metricName as keyof PerformanceMetrics] as number
      let alertType: PerformanceAlert['type'] | null = null
      let thresholdValue = 0

      if (value >= threshold.critical) {
        alertType = 'critical'
        thresholdValue = threshold.critical
      } else if (value >= threshold.error) {
        alertType = 'error'
        thresholdValue = threshold.error
      } else if (value >= threshold.warning) {
        alertType = 'warning'
        thresholdValue = threshold.warning
      }

      if (alertType) {
        const alertId = `${metricName}_${Date.now()}`
        const alert: PerformanceAlert = {
          id: alertId,
          type: alertType,
          metric: metricName as keyof PerformanceMetrics,
          value,
          threshold: thresholdValue,
          message: generateAlertMessage(metricName as keyof PerformanceMetrics, alertType, value),
          timestamp: new Date(),
          resolved: false
        }

        setAlerts(prev => [alert, ...prev.slice(0, 49)]) // Keep last 50 alerts
        onAlert?.(alert)
      }
    })
  }, [onAlert])

  const generateAlertMessage = (metric: keyof PerformanceMetrics, type: PerformanceAlert['type'], value: number): string => {
    const messages = {
      fps: {
        warning: `Frame rate dropped to ${value.toFixed(1)} FPS`,
        error: `Low frame rate: ${value.toFixed(1)} FPS`,
        critical: `Critical frame rate: ${value.toFixed(1)} FPS`
      },
      renderTime: {
        warning: `Render time increased: ${value.toFixed(2)}ms`,
        error: `High render time: ${value.toFixed(2)}ms`,
        critical: `Critical render time: ${value.toFixed(2)}ms`
      },
      usedJSHeapSize: {
        warning: `Memory usage: ${(value / 1024 / 1024).toFixed(1)}MB`,
        error: `High memory usage: ${(value / 1024 / 1024).toFixed(1)}MB`,
        critical: `Critical memory usage: ${(value / 1024 / 1024).toFixed(1)}MB`
      },
      domNodes: {
        warning: `DOM complexity: ${value} nodes`,
        error: `High DOM complexity: ${value} nodes`,
        critical: `Critical DOM complexity: ${value} nodes`
      }
    }

    return (messages as any)[metric]?.[type] || `${metric} ${type}: ${value}`
  }

  // Start/stop monitoring
  const startMonitoring = useCallback(() => {
    if (intervalRef.current) return

    intervalRef.current = setInterval(() => {
      if (!isMonitoring) return

      const newMetrics = collectMetrics()
      setMetrics(prev => [newMetrics, ...prev.slice(0, maxDataPoints - 1)])
      checkAlerts(newMetrics)
    }, updateInterval)

    // Setup Performance Observer for long tasks
    if ('PerformanceObserver' in window) {
      performanceObserverRef.current = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) { // Long task threshold
            const alert: PerformanceAlert = {
              id: `long_task_${Date.now()}`,
              type: 'warning',
              metric: 'scriptTime',
              value: entry.duration,
              threshold: 50,
              message: `Long task detected: ${entry.duration.toFixed(2)}ms`,
              timestamp: new Date(),
              resolved: false
            }
            setAlerts(prev => [alert, ...prev])
            onAlert?.(alert)
          }
        }
      })

      try {
        performanceObserverRef.current.observe({ entryTypes: ['longtask'] })
      } catch (e) {
        console.warn('Long task observation not supported')
      }
    }
  }, [isMonitoring, collectMetrics, checkAlerts, maxDataPoints, updateInterval, onAlert])

  const stopMonitoring = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    if (performanceObserverRef.current) {
      performanceObserverRef.current.disconnect()
    }
  }, [])

  // Effects
  useEffect(() => {
    startMonitoring()
    return stopMonitoring
  }, [startMonitoring, stopMonitoring])

  useEffect(() => {
    if (isMonitoring) {
      startMonitoring()
    } else {
      stopMonitoring()
    }
  }, [isMonitoring, startMonitoring, stopMonitoring])

  // Custom metric tracking hooks for other components to use
  React.useEffect(() => {
    const updateCustomMetrics = (type: keyof typeof customMetricsRef.current) => {
      customMetricsRef.current[type]++
    }

    // Expose global functions for tracking
    ;(window as any).trackComponentRender = () => updateCustomMetrics('componentRenders')
    ;(window as any).trackWebSocketMessage = () => updateCustomMetrics('webSocketMessages')
    ;(window as any).trackStoreUpdate = () => updateCustomMetrics('storeUpdates')
    ;(window as any).trackChartRedraw = () => updateCustomMetrics('chartRedraws')

    return () => {
      delete (window as any).trackComponentRender
      delete (window as any).trackWebSocketMessage
      delete (window as any).trackStoreUpdate
      delete (window as any).trackChartRedraw
    }
  }, [])

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  const clearMetrics = useCallback(() => {
    setMetrics([])
    customMetricsRef.current = {
      componentRenders: 0,
      webSocketMessages: 0,
      storeUpdates: 0,
      chartRedraws: 0
    }
  }, [])

  const currentMetrics = metrics[0]
  const activeAlerts = alerts.filter(alert => !alert.resolved)

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-green-500" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Performance Monitor
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Real-time application performance metrics
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            className={cn(
              'flex items-center gap-2 px-3 py-1 text-sm rounded border',
              isMonitoring
                ? 'border-red-300 text-red-600 hover:bg-red-50'
                : 'border-green-300 text-green-600 hover:bg-green-50'
            )}
          >
            {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isMonitoring ? 'Pause' : 'Resume'}
          </button>

          <button
            onClick={clearMetrics}
            className="flex items-center gap-2 px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            <RotateCcw className="w-4 h-4" />
            Clear
          </button>

          <button
            onClick={() => setShowOptimizations(!showOptimizations)}
            className="px-3 py-1 text-sm border border-blue-300 text-blue-600 rounded hover:bg-blue-50"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Alert Summary */}
      {activeAlerts.length > 0 && (
        <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-red-800 dark:text-red-200">
              Performance Alerts ({activeAlerts.length})
            </h3>
            <button
              onClick={clearAlerts}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Clear All
            </button>
          </div>
          <div className="space-y-1">
            {activeAlerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className="flex items-center gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span>{alert.message}</span>
                <span className="text-red-400">
                  {alert.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))}
            {activeAlerts.length > 3 && (
              <div className="text-sm text-red-600">
                +{activeAlerts.length - 3} more alerts
              </div>
            )}
          </div>
        </div>
      )}

      {/* Key Metrics Cards */}
      {currentMetrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="FPS"
            value={currentMetrics.fps.toFixed(1)}
            unit=""
            icon={Zap}
            trend={getTrend(metrics.slice(0, 10).map(m => m.fps))}
            status={getMetricStatus('fps', currentMetrics.fps)}
            isSelected={selectedMetric === 'fps'}
            onClick={() => setSelectedMetric('fps')}
          />
          
          <MetricCard
            title="Memory"
            value={(currentMetrics.usedJSHeapSize / 1024 / 1024).toFixed(1)}
            unit="MB"
            icon={MemoryStick}
            trend={getTrend(metrics.slice(0, 10).map(m => m.usedJSHeapSize))}
            status={getMetricStatus('usedJSHeapSize', currentMetrics.usedJSHeapSize)}
            isSelected={selectedMetric === 'usedJSHeapSize'}
            onClick={() => setSelectedMetric('usedJSHeapSize')}
          />
          
          <MetricCard
            title="DOM Nodes"
            value={currentMetrics.domNodes.toString()}
            unit=""
            icon={Cpu}
            trend={getTrend(metrics.slice(0, 10).map(m => m.domNodes))}
            status={getMetricStatus('domNodes', currentMetrics.domNodes)}
            isSelected={selectedMetric === 'domNodes'}
            onClick={() => setSelectedMetric('domNodes')}
          />
          
          <MetricCard
            title="Render Time"
            value={currentMetrics.renderTime.toFixed(2)}
            unit="ms"
            icon={Clock}
            trend={getTrend(metrics.slice(0, 10).map(m => m.renderTime))}
            status={getMetricStatus('renderTime', currentMetrics.renderTime)}
            isSelected={selectedMetric === 'renderTime'}
            onClick={() => setSelectedMetric('renderTime')}
          />
        </div>
      )}

      {/* Performance Chart */}
      {metrics.length > 0 && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-900 dark:text-gray-100">
              {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)} Over Time
            </h3>
            <div className="text-sm text-gray-500">
              Last {Math.min(metrics.length, maxDataPoints)} data points
            </div>
          </div>
          
          <PerformanceChart
            data={metrics.slice(0, 50).reverse()}
            metric={selectedMetric}
            height={200}
          />
        </div>
      )}

      {/* Optimization Recommendations */}
      {showOptimizations && currentMetrics && (
        <OptimizationRecommendations
          metrics={currentMetrics}
          alerts={activeAlerts}
          onClose={() => setShowOptimizations(false)}
        />
      )}
    </div>
  )

  function getTrend(values: number[]): 'up' | 'down' | 'stable' {
    if (values.length < 2) return 'stable'
    const recent = values.slice(0, 3).reduce((a, b) => a + b, 0) / 3
    const older = values.slice(3, 6).reduce((a, b) => a + b, 0) / 3
    const diff = recent - older
    const threshold = Math.abs(older) * 0.1 // 10% threshold
    
    if (Math.abs(diff) < threshold) return 'stable'
    return diff > 0 ? 'up' : 'down'
  }

  function getMetricStatus(metric: keyof PerformanceMetrics, value: number): 'good' | 'warning' | 'error' {
    const threshold = (thresholds as any)[metric]
    if (!threshold) return 'good'
    
    if (value >= threshold.error) return 'error'
    if (value >= threshold.warning) return 'warning'
    return 'good'
  }
}

// Metric Card Component
interface MetricCardProps {
  title: string
  value: string
  unit: string
  icon: React.ComponentType<{ className?: string }>
  trend: 'up' | 'down' | 'stable'
  status: 'good' | 'warning' | 'error'
  isSelected: boolean
  onClick: () => void
}

function MetricCard({ title, value, unit, icon: Icon, trend, status, isSelected, onClick }: MetricCardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Activity
  
  return (
    <div
      onClick={onClick}
      className={cn(
        'p-4 border rounded-lg cursor-pointer transition-all',
        isSelected
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
          : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        <TrendIcon className={cn('w-4 h-4', {
          'text-red-500': trend === 'up' && (status === 'warning' || status === 'error'),
          'text-green-500': trend === 'down' && (status === 'warning' || status === 'error'),
          'text-gray-500': trend === 'stable'
        })} />
      </div>
      
      <div className="flex items-baseline gap-1 mb-1">
        <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {value}
        </span>
        <span className="text-sm text-gray-500">{unit}</span>
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600 dark:text-gray-400">{title}</span>
        <div className={cn('w-2 h-2 rounded-full', {
          'bg-green-500': status === 'good',
          'bg-yellow-500': status === 'warning',
          'bg-red-500': status === 'error'
        })} />
      </div>
    </div>
  )
}

// Simple Performance Chart Component
interface PerformanceChartProps {
  data: PerformanceMetrics[]
  metric: keyof PerformanceMetrics
  height: number
}

function PerformanceChart({ data, metric, height }: PerformanceChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || data.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Get values
    const values = data.map(d => d[metric] as number).filter(v => typeof v === 'number' && !isNaN(v))
    if (values.length === 0) return

    // Calculate bounds
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const valueRange = maxValue - minValue || 1

    const padding = 20
    const chartWidth = rect.width - padding * 2
    const chartHeight = height - padding * 2

    // Draw grid
    ctx.strokeStyle = '#E5E7EB'
    ctx.lineWidth = 1
    
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(rect.width - padding, y)
      ctx.stroke()
    }

    // Draw line
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.beginPath()

    values.forEach((value, index) => {
      const x = padding + (chartWidth / (values.length - 1)) * index
      const y = padding + chartHeight - ((value - minValue) / valueRange) * chartHeight

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    ctx.fillStyle = '#3B82F6'
    values.forEach((value, index) => {
      const x = padding + (chartWidth / (values.length - 1)) * index
      const y = padding + chartHeight - ((value - minValue) / valueRange) * chartHeight

      ctx.beginPath()
      ctx.arc(x, y, 2, 0, Math.PI * 2)
      ctx.fill()
    })

    // Draw labels
    ctx.fillStyle = '#6B7280'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'right'
    
    for (let i = 0; i <= 4; i++) {
      const value = minValue + (valueRange / 4) * (4 - i)
      const y = padding + (chartHeight / 4) * i + 3
      ctx.fillText(value.toFixed(1), padding - 5, y)
    }

  }, [data, metric, height])

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className="w-full"
        style={{ height }}
      />
    </div>
  )
}

// Optimization Recommendations Component
interface OptimizationRecommendationsProps {
  metrics: PerformanceMetrics
  alerts: PerformanceAlert[]
  onClose: () => void
}

function OptimizationRecommendations({ metrics, alerts, onClose }: OptimizationRecommendationsProps) {
  const recommendations = generateRecommendations(metrics, alerts)

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-medium text-gray-900 dark:text-gray-100">
          Performance Recommendations
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>
      
      <div className="p-4 space-y-3">
        {recommendations.length === 0 ? (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="w-4 h-4" />
            <span>No performance issues detected. Keep up the good work!</span>
          </div>
        ) : (
          recommendations.map((rec, index) => (
            <div key={index} className="flex gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">
                  {rec.title}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {rec.description}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )

  function generateRecommendations(metrics: PerformanceMetrics, alerts: PerformanceAlert[]) {
    const recs = []

    // FPS recommendations
    if (metrics.fps < 30) {
      recs.push({
        title: 'Optimize Rendering Performance',
        description: 'Consider using React.memo, useMemo, and useCallback to prevent unnecessary re-renders. Implement virtualization for large lists.'
      })
    }

    // Memory recommendations
    if (metrics.usedJSHeapSize > 50 * 1024 * 1024) {
      recs.push({
        title: 'Reduce Memory Usage',
        description: 'Clear unused data, implement proper cleanup in useEffect, and consider lazy loading for large components.'
      })
    }

    // DOM recommendations
    if (metrics.domNodes > 1500) {
      recs.push({
        title: 'Optimize DOM Structure',
        description: 'Reduce DOM complexity by removing unused elements, using CSS instead of DOM manipulation, and implementing virtualization.'
      })
    }

    // Network recommendations
    if (metrics.totalTransferSize > 1024 * 1024) {
      recs.push({
        title: 'Optimize Network Usage',
        description: 'Implement data compression, reduce payload sizes, and use caching strategies for API responses.'
      })
    }

    return recs
  }
}