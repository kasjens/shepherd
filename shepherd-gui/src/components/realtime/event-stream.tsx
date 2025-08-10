'use client'

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  User, 
  Zap, 
  MessageSquare, 
  Settings, 
  Play, 
  Pause, 
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  EyeOff
} from 'lucide-react'
import { format as formatDate, formatDistanceToNow } from 'date-fns'
import { cn } from '@/lib/utils'
import { useWebSocket } from '@/hooks/use-websocket'
import { FixedSizeList as List } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'

export type EventLevel = 'info' | 'success' | 'warning' | 'error' | 'debug'
export type EventCategory = 'system' | 'user' | 'workflow' | 'agent' | 'api' | 'security'

export interface StreamEvent {
  id: string
  timestamp: Date
  level: EventLevel
  category: EventCategory
  title: string
  message: string
  source: string
  userId?: string
  userName?: string
  metadata?: Record<string, any>
  tags?: string[]
}

export interface EventStreamProps {
  maxEvents?: number
  autoScroll?: boolean
  showFilters?: boolean
  showSearch?: boolean
  showExport?: boolean
  levels?: EventLevel[]
  categories?: EventCategory[]
  className?: string
}

export function EventStream({
  maxEvents = 1000,
  autoScroll = true,
  showFilters = true,
  showSearch = true,
  showExport = true,
  levels = ['info', 'success', 'warning', 'error', 'debug'],
  categories = ['system', 'user', 'workflow', 'agent', 'api', 'security'],
  className
}: EventStreamProps) {
  const [events, setEvents] = useState<StreamEvent[]>([])
  const [isStreaming, setIsStreaming] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevels, setSelectedLevels] = useState<Set<EventLevel>>(new Set(levels))
  const [selectedCategories, setSelectedCategories] = useState<Set<EventCategory>>(new Set(categories))
  const [showDetails, setShowDetails] = useState(false)

  // WebSocket connection for real-time events
  const ws = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      if (message.type === 'event_stream' && isStreaming) {
        handleNewEvent(message.data)
      }
    }
  })

  // Filter events based on search and filters
  const filteredEvents = useMemo(() => {
    return events
      .filter(event => {
        // Level filter
        if (!selectedLevels.has(event.level)) return false
        
        // Category filter
        if (!selectedCategories.has(event.category)) return false
        
        // Search filter
        if (searchQuery) {
          const query = searchQuery.toLowerCase()
          return (
            event.title.toLowerCase().includes(query) ||
            event.message.toLowerCase().includes(query) ||
            event.source.toLowerCase().includes(query) ||
            event.userName?.toLowerCase().includes(query) ||
            event.tags?.some(tag => tag.toLowerCase().includes(query))
          )
        }
        
        return true
      })
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }, [events, selectedLevels, selectedCategories, searchQuery])

  // Handle new incoming events
  const handleNewEvent = useCallback((eventData: any) => {
    const event: StreamEvent = {
      id: eventData.id || `event_${Date.now()}_${Math.random()}`,
      timestamp: new Date(eventData.timestamp),
      level: eventData.level || 'info',
      category: eventData.category || 'system',
      title: eventData.title,
      message: eventData.message,
      source: eventData.source,
      userId: eventData.userId,
      userName: eventData.userName,
      metadata: eventData.metadata,
      tags: eventData.tags || []
    }

    setEvents(prev => {
      const newEvents = [event, ...prev]
      // Limit events to maxEvents
      return newEvents.slice(0, maxEvents)
    })
  }, [maxEvents])

  // Subscribe to different event streams
  useEffect(() => {
    if (!ws.isConnected) return

    const subscriptions = [
      // System events
      ws.subscribe('system:event', (data) => {
        handleNewEvent({
          ...data,
          level: 'info',
          category: 'system'
        })
      }),

      // Workflow events
      ws.subscribe('workflow:event', (data) => {
        handleNewEvent({
          ...data,
          level: data.status === 'error' ? 'error' : data.status === 'completed' ? 'success' : 'info',
          category: 'workflow'
        })
      }),

      // Agent events
      ws.subscribe('agent:event', (data) => {
        handleNewEvent({
          ...data,
          level: 'info',
          category: 'agent'
        })
      }),

      // API events
      ws.subscribe('api:event', (data) => {
        handleNewEvent({
          ...data,
          level: data.status >= 400 ? 'error' : data.status >= 300 ? 'warning' : 'info',
          category: 'api'
        })
      }),

      // User events
      ws.subscribe('user:event', (data) => {
        handleNewEvent({
          ...data,
          level: 'info',
          category: 'user'
        })
      }),

      // Security events
      ws.subscribe('security:event', (data) => {
        handleNewEvent({
          ...data,
          level: data.severity === 'high' ? 'error' : data.severity === 'medium' ? 'warning' : 'info',
          category: 'security'
        })
      })
    ]

    return () => {
      subscriptions.forEach(unsubscribe => unsubscribe())
    }
  }, [ws, handleNewEvent])

  // Toggle streaming
  const toggleStreaming = useCallback(() => {
    setIsStreaming(!isStreaming)
  }, [isStreaming])

  // Clear all events
  const clearEvents = useCallback(() => {
    setEvents([])
  }, [])

  // Export events
  const exportEvents = useCallback((format: 'json' | 'csv' = 'json') => {
    const dataStr = format === 'json' 
      ? JSON.stringify(filteredEvents, null, 2)
      : convertToCSV(filteredEvents)
    
    const blob = new Blob([dataStr], { type: format === 'json' ? 'application/json' : 'text/csv' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `events-${format}-${formatDate(new Date(), 'yyyy-MM-dd-HH-mm')}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [filteredEvents])

  return (
    <div className={cn('flex flex-col h-full bg-white dark:bg-gray-900', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Event Stream
          </h2>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <div className={cn(
              'w-2 h-2 rounded-full',
              isStreaming ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            )} />
            {filteredEvents.length} events
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Connection status */}
          <div className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            ws.isConnected
              ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
              : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
          )}>
            {ws.isConnected ? 'Connected' : 'Disconnected'}
          </div>

          {/* Controls */}
          <button
            onClick={toggleStreaming}
            className={cn(
              'p-2 rounded-md border',
              isStreaming
                ? 'border-red-300 text-red-600 hover:bg-red-50 dark:hover:bg-red-950'
                : 'border-green-300 text-green-600 hover:bg-green-50 dark:hover:bg-green-950'
            )}
            title={isStreaming ? 'Pause Stream' : 'Resume Stream'}
          >
            {isStreaming ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setShowDetails(!showDetails)}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
            title={showDetails ? 'Hide Details' : 'Show Details'}
          >
            {showDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>

          {showExport && (
            <button
              onClick={() => exportEvents('json')}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
              title="Export Events"
            >
              <Download className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={clearEvents}
            className="p-2 text-red-600 hover:text-red-800 border border-red-300 rounded-md hover:bg-red-50 dark:hover:bg-red-950"
            title="Clear All Events"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      {(showFilters || showSearch) && (
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
          {/* Search */}
          {showSearch && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Level and Category Filters */}
          {showFilters && (
            <div className="grid grid-cols-2 gap-4">
              {/* Levels */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Levels
                </label>
                <div className="flex flex-wrap gap-1">
                  {levels.map((level) => (
                    <button
                      key={level}
                      onClick={() => {
                        const newSelected = new Set(selectedLevels)
                        if (newSelected.has(level)) {
                          newSelected.delete(level)
                        } else {
                          newSelected.add(level)
                        }
                        setSelectedLevels(newSelected)
                      }}
                      className={cn(
                        'px-2 py-1 text-xs rounded-full border',
                        selectedLevels.has(level)
                          ? getLevelStyles(level).active
                          : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                      )}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Categories */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Categories
                </label>
                <div className="flex flex-wrap gap-1">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => {
                        const newSelected = new Set(selectedCategories)
                        if (newSelected.has(category)) {
                          newSelected.delete(category)
                        } else {
                          newSelected.add(category)
                        }
                        setSelectedCategories(newSelected)
                      }}
                      className={cn(
                        'px-2 py-1 text-xs rounded-full border',
                        selectedCategories.has(category)
                          ? 'bg-blue-100 dark:bg-blue-900 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300'
                          : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                      )}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Event List */}
      <div className="flex-1">
        {filteredEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Activity className="w-12 h-12 mb-4 opacity-50" />
            <div className="text-lg font-medium">No events</div>
            <div className="text-sm">
              {events.length === 0 
                ? 'Waiting for events...' 
                : 'No events match your filters'
              }
            </div>
          </div>
        ) : (
          <AutoSizer>
            {({ height, width }) => (
              <List
                height={height}
                width={width}
                itemCount={filteredEvents.length}
                itemSize={showDetails ? 120 : 80}
                overscanCount={10}
              >
                {({ index, style }) => (
                  <EventItem
                    key={filteredEvents[index].id}
                    event={filteredEvents[index]}
                    showDetails={showDetails}
                    style={style}
                  />
                )}
              </List>
            )}
          </AutoSizer>
        )}
      </div>
    </div>
  )
}

// Event Item Component
interface EventItemProps {
  event: StreamEvent
  showDetails: boolean
  style: React.CSSProperties
}

function EventItem({ event, showDetails, style }: EventItemProps) {
  const getIcon = () => {
    switch (event.category) {
      case 'system':
        return <Settings className="w-4 h-4" />
      case 'user':
        return <User className="w-4 h-4" />
      case 'workflow':
        return <Zap className="w-4 h-4" />
      case 'agent':
        return <Activity className="w-4 h-4" />
      case 'api':
        return <MessageSquare className="w-4 h-4" />
      case 'security':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  const levelStyles = getLevelStyles(event.level)

  return (
    <div style={style} className="px-4 py-2">
      <div className={cn(
        'flex items-start gap-3 p-3 rounded-lg border-l-4',
        levelStyles.background,
        levelStyles.border
      )}>
        <div className={cn('flex-shrink-0 mt-1', levelStyles.text)}>
          {getIcon()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                {event.title}
              </div>
              <div className="text-gray-600 dark:text-gray-400 text-sm mt-1 line-clamp-2">
                {event.message}
              </div>
            </div>

            <div className="flex-shrink-0 text-right">
              <div className="text-xs text-gray-500">
                {formatDistanceToNow(event.timestamp, { addSuffix: true })}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {formatDate(event.timestamp, 'HH:mm:ss')}
              </div>
            </div>
          </div>

          {showDetails && (
            <div className="mt-2 space-y-1">
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Source: {event.source}</span>
                {event.userName && <span>User: {event.userName}</span>}
                <span>Level: {event.level}</span>
                <span>Category: {event.category}</span>
              </div>
              
              {event.tags && event.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {event.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Utility functions
function getLevelStyles(level: EventLevel) {
  switch (level) {
    case 'error':
      return {
        background: 'bg-red-50 dark:bg-red-950',
        border: 'border-l-red-500',
        text: 'text-red-600',
        active: 'bg-red-100 dark:bg-red-900 border-red-300 dark:border-red-700 text-red-700 dark:text-red-300'
      }
    case 'warning':
      return {
        background: 'bg-yellow-50 dark:bg-yellow-950',
        border: 'border-l-yellow-500',
        text: 'text-yellow-600',
        active: 'bg-yellow-100 dark:bg-yellow-900 border-yellow-300 dark:border-yellow-700 text-yellow-700 dark:text-yellow-300'
      }
    case 'success':
      return {
        background: 'bg-green-50 dark:bg-green-950',
        border: 'border-l-green-500',
        text: 'text-green-600',
        active: 'bg-green-100 dark:bg-green-900 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300'
      }
    case 'debug':
      return {
        background: 'bg-purple-50 dark:bg-purple-950',
        border: 'border-l-purple-500',
        text: 'text-purple-600',
        active: 'bg-purple-100 dark:bg-purple-900 border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-300'
      }
    case 'info':
    default:
      return {
        background: 'bg-blue-50 dark:bg-blue-950',
        border: 'border-l-blue-500',
        text: 'text-blue-600',
        active: 'bg-blue-100 dark:bg-blue-900 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300'
      }
  }
}

function convertToCSV(events: StreamEvent[]): string {
  const headers = ['timestamp', 'level', 'category', 'title', 'message', 'source', 'userName', 'tags']
  const csvContent = [
    headers.join(','),
    ...events.map(event => [
      event.timestamp.toISOString(),
      event.level,
      event.category,
      `"${event.title.replace(/"/g, '""')}"`,
      `"${event.message.replace(/"/g, '""')}"`,
      event.source,
      event.userName || '',
      `"${(event.tags || []).join(', ')}"`
    ].join(','))
  ].join('\n')
  
  return csvContent
}