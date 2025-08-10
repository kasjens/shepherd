'use client'

import React, { memo, useState, useCallback, useMemo, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import {
  BarChart3,
  Download,
  Settings,
  Plus,
  RotateCcw,
  Save,
  Eye,
  EyeOff,
  Grid3X3,
  Maximize2,
  Minimize2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'
import {
  MetricWidget,
  ChartWidget,
  TableWidget,
  GaugeWidget,
  StatusWidget,
  ProgressWidget,
  WidgetData
} from './widget-types'

const ResponsiveGridLayout = WidthProvider(Responsive)

export interface DashboardConfig {
  id: string
  name: string
  layout: Layout[]
  widgets: WidgetData[]
  settings: {
    autoRefresh: boolean
    refreshInterval: number
    compactMode: boolean
    showGrid: boolean
  }
}

export interface AnalyticsDashboardProps {
  config: DashboardConfig
  onConfigChange?: (config: DashboardConfig) => void
  onExport?: (format: 'pdf' | 'png' | 'csv') => void
  onSave?: (config: DashboardConfig) => void
  isEditing?: boolean
  onEditToggle?: (editing: boolean) => void
  className?: string
}

const WIDGET_COMPONENTS = {
  metric: MetricWidget,
  chart: ChartWidget,
  table: TableWidget,
  gauge: GaugeWidget,
  status: StatusWidget,
  progress: ProgressWidget,
  heatmap: MetricWidget, // Placeholder
  timeline: ChartWidget, // Using chart as timeline
  list: TableWidget // Using table as list
}

const DEFAULT_WIDGET_SIZES = {
  metric: { w: 3, h: 2 },
  chart: { w: 6, h: 4 },
  table: { w: 8, h: 4 },
  gauge: { w: 3, h: 3 },
  status: { w: 4, h: 3 },
  progress: { w: 4, h: 3 },
  heatmap: { w: 6, h: 4 },
  timeline: { w: 12, h: 3 },
  list: { w: 6, h: 4 }
}

const AnalyticsDashboard = memo<AnalyticsDashboardProps>(({
  config,
  onConfigChange,
  onExport,
  onSave,
  isEditing = false,
  onEditToggle,
  className
}) => {
  const { reducedMotion, theme } = useUIStore(state => ({
    reducedMotion: state.reducedMotion,
    theme: state.theme
  }))

  const [layouts, setLayouts] = useState<{ [key: string]: Layout[] }>({
    lg: config.layout,
    md: config.layout,
    sm: config.layout,
    xs: config.layout,
    xxs: config.layout
  })

  const [selectedWidgets, setSelectedWidgets] = useState<Set<string>>(new Set())
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  // Auto-refresh logic
  useEffect(() => {
    if (!config.settings.autoRefresh) return

    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1)
    }, config.settings.refreshInterval * 1000)

    return () => clearInterval(interval)
  }, [config.settings.autoRefresh, config.settings.refreshInterval])

  const handleLayoutChange = useCallback((layout: Layout[], layouts: { [key: string]: Layout[] }) => {
    if (!isEditing) return
    
    setLayouts(layouts)
    
    const newConfig = {
      ...config,
      layout: layout
    }
    onConfigChange?.(newConfig)
  }, [config, onConfigChange, isEditing])

  const handleWidgetSelect = useCallback((widgetId: string, selected: boolean) => {
    setSelectedWidgets(prev => {
      const newSet = new Set(prev)
      if (selected) {
        newSet.add(widgetId)
      } else {
        newSet.delete(widgetId)
      }
      return newSet
    })
  }, [])

  const handleAddWidget = useCallback((type: WidgetData['type']) => {
    const newWidget: WidgetData = {
      id: `widget_${Date.now()}`,
      title: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
      type,
      data: getDefaultWidgetData(type)
    }

    const defaultSize = DEFAULT_WIDGET_SIZES[type]
    const newLayoutItem: Layout = {
      i: newWidget.id,
      x: 0,
      y: 0,
      w: defaultSize.w,
      h: defaultSize.h,
      minW: 2,
      minH: 1
    }

    const newConfig = {
      ...config,
      widgets: [...config.widgets, newWidget],
      layout: [...config.layout, newLayoutItem]
    }

    onConfigChange?.(newConfig)
  }, [config, onConfigChange])

  const handleRemoveSelected = useCallback(() => {
    const newWidgets = config.widgets.filter(w => !selectedWidgets.has(w.id))
    const newLayout = config.layout.filter(l => !selectedWidgets.has(l.i))

    const newConfig = {
      ...config,
      widgets: newWidgets,
      layout: newLayout
    }

    onConfigChange?.(newConfig)
    setSelectedWidgets(new Set())
  }, [config, onConfigChange, selectedWidgets])

  const handleResetLayout = useCallback(() => {
    const resetLayout = config.widgets.map((widget, index) => ({
      i: widget.id,
      x: (index % 4) * 3,
      y: Math.floor(index / 4) * 3,
      w: DEFAULT_WIDGET_SIZES[widget.type].w,
      h: DEFAULT_WIDGET_SIZES[widget.type].h
    }))

    const newConfig = {
      ...config,
      layout: resetLayout
    }

    setLayouts({
      lg: resetLayout,
      md: resetLayout,
      sm: resetLayout,
      xs: resetLayout,
      xxs: resetLayout
    })

    onConfigChange?.(newConfig)
  }, [config, onConfigChange])

  const handleExport = useCallback((format: 'pdf' | 'png' | 'csv') => {
    onExport?.(format)
  }, [onExport])

  const renderWidget = useCallback((widget: WidgetData) => {
    const WidgetComponent = WIDGET_COMPONENTS[widget.type]
    const isSelected = selectedWidgets.has(widget.id)

    return (
      <div
        key={widget.id}
        className={cn(
          'relative group',
          isEditing && 'cursor-move',
          isSelected && 'ring-2 ring-blue-500 ring-opacity-50'
        )}
        onClick={(e) => {
          if (isEditing) {
            e.stopPropagation()
            handleWidgetSelect(widget.id, !isSelected)
          }
        }}
      >
        {/* Widget Header Overlay (Edit Mode) */}
        {isEditing && (
          <div className={cn(
            'absolute top-2 right-2 z-10 flex items-center gap-1 opacity-0 group-hover:opacity-100',
            !reducedMotion && 'transition-opacity duration-200'
          )}>
            <button
              className="p-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs hover:bg-gray-50 dark:hover:bg-gray-700"
              onClick={(e) => {
                e.stopPropagation()
                setIsFullscreen(true)
              }}
            >
              <Maximize2 className="w-3 h-3" />
            </button>
            <button
              className="p-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs hover:bg-red-50 dark:hover:bg-red-900 text-red-600"
              onClick={(e) => {
                e.stopPropagation()
                handleWidgetSelect(widget.id, true)
                handleRemoveSelected()
              }}
            >
              ×
            </button>
          </div>
        )}

        <WidgetComponent widget={widget} className="h-full" />
      </div>
    )
  }, [selectedWidgets, isEditing, handleWidgetSelect, handleRemoveSelected, reducedMotion])

  const breakpoints = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }
  const cols = { lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Dashboard Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-blue-500" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {config.name}
            </h2>
            <p className="text-sm text-gray-500">
              {config.widgets.length} widget{config.widgets.length !== 1 ? 's' : ''}
              {config.settings.autoRefresh && (
                <span> • Auto-refresh: {config.settings.refreshInterval}s</span>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View/Edit Toggle */}
          <button
            onClick={() => onEditToggle?.(!isEditing)}
            className={cn(
              'px-3 py-1.5 text-sm rounded-md border',
              isEditing
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
              !reducedMotion && 'transition-colors duration-200'
            )}
          >
            {isEditing ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
            {isEditing ? 'Exit Edit' : 'Edit Layout'}
          </button>

          {/* Refresh */}
          <button
            onClick={() => setRefreshKey(prev => prev + 1)}
            className={cn(
              'p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
              !reducedMotion && 'transition-colors duration-200'
            )}
            title="Refresh Data"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Export Menu */}
          <div className="relative group">
            <button
              className={cn(
                'p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
              title="Export Dashboard"
            >
              <Download className="w-4 h-4" />
            </button>
            
            <div className={cn(
              'absolute right-0 top-full mt-1 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible',
              !reducedMotion && 'transition-all duration-200'
            )}>
              <button
                onClick={() => handleExport('pdf')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 first:rounded-t-md"
              >
                Export as PDF
              </button>
              <button
                onClick={() => handleExport('png')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Export as PNG
              </button>
              <button
                onClick={() => handleExport('csv')}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 last:rounded-b-md"
              >
                Export Data
              </button>
            </div>
          </div>

          {/* Save */}
          {isEditing && onSave && (
            <button
              onClick={() => onSave(config)}
              className={cn(
                'px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 border border-green-600',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Save className="w-4 h-4 mr-1" />
              Save
            </button>
          )}
        </div>
      </div>

      {/* Edit Mode Toolbar */}
      {isEditing && (
        <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-950 border-b border-blue-200 dark:border-blue-800">
          <span className="text-sm font-medium text-blue-900 dark:text-blue-100">Add Widget:</span>
          
          {Object.keys(WIDGET_COMPONENTS).map((type) => (
            <button
              key={type}
              onClick={() => handleAddWidget(type as WidgetData['type'])}
              className={cn(
                'px-2 py-1 text-xs bg-white dark:bg-gray-800 border border-blue-300 dark:border-blue-700 rounded hover:bg-blue-50 dark:hover:bg-blue-900 text-blue-700 dark:text-blue-300',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Plus className="w-3 h-3 mr-1" />
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}

          <div className="ml-auto flex items-center gap-2">
            {selectedWidgets.size > 0 && (
              <button
                onClick={handleRemoveSelected}
                className={cn(
                  'px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                Remove Selected ({selectedWidgets.size})
              </button>
            )}

            <button
              onClick={handleResetLayout}
              className={cn(
                'px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Grid3X3 className="w-3 h-3 mr-1" />
              Reset Layout
            </button>
          </div>
        </div>
      )}

      {/* Dashboard Grid */}
      <div className="flex-1 p-4 bg-gray-50 dark:bg-gray-950 overflow-auto">
        <ResponsiveGridLayout
          className="layout"
          layouts={layouts}
          onLayoutChange={handleLayoutChange}
          breakpoints={breakpoints}
          cols={cols}
          rowHeight={60}
          isDraggable={isEditing}
          isResizable={isEditing}
          compactType="vertical"
          preventCollision={false}
          margin={[16, 16]}
          containerPadding={[0, 0]}
          useCSSTransforms={!reducedMotion}
        >
          {config.widgets.map(renderWidget)}
        </ResponsiveGridLayout>
      </div>
    </div>
  )
})

// Helper function to generate default data for new widgets
function getDefaultWidgetData(type: WidgetData['type']) {
  switch (type) {
    case 'metric':
      return {
        value: 1234,
        previousValue: 1100,
        label: 'Total Count',
        color: 'blue',
        icon: 'Activity'
      }
    
    case 'chart':
      return {
        chartType: 'line',
        data: [
          { name: 'Jan', value: 400 },
          { name: 'Feb', value: 300 },
          { name: 'Mar', value: 600 },
          { name: 'Apr', value: 800 },
          { name: 'May', value: 500 }
        ],
        xKey: 'name',
        yKey: 'value',
        colors: ['#3B82F6']
      }
    
    case 'table':
      return {
        columns: [
          { key: 'name', title: 'Name' },
          { key: 'value', title: 'Value' },
          { key: 'status', title: 'Status' }
        ],
        data: [
          { name: 'Item 1', value: 100, status: 'Active' },
          { name: 'Item 2', value: 200, status: 'Inactive' },
          { name: 'Item 3', value: 150, status: 'Active' }
        ]
      }
    
    case 'gauge':
      return {
        value: 75,
        min: 0,
        max: 100,
        label: 'Performance',
        color: 'blue',
        thresholds: { warning: 70, critical: 90 }
      }
    
    case 'status':
      return {
        services: [
          { name: 'API Server', status: 'healthy', uptime: '99.9%' },
          { name: 'Database', status: 'healthy', uptime: '99.5%' },
          { name: 'Cache', status: 'warning', uptime: '95.2%' }
        ]
      }
    
    case 'progress':
      return {
        items: [
          { label: 'CPU Usage', value: 45, color: 'blue' },
          { label: 'Memory', value: 68, color: 'green' },
          { label: 'Disk Space', value: 32, color: 'yellow' }
        ]
      }
    
    default:
      return {}
  }
}

AnalyticsDashboard.displayName = 'AnalyticsDashboard'

export default AnalyticsDashboard