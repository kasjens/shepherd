'use client'

import React, { memo, useMemo } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts'
import { format } from 'date-fns'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  MessageCircle,
  Clock,
  Zap,
  AlertTriangle,
  CheckCircle,
  Minus
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface WidgetData {
  id: string
  title: string
  type: 'metric' | 'chart' | 'table' | 'gauge' | 'heatmap' | 'timeline' | 'status' | 'progress' | 'list'
  data: any
  config?: Record<string, any>
}

interface BaseWidgetProps {
  widget: WidgetData
  className?: string
}

// Metric Widget - Single value with trend
export const MetricWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { theme } = useUIStore(state => ({ theme: state.theme }))
  const { value, previousValue, label, trend, color = 'blue', icon: IconName } = widget.data

  const trendDirection = useMemo(() => {
    if (!previousValue) return 'neutral'
    return value > previousValue ? 'up' : value < previousValue ? 'down' : 'neutral'
  }, [value, previousValue])

  const trendPercentage = useMemo(() => {
    if (!previousValue || previousValue === 0) return 0
    return ((value - previousValue) / previousValue) * 100
  }, [value, previousValue])

  const TrendIcon = trendDirection === 'up' ? TrendingUp : trendDirection === 'down' ? TrendingDown : Minus
  const IconComponent = IconName === 'Users' ? Users : 
                       IconName === 'Activity' ? Activity :
                       IconName === 'MessageCircle' ? MessageCircle : 
                       IconName === 'Clock' ? Clock : Activity

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6',
      className
    )}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">{widget.title}</h3>
        <IconComponent className={cn(
          'w-5 h-5',
          color === 'blue' && 'text-blue-500',
          color === 'green' && 'text-green-500',
          color === 'red' && 'text-red-500',
          color === 'yellow' && 'text-yellow-500'
        )} />
      </div>
      
      <div className="space-y-2">
        <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-600 dark:text-gray-400">{label}</span>
          
          {previousValue && (
            <div className={cn(
              'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs',
              trendDirection === 'up' && 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
              trendDirection === 'down' && 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
              trendDirection === 'neutral' && 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
            )}>
              <TrendIcon className="w-3 h-3" />
              <span>{Math.abs(trendPercentage).toFixed(1)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

// Chart Widget - Various chart types
export const ChartWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { theme } = useUIStore(state => ({ theme: state.theme }))
  const { chartType, data, xKey, yKey, colors, showGrid = true } = widget.data

  const chartTheme = useMemo(() => ({
    background: theme === 'dark' ? '#1F2937' : '#FFFFFF',
    text: theme === 'dark' ? '#E5E7EB' : '#374151',
    grid: theme === 'dark' ? '#374151' : '#E5E7EB'
  }), [theme])

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 20 }
    }

    switch (chartType) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />}
            <XAxis dataKey={xKey} stroke={chartTheme.text} fontSize={12} />
            <YAxis stroke={chartTheme.text} fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: chartTheme.background,
                border: `1px solid ${chartTheme.grid}`,
                borderRadius: '6px'
              }}
            />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={colors?.[0] || '#3B82F6'}
              strokeWidth={2}
              dot={{ fill: colors?.[0] || '#3B82F6', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        )
      
      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />}
            <XAxis dataKey={xKey} stroke={chartTheme.text} fontSize={12} />
            <YAxis stroke={chartTheme.text} fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: chartTheme.background,
                border: `1px solid ${chartTheme.grid}`,
                borderRadius: '6px'
              }}
            />
            <Area
              type="monotone"
              dataKey={yKey}
              stroke={colors?.[0] || '#3B82F6'}
              fill={colors?.[0] || '#3B82F6'}
              fillOpacity={0.3}
            />
          </AreaChart>
        )
      
      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />}
            <XAxis dataKey={xKey} stroke={chartTheme.text} fontSize={12} />
            <YAxis stroke={chartTheme.text} fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: chartTheme.background,
                border: `1px solid ${chartTheme.grid}`,
                borderRadius: '6px'
              }}
            />
            <Bar dataKey={yKey} fill={colors?.[0] || '#3B82F6'} />
          </BarChart>
        )
      
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey={yKey}
              label={({ name, percent }: { name?: string, percent?: number }) => `${name || 'Unknown'} ${((percent || 0) * 100).toFixed(0)}%`}
            >
              {data.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={colors?.[index] || `hsl(${index * 45}, 70%, 50%)`} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        )
      
      default:
        return <div className="text-center text-gray-500">Unsupported chart type</div>
    }
  }

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4',
      className
    )}>
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">{widget.title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  )
})

// Table Widget - Data table with sorting
export const TableWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { data, columns, maxRows = 10 } = widget.data

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4',
      className
    )}>
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">{widget.title}</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              {columns.map((column: any) => (
                <th key={column.key} className="text-left py-2 px-3 font-medium text-gray-600 dark:text-gray-400">
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, maxRows).map((row: any, index: number) => (
              <tr key={index} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800">
                {columns.map((column: any) => (
                  <td key={column.key} className="py-2 px-3 text-gray-900 dark:text-gray-100">
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {data.length > maxRows && (
        <div className="mt-2 text-xs text-gray-500 text-center">
          Showing {maxRows} of {data.length} rows
        </div>
      )}
    </div>
  )
})

// Gauge Widget - Circular progress indicator
export const GaugeWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { value, max, min = 0, label, color = 'blue', thresholds } = widget.data
  
  const percentage = ((value - min) / (max - min)) * 100
  const circumference = 2 * Math.PI * 40
  const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`
  
  const getColor = () => {
    if (thresholds) {
      if (value >= thresholds.critical) return 'text-red-500'
      if (value >= thresholds.warning) return 'text-yellow-500'
      return 'text-green-500'
    }
    return `text-${color}-500`
  }

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6',
      className
    )}>
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4 text-center">{widget.title}</h3>
      
      <div className="flex flex-col items-center">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeDasharray={strokeDasharray}
              strokeLinecap="round"
              className={getColor()}
            />
          </svg>
          
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {typeof value === 'number' ? value.toFixed(1) : value}
            </span>
            <span className="text-xs text-gray-500">
              {percentage.toFixed(0)}%
            </span>
          </div>
        </div>
        
        <div className="mt-4 text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400">{label}</div>
          <div className="text-xs text-gray-500 mt-1">
            Range: {min} - {max}
          </div>
        </div>
      </div>
    </div>
  )
})

// Status Widget - System status indicators
export const StatusWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { services } = widget.data

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4',
      className
    )}>
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">{widget.title}</h3>
      
      <div className="space-y-3">
        {services.map((service: any, index: number) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getStatusIcon(service.status)}
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {service.name}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              {service.uptime && (
                <span className="text-xs text-gray-500">
                  {service.uptime}
                </span>
              )}
              <span className={cn(
                'px-2 py-1 rounded-full text-xs font-medium',
                service.status === 'healthy' && 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
                service.status === 'warning' && 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
                service.status === 'error' && 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
              )}>
                {service.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})

// Progress Widget - Multiple progress bars
export const ProgressWidget = memo<BaseWidgetProps>(({ widget, className }) => {
  const { items } = widget.data

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4',
      className
    )}>
      <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">{widget.title}</h3>
      
      <div className="space-y-4">
        {items.map((item: any, index: number) => (
          <div key={index}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
              <span className="text-sm text-gray-500">{item.value}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={cn(
                  'h-2 rounded-full transition-all duration-300',
                  item.color === 'blue' && 'bg-blue-500',
                  item.color === 'green' && 'bg-green-500',
                  item.color === 'red' && 'bg-red-500',
                  item.color === 'yellow' && 'bg-yellow-500',
                  !item.color && 'bg-blue-500'
                )}
                style={{ width: `${Math.min(item.value, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})

MetricWidget.displayName = 'MetricWidget'
ChartWidget.displayName = 'ChartWidget'
TableWidget.displayName = 'TableWidget'
GaugeWidget.displayName = 'GaugeWidget'
StatusWidget.displayName = 'StatusWidget'
ProgressWidget.displayName = 'ProgressWidget'