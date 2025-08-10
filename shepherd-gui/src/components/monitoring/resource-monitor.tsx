'use client'

import React, { memo, useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  Cpu, 
  HardDrive as Memory, 
  HardDrive, 
  Zap, 
  Activity, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Settings
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface ResourceData {
  timestamp: number
  cpu: number
  memory: number
  disk: number
  network: number
  tokens: number
  agents: number
}

export interface ResourceThresholds {
  cpu: { warning: number; critical: number }
  memory: { warning: number; critical: number }
  disk: { warning: number; critical: number }
  tokens: { warning: number; critical: number }
}

export interface ResourceMonitorProps {
  data: ResourceData[]
  currentData: ResourceData
  thresholds?: Partial<ResourceThresholds>
  updateInterval?: number
  onRefresh?: () => void
  onSettingsClick?: () => void
  className?: string
  compact?: boolean
  autoRefresh?: boolean
}

const DEFAULT_THRESHOLDS: ResourceThresholds = {
  cpu: { warning: 70, critical: 90 },
  memory: { warning: 80, critical: 95 },
  disk: { warning: 85, critical: 95 },
  tokens: { warning: 80, critical: 95 }
}

const ResourceMonitor = memo<ResourceMonitorProps>(({
  data,
  currentData,
  thresholds = {},
  updateInterval = 1000,
  onRefresh,
  onSettingsClick,
  className,
  compact = false,
  autoRefresh = true
}) => {
  const { theme, reducedMotion } = useUIStore(state => ({
    theme: state.theme,
    reducedMotion: state.reducedMotion
  }))

  const [selectedMetric, setSelectedMetric] = useState<'cpu' | 'memory' | 'disk' | 'tokens'>('cpu')
  const [timeRange, setTimeRange] = useState<'1m' | '5m' | '15m' | '1h'>('5m')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const mergedThresholds = useMemo(() => ({
    ...DEFAULT_THRESHOLDS,
    ...thresholds
  }), [thresholds])

  const formatValue = useCallback((value: number, type: 'cpu' | 'memory' | 'disk' | 'tokens' | 'network' | 'agents') => {
    switch (type) {
      case 'cpu':
      case 'disk':
        return `${value.toFixed(1)}%`
      case 'memory':
        if (value >= 1000) return `${(value / 1024).toFixed(1)}GB`
        return `${value.toFixed(0)}MB`
      case 'network':
        if (value >= 1000) return `${(value / 1000).toFixed(1)}MB/s`
        return `${value.toFixed(0)}KB/s`
      case 'tokens':
        if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
        return value.toString()
      case 'agents':
        return value.toString()
      default:
        return value.toString()
    }
  }, [])

  const getStatusColor = useCallback((value: number, thresholdConfig: { warning: number; critical: number }) => {
    if (value >= thresholdConfig.critical) return { color: 'text-red-500', bg: 'bg-red-100', border: 'border-red-200' }
    if (value >= thresholdConfig.warning) return { color: 'text-orange-500', bg: 'bg-orange-100', border: 'border-orange-200' }
    return { color: 'text-green-500', bg: 'bg-green-100', border: 'border-green-200' }
  }, [])

  const getStatusIcon = useCallback((value: number, thresholdConfig: { warning: number; critical: number }) => {
    if (value >= thresholdConfig.critical) return AlertTriangle
    if (value >= thresholdConfig.warning) return TrendingUp
    return CheckCircle
  }, [])

  const filteredData = useMemo(() => {
    const now = Date.now()
    const ranges = {
      '1m': 60 * 1000,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
      '1h': 60 * 60 * 1000
    }
    
    const cutoff = now - ranges[timeRange]
    return data.filter(d => d.timestamp >= cutoff).slice(-100) // Limit to 100 points for performance
  }, [data, timeRange])

  const handleRefresh = useCallback(async () => {
    if (isRefreshing || !onRefresh) return
    
    setIsRefreshing(true)
    try {
      await onRefresh()
    } catch (error) {
      console.error('Failed to refresh resource data:', error)
    } finally {
      setIsRefreshing(false)
    }
  }, [onRefresh, isRefreshing])

  // Auto-refresh logic
  useEffect(() => {
    if (!autoRefresh || !onRefresh) return

    const refresh = () => {
      if (!isRefreshing) {
        handleRefresh()
      }
      refreshTimeoutRef.current = setTimeout(refresh, updateInterval)
    }

    refreshTimeoutRef.current = setTimeout(refresh, updateInterval)

    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
      }
    }
  }, [autoRefresh, onRefresh, updateInterval, handleRefresh, isRefreshing])

  const resourceMetrics = [
    {
      key: 'cpu' as const,
      label: 'CPU Usage',
      icon: Cpu,
      value: currentData.cpu,
      threshold: mergedThresholds.cpu,
      color: '#3B82F6'
    },
    {
      key: 'memory' as const,
      label: 'Memory Usage',
      icon: Memory,
      value: currentData.memory,
      threshold: mergedThresholds.memory,
      color: '#10B981'
    },
    {
      key: 'disk' as const,
      label: 'Disk Usage',
      icon: HardDrive,
      value: currentData.disk,
      threshold: mergedThresholds.disk,
      color: '#F59E0B'
    },
    {
      key: 'tokens' as const,
      label: 'Token Usage',
      icon: Zap,
      value: currentData.tokens,
      threshold: mergedThresholds.tokens,
      color: '#8B5CF6'
    }
  ]

  const chartTheme = useMemo(() => ({
    background: theme === 'dark' ? '#1F2937' : '#FFFFFF',
    text: theme === 'dark' ? '#E5E7EB' : '#374151',
    grid: theme === 'dark' ? '#374151' : '#E5E7EB',
    tooltip: theme === 'dark' ? '#111827' : '#FFFFFF'
  }), [theme])

  if (compact) {
    return (
      <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-3', className)}>
        {resourceMetrics.map((metric) => {
          const status = getStatusColor(metric.value, metric.threshold)
          const StatusIcon = getStatusIcon(metric.value, metric.threshold)
          const IconComponent = metric.icon

          return (
            <div
              key={metric.key}
              className={cn(
                'p-3 rounded-lg border',
                'bg-white dark:bg-gray-800',
                status.border,
                !reducedMotion && 'transition-colors duration-200',
                'hover:shadow-md cursor-pointer'
              )}
              onClick={() => setSelectedMetric(metric.key)}
            >
              <div className="flex items-center justify-between mb-2">
                <IconComponent className={cn('w-5 h-5', status.color)} />
                <StatusIcon className={cn('w-4 h-4', status.color)} />
              </div>
              
              <div className="space-y-1">
                <div className={cn('text-lg font-semibold', status.color)}>
                  {formatValue(metric.value, metric.key)}
                </div>
                <div className="text-xs text-gray-500">
                  {metric.label}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className={cn('bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Resource Monitor
            </h3>
          </div>

          <div className="flex items-center gap-2">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className={cn(
                'px-3 py-1.5 text-sm border rounded-md',
                'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600',
                'focus:outline-none focus:ring-2 focus:ring-blue-500',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <option value="1m">1 minute</option>
              <option value="5m">5 minutes</option>
              <option value="15m">15 minutes</option>
              <option value="1h">1 hour</option>
            </select>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className={cn(
                'p-2 rounded-md border',
                'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600',
                'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <RefreshCw className={cn(
                'w-4 h-4',
                isRefreshing && !reducedMotion && 'animate-spin'
              )} />
            </button>

            {/* Settings Button */}
            {onSettingsClick && (
              <button
                onClick={onSettingsClick}
                className={cn(
                  'p-2 rounded-md border',
                  'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600',
                  'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <Settings className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Current Status Cards */}
      <div className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {resourceMetrics.map((metric) => {
            const status = getStatusColor(metric.value, metric.threshold)
            const StatusIcon = getStatusIcon(metric.value, metric.threshold)
            const IconComponent = metric.icon
            const isSelected = selectedMetric === metric.key

            return (
              <div
                key={metric.key}
                className={cn(
                  'p-4 rounded-lg border cursor-pointer',
                  isSelected
                    ? 'border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-950'
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
                  !reducedMotion && 'transition-all duration-200',
                  'hover:shadow-md'
                )}
                onClick={() => setSelectedMetric(metric.key)}
              >
                <div className="flex items-center justify-between mb-3">
                  <IconComponent className={cn(
                    'w-6 h-6',
                    isSelected ? 'text-blue-600 dark:text-blue-400' : status.color
                  )} />
                  <StatusIcon className={cn('w-5 h-5', status.color)} />
                </div>
                
                <div className="space-y-1">
                  <div className={cn(
                    'text-2xl font-bold',
                    isSelected ? 'text-blue-600 dark:text-blue-400' : status.color
                  )}>
                    {formatValue(metric.value, metric.key)}
                  </div>
                  <div className={cn(
                    'text-sm font-medium',
                    isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-600 dark:text-gray-400'
                  )}>
                    {metric.label}
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Warning: {metric.threshold.warning}%</span>
                    <span>Critical: {metric.threshold.critical}%</span>
                  </div>
                </div>

                {/* Mini Progress Bar */}
                <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={cn(
                      'h-2 rounded-full transition-all duration-300',
                      metric.value >= metric.threshold.critical
                        ? 'bg-red-500'
                        : metric.value >= metric.threshold.warning
                        ? 'bg-orange-500'
                        : 'bg-green-500'
                    )}
                    style={{ width: `${Math.min(metric.value, 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Chart */}
        <div className="h-64 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
                stroke={chartTheme.text}
                fontSize={12}
              />
              <YAxis
                domain={[0, selectedMetric === 'memory' ? 'auto' : 100]}
                tickFormatter={(value) => formatValue(value, selectedMetric)}
                stroke={chartTheme.text}
                fontSize={12}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: chartTheme.tooltip,
                  border: `1px solid ${chartTheme.grid}`,
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                formatter={(value: number) => [formatValue(value, selectedMetric), resourceMetrics.find(m => m.key === selectedMetric)?.label]}
              />
              <Area
                type="monotone"
                dataKey={selectedMetric}
                stroke={resourceMetrics.find(m => m.key === selectedMetric)?.color}
                fill={resourceMetrics.find(m => m.key === selectedMetric)?.color}
                fillOpacity={0.3}
                strokeWidth={2}
              />
              
              {/* Threshold Lines */}
              <Line
                type="monotone"
                dataKey={() => mergedThresholds[selectedMetric].warning}
                stroke="#F59E0B"
                strokeDasharray="5 5"
                strokeWidth={1}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey={() => mergedThresholds[selectedMetric].critical}
                stroke="#EF4444"
                strokeDasharray="5 5"
                strokeWidth={1}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Network Usage */}
          <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-purple-500" />
              <span className="font-medium text-gray-700 dark:text-gray-300">Network</span>
            </div>
            <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
              {formatValue(currentData.network, 'network')}
            </div>
          </div>

          {/* Active Agents */}
          <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-teal-500" />
              <span className="font-medium text-gray-700 dark:text-gray-300">Active Agents</span>
            </div>
            <div className="text-xl font-bold text-teal-600 dark:text-teal-400">
              {formatValue(currentData.agents, 'agents')}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
})

ResourceMonitor.displayName = 'ResourceMonitor'

export default ResourceMonitor