'use client'

import React, { useState, useEffect, useCallback, useMemo, Suspense, lazy } from 'react'
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp, 
  Activity, 
  Users, 
  Zap,
  Download,
  Filter,
  Maximize2,
  Grid3X3,
  List,
  RefreshCw,
  Settings,
  Eye,
  EyeOff,
  ChevronDown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { FixedSizeGrid as Grid } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'
import { useWebSocket } from '@/hooks/use-websocket'

// Lazy load heavy chart components
const LazyLineChart = lazy(() => import('./charts/line-chart'))
const LazyBarChart = lazy(() => import('./charts/bar-chart'))
const LazyPieChart = lazy(() => import('./charts/pie-chart'))
const LazyHeatmap = lazy(() => import('./charts/heatmap'))
const LazyScatterPlot = lazy(() => import('./charts/scatter-plot'))
const LazyAreaChart = lazy(() => import('./charts/area-chart'))

export interface ChartWidget {
  id: string
  type: 'line' | 'bar' | 'pie' | 'heatmap' | 'scatter' | 'area'
  title: string
  description?: string
  dataSource: string
  config: ChartConfig
  position: { x: number; y: number }
  size: { width: number; height: number }
  isVisible: boolean
  lastUpdated: Date
  updateInterval?: number // milliseconds
}

export interface ChartConfig {
  xAxis?: string
  yAxis?: string | string[]
  groupBy?: string
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max'
  timeRange?: '1h' | '6h' | '24h' | '7d' | '30d'
  filters?: Record<string, any>
  colors?: string[]
  showLegend?: boolean
  showGrid?: boolean
  animate?: boolean
}

export interface DashboardData {
  [key: string]: any[]
}

export interface AdvancedDashboardProps {
  widgets: ChartWidget[]
  data: DashboardData
  onWidgetUpdate?: (widget: ChartWidget) => void
  onWidgetAdd?: () => void
  onWidgetRemove?: (widgetId: string) => void
  onExport?: (format: 'png' | 'pdf' | 'json') => void
  className?: string
}

// Chart component mapping
const CHART_COMPONENTS = {
  line: LazyLineChart,
  bar: LazyBarChart,
  pie: LazyPieChart,
  heatmap: LazyHeatmap,
  scatter: LazyScatterPlot,
  area: LazyAreaChart
}

export function AdvancedDashboard({
  widgets,
  data,
  onWidgetUpdate,
  onWidgetAdd,
  onWidgetRemove,
  onExport,
  className
}: AdvancedDashboardProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [filters, setFilters] = useState<Record<string, any>>({})
  const [gridColumns, setGridColumns] = useState(3)
  
  // WebSocket for real-time updates
  const ws = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      if (message.type === 'analytics_update' && onWidgetUpdate) {
        const updatedWidget = widgets.find(w => w.id === message.widgetId)
        if (updatedWidget) {
          onWidgetUpdate({
            ...updatedWidget,
            lastUpdated: new Date()
          })
        }
      }
    }
  })

  // Filter visible widgets
  const visibleWidgets = useMemo(() => 
    widgets.filter(widget => widget.isVisible),
    [widgets]
  )

  // Grid layout calculations
  const gridItemHeight = 300
  const gridItemWidth = 400
  const getGridRows = useCallback(() => 
    Math.ceil(visibleWidgets.length / gridColumns), [visibleWidgets.length, gridColumns]
  )

  // Refresh all widgets
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true)
    try {
      // Send refresh request via WebSocket
      await ws.send('analytics:refresh_all', { 
        widgetIds: visibleWidgets.map(w => w.id),
        filters 
      })
    } catch (error) {
      console.error('Failed to refresh dashboard:', error)
    } finally {
      setIsRefreshing(false)
    }
  }, [ws, visibleWidgets, filters])

  // Auto-refresh effect
  useEffect(() => {
    const intervals = new Map<string, NodeJS.Timeout>()
    
    visibleWidgets.forEach(widget => {
      if (widget.updateInterval && widget.updateInterval > 0) {
        const interval = setInterval(() => {
          if (onWidgetUpdate) {
            onWidgetUpdate({
              ...widget,
              lastUpdated: new Date()
            })
          }
        }, widget.updateInterval)
        
        intervals.set(widget.id, interval)
      }
    })

    return () => {
      intervals.forEach(interval => clearInterval(interval))
    }
  }, [visibleWidgets, onWidgetUpdate])

  // Grid cell renderer
  const GridCell = useCallback(({ columnIndex, rowIndex, style }: any) => {
    const widgetIndex = rowIndex * gridColumns + columnIndex
    const widget = visibleWidgets[widgetIndex]
    
    if (!widget) {
      return <div style={style} />
    }

    return (
      <div style={style} className="p-2">
        <WidgetCard
          widget={widget}
          data={data[widget.dataSource] || []}
          isSelected={selectedWidget === widget.id}
          onSelect={() => setSelectedWidget(widget.id)}
          onUpdate={onWidgetUpdate}
          onRemove={onWidgetRemove}
        />
      </div>
    )
  }, [visibleWidgets, gridColumns, data, selectedWidget, onWidgetUpdate, onWidgetRemove])

  return (
    <div className={cn('flex flex-col h-full bg-white dark:bg-gray-900', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-blue-500" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Advanced Analytics
          </h2>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Activity className={cn(
              'w-4 h-4',
              ws.isConnected ? 'text-green-500' : 'text-red-500'
            )} />
            {visibleWidgets.length} widgets
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 dark:border-gray-600 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded-l-lg',
                viewMode === 'grid'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-r-lg border-l border-gray-300 dark:border-gray-600',
                viewMode === 'list'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Grid Columns Selector (Grid mode only) */}
          {viewMode === 'grid' && (
            <select
              value={gridColumns}
              onChange={(e) => setGridColumns(Number(e.target.value))}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm"
            >
              <option value={1}>1 Column</option>
              <option value={2}>2 Columns</option>
              <option value={3}>3 Columns</option>
              <option value={4}>4 Columns</option>
            </select>
          )}

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={cn(
              'p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200',
              'border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
              isRefreshing && 'opacity-50 cursor-not-allowed'
            )}
            title="Refresh All Widgets"
          >
            <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
          </button>

          {/* Export Button */}
          <div className="relative group">
            <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700">
              <Download className="w-4 h-4" />
            </button>
            <div className="absolute right-0 top-full mt-1 invisible group-hover:visible bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg py-1 z-10">
              <button
                onClick={() => onExport?.('png')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Export as PNG
              </button>
              <button
                onClick={() => onExport?.('pdf')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Export as PDF
              </button>
              <button
                onClick={() => onExport?.('json')}
                className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Export Data (JSON)
              </button>
            </div>
          </div>

          {/* Add Widget Button */}
          <button
            onClick={onWidgetAdd}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm font-medium"
          >
            Add Widget
          </button>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="flex-1 overflow-hidden">
        {visibleWidgets.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <BarChart3 className="w-16 h-16 mb-4 opacity-50" />
            <div className="text-xl font-medium mb-2">No Widgets</div>
            <div className="text-sm mb-4">Add your first analytics widget to get started</div>
            <button
              onClick={onWidgetAdd}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
            >
              Add Widget
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          <AutoSizer>
            {({ height, width }) => (
              <Grid
                columnCount={gridColumns}
                rowCount={getGridRows()}
                columnWidth={width / gridColumns}
                rowHeight={gridItemHeight}
                height={height}
                width={width}
                overscanRowCount={1}
                overscanColumnCount={1}
              >
                {GridCell}
              </Grid>
            )}
          </AutoSizer>
        ) : (
          <div className="h-full overflow-y-auto">
            <div className="space-y-4 p-4">
              {visibleWidgets.map((widget) => (
                <WidgetCard
                  key={widget.id}
                  widget={widget}
                  data={data[widget.dataSource] || []}
                  isSelected={selectedWidget === widget.id}
                  onSelect={() => setSelectedWidget(widget.id)}
                  onUpdate={onWidgetUpdate}
                  onRemove={onWidgetRemove}
                  variant="list"
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Individual Widget Card Component
interface WidgetCardProps {
  widget: ChartWidget
  data: any[]
  isSelected: boolean
  onSelect: () => void
  onUpdate?: (widget: ChartWidget) => void
  onRemove?: (widgetId: string) => void
  variant?: 'grid' | 'list'
}

function WidgetCard({
  widget,
  data,
  isSelected,
  onSelect,
  onUpdate,
  onRemove,
  variant = 'grid'
}: WidgetCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const ChartComponent = CHART_COMPONENTS[widget.type]

  const handleToggleVisibility = () => {
    onUpdate?.({
      ...widget,
      isVisible: !widget.isVisible
    })
  }

  const handleRemove = () => {
    if (window.confirm(`Remove widget "${widget.title}"?`)) {
      onRemove?.(widget.id)
    }
  }

  return (
    <div
      className={cn(
        'border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow',
        isSelected && 'ring-2 ring-blue-500',
        variant === 'list' && 'h-80'
      )}
      onClick={onSelect}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">
            {widget.title}
          </h3>
          {widget.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {widget.description}
            </p>
          )}
        </div>

        <div className="flex items-center gap-1">
          <div className="text-xs text-gray-400">
            {widget.lastUpdated.toLocaleTimeString()}
          </div>
          
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleToggleVisibility()
            }}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            title={widget.isVisible ? 'Hide Widget' : 'Show Widget'}
          >
            {widget.isVisible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation()
              handleRemove()
            }}
            className="p-1 text-gray-400 hover:text-red-500"
            title="Remove Widget"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Widget Content */}
      <div className={cn(
        'p-4',
        variant === 'grid' ? 'h-56' : 'h-64'
      )}>
        {error ? (
          <div className="flex items-center justify-center h-full text-red-500">
            <div className="text-center">
              <div className="text-sm font-medium">Error loading chart</div>
              <div className="text-xs mt-1">{error}</div>
            </div>
          </div>
        ) : (
          <Suspense 
            fallback={
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
              </div>
            }
          >
            <ChartComponent
              data={data}
              config={widget.config}
              width="100%"
              height="100%"
              onError={setError}
              onLoadingChange={setIsLoading}
            />
          </Suspense>
        )}
      </div>
    </div>
  )
}

export default AdvancedDashboard