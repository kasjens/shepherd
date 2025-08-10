'use client'

import React, { memo, useState, useCallback, useMemo } from 'react'
import {
  FileText,
  Download,
  FileCode,
  FileImage,
  Globe,
  Package,
  Calendar,
  Filter,
  Settings,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Users,
  MessageSquare,
  Clock
} from 'lucide-react'
import { format, startOfDay, endOfDay, subDays } from 'date-fns'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface ConversationData {
  id: string
  title: string
  participants: string[]
  messageCount: number
  startDate: Date
  endDate: Date
  totalTokens: number
  status: 'active' | 'archived' | 'deleted'
  tags: string[]
  messages: {
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: Date
    tokens: number
    artifacts?: {
      id: string
      name: string
      type: string
      content: string
    }[]
  }[]
}

export interface ExportOptions {
  format: 'txt' | 'md' | 'json' | 'html' | 'pdf' | 'csv'
  includeMetadata: boolean
  includeArtifacts: boolean
  includeSystemMessages: boolean
  dateRange: {
    start: Date | null
    end: Date | null
  }
  selectedConversations: Set<string>
  compressionEnabled: boolean
  passwordProtected: boolean
  password?: string
  customFilename?: string
}

export interface ConversationExportProps {
  conversations: ConversationData[]
  onExport: (options: ExportOptions) => Promise<void>
  onPreview: (conversationId: string, format: string) => void
  className?: string
}

const EXPORT_FORMATS = [
  {
    id: 'txt',
    name: 'Plain Text',
    icon: FileText,
    description: 'Simple text format, easy to read',
    extension: '.txt',
    supportedFeatures: ['metadata', 'messages']
  },
  {
    id: 'md',
    name: 'Markdown',
    icon: FileCode,
    description: 'Formatted text with syntax highlighting',
    extension: '.md',
    supportedFeatures: ['metadata', 'messages', 'artifacts', 'formatting']
  },
  {
    id: 'json',
    name: 'JSON',
    icon: Package,
    description: 'Structured data for programmatic access',
    extension: '.json',
    supportedFeatures: ['metadata', 'messages', 'artifacts', 'system', 'tokens']
  },
  {
    id: 'html',
    name: 'HTML',
    icon: Globe,
    description: 'Web page with interactive features',
    extension: '.html',
    supportedFeatures: ['metadata', 'messages', 'artifacts', 'formatting', 'interactive']
  },
  {
    id: 'pdf',
    name: 'PDF',
    icon: FileImage,
    description: 'Printable document format',
    extension: '.pdf',
    supportedFeatures: ['metadata', 'messages', 'artifacts', 'formatting']
  },
  {
    id: 'csv',
    name: 'CSV',
    icon: FileText,
    description: 'Spreadsheet format for data analysis',
    extension: '.csv',
    supportedFeatures: ['metadata', 'messages', 'tokens']
  }
]

const DATE_PRESETS = [
  { label: 'Last 24 hours', value: 1 },
  { label: 'Last 7 days', value: 7 },
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'All time', value: null }
]

const ConversationExport = memo<ConversationExportProps>(({
  conversations,
  onExport,
  onPreview,
  className
}) => {
  const { reducedMotion } = useUIStore(state => ({ reducedMotion: state.reducedMotion }))

  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'md',
    includeMetadata: true,
    includeArtifacts: true,
    includeSystemMessages: false,
    dateRange: { start: null, end: null },
    selectedConversations: new Set(),
    compressionEnabled: false,
    passwordProtected: false,
    customFilename: ''
  })

  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [expandedOptions, setExpandedOptions] = useState(false)

  // Filter conversations based on search and filters
  const filteredConversations = useMemo(() => {
    return conversations.filter(conv => {
      // Search filter
      if (searchQuery && !conv.title.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }

      // Status filter
      if (statusFilter !== 'all' && conv.status !== statusFilter) {
        return false
      }

      // Date range filter
      if (exportOptions.dateRange.start || exportOptions.dateRange.end) {
        const start = exportOptions.dateRange.start ? startOfDay(exportOptions.dateRange.start) : null
        const end = exportOptions.dateRange.end ? endOfDay(exportOptions.dateRange.end) : null

        if (start && conv.endDate < start) return false
        if (end && conv.startDate > end) return false
      }

      return true
    })
  }, [conversations, searchQuery, statusFilter, exportOptions.dateRange])

  // Calculate export statistics
  const exportStats = useMemo(() => {
    const selected = filteredConversations.filter(conv => 
      exportOptions.selectedConversations.has(conv.id)
    )

    return {
      totalConversations: selected.length,
      totalMessages: selected.reduce((sum, conv) => sum + conv.messageCount, 0),
      totalTokens: selected.reduce((sum, conv) => sum + conv.totalTokens, 0),
      dateRange: selected.length > 0 ? {
        start: new Date(Math.min(...selected.map(conv => conv.startDate.getTime()))),
        end: new Date(Math.max(...selected.map(conv => conv.endDate.getTime())))
      } : null
    }
  }, [filteredConversations, exportOptions.selectedConversations])

  const handleFormatChange = useCallback((format: ExportOptions['format']) => {
    setExportOptions(prev => ({ ...prev, format }))
  }, [])

  const handleOptionChange = useCallback((key: keyof ExportOptions, value: any) => {
    setExportOptions(prev => ({ ...prev, [key]: value }))
  }, [])

  const handleDatePreset = useCallback((days: number | null) => {
    if (days === null) {
      setExportOptions(prev => ({
        ...prev,
        dateRange: { start: null, end: null }
      }))
    } else {
      setExportOptions(prev => ({
        ...prev,
        dateRange: {
          start: subDays(new Date(), days),
          end: new Date()
        }
      }))
    }
  }, [])

  const handleConversationToggle = useCallback((conversationId: string, selected: boolean) => {
    setExportOptions(prev => {
      const newSelected = new Set(prev.selectedConversations)
      if (selected) {
        newSelected.add(conversationId)
      } else {
        newSelected.delete(conversationId)
      }
      return { ...prev, selectedConversations: newSelected }
    })
  }, [])

  const handleSelectAll = useCallback(() => {
    const allIds = new Set(filteredConversations.map(conv => conv.id))
    setExportOptions(prev => ({ ...prev, selectedConversations: allIds }))
  }, [filteredConversations])

  const handleSelectNone = useCallback(() => {
    setExportOptions(prev => ({ ...prev, selectedConversations: new Set() }))
  }, [])

  const handleExport = useCallback(async () => {
    if (exportOptions.selectedConversations.size === 0) return

    setIsExporting(true)
    setExportProgress(0)

    try {
      // Simulate progress
      for (let i = 0; i <= 100; i += 10) {
        setExportProgress(i)
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      await onExport(exportOptions)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
      setExportProgress(0)
    }
  }, [exportOptions, onExport])

  const selectedFormat = EXPORT_FORMATS.find(f => f.id === exportOptions.format)

  return (
    <div className={cn('flex flex-col h-full bg-white dark:bg-gray-900', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <Download className="w-6 h-6 text-blue-500" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Export Conversations
            </h2>
            <p className="text-sm text-gray-500">
              Export your conversations in various formats
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setExpandedOptions(!expandedOptions)}
            className={cn(
              'px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
              !reducedMotion && 'transition-colors duration-200'
            )}
          >
            <Settings className="w-4 h-4 mr-1" />
            {expandedOptions ? 'Hide' : 'Show'} Options
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Conversation List */}
        <div className="w-2/3 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Filters */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
            <div className="flex gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
                />
              </div>
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <button
                  onClick={handleSelectAll}
                  className={cn(
                    'px-2 py-1 text-xs border border-blue-300 dark:border-blue-700 rounded text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950',
                    !reducedMotion && 'transition-colors duration-200'
                  )}
                >
                  Select All ({filteredConversations.length})
                </button>
                <button
                  onClick={handleSelectNone}
                  className={cn(
                    'px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
                    !reducedMotion && 'transition-colors duration-200'
                  )}
                >
                  Select None
                </button>
              </div>
              
              <div className="text-sm text-gray-500">
                {exportOptions.selectedConversations.size} of {filteredConversations.length} selected
              </div>
            </div>

            {/* Date Range Presets */}
            <div className="flex gap-2 flex-wrap">
              {DATE_PRESETS.map((preset) => (
                <button
                  key={preset.label}
                  onClick={() => handleDatePreset(preset.value)}
                  className={cn(
                    'px-2 py-1 text-xs rounded border',
                    (preset.value === null && !exportOptions.dateRange.start && !exportOptions.dateRange.end) ||
                    (preset.value && exportOptions.dateRange.start && 
                     exportOptions.dateRange.start.getTime() === subDays(new Date(), preset.value).setHours(0,0,0,0))
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700'
                      : 'border-gray-300 dark:border-gray-600 text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
                    !reducedMotion && 'transition-colors duration-200'
                  )}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-auto p-4 space-y-2">
            {filteredConversations.map((conversation) => {
              const isSelected = exportOptions.selectedConversations.has(conversation.id)
              const statusColor = {
                active: 'text-green-600',
                archived: 'text-blue-600',
                deleted: 'text-red-600'
              }[conversation.status]

              return (
                <div
                  key={conversation.id}
                  className={cn(
                    'p-3 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer',
                    isSelected
                      ? 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800'
                      : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700',
                    !reducedMotion && 'transition-colors duration-200'
                  )}
                  onClick={() => handleConversationToggle(conversation.id, !isSelected)}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="mt-1 w-4 h-4 text-blue-600"
                    />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {conversation.title}
                        </h3>
                        <span className={cn('text-xs px-1.5 py-0.5 rounded', statusColor)}>
                          {conversation.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {conversation.messageCount} messages
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {conversation.participants.length} participants
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {format(conversation.endDate, 'MMM dd, yyyy')}
                        </div>
                      </div>
                      
                      {conversation.tags.length > 0 && (
                        <div className="flex gap-1 mt-2">
                          {conversation.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                          {conversation.tags.length > 3 && (
                            <span className="text-xs text-gray-500">+{conversation.tags.length - 3}</span>
                          )}
                        </div>
                      )}
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onPreview(conversation.id, exportOptions.format)
                      }}
                      className={cn(
                        'p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300',
                        !reducedMotion && 'transition-colors duration-200'
                      )}
                      title="Preview"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )
            })}

            {filteredConversations.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <div className="text-lg font-medium mb-1">No conversations found</div>
                <div className="text-sm">Try adjusting your search criteria</div>
              </div>
            )}
          </div>
        </div>

        {/* Export Options */}
        <div className="w-1/3 flex flex-col">
          {/* Format Selection */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Export Format</h3>
            
            <div className="grid gap-2">
              {EXPORT_FORMATS.map((format) => {
                const IconComponent = format.icon
                const isSelected = exportOptions.format === format.id
                
                return (
                  <button
                    key={format.id}
                    onClick={() => handleFormatChange(format.id as ExportOptions['format'])}
                    className={cn(
                      'flex items-start gap-3 p-3 border rounded-lg text-left',
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700',
                      !reducedMotion && 'transition-colors duration-200'
                    )}
                  >
                    <IconComponent className={cn(
                      'w-5 h-5 flex-shrink-0 mt-0.5',
                      isSelected ? 'text-blue-600' : 'text-gray-500'
                    )} />
                    
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 dark:text-gray-100">
                        {format.name}
                      </div>
                      <div className="text-sm text-gray-500 mt-0.5">
                        {format.description}
                      </div>
                    </div>

                    {isSelected && (
                      <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Export Options */}
          {expandedOptions && (
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Options</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-gray-700 dark:text-gray-300">Include metadata</label>
                  <input
                    type="checkbox"
                    checked={exportOptions.includeMetadata}
                    onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
                    className="w-4 h-4 text-blue-600"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm text-gray-700 dark:text-gray-300">Include artifacts</label>
                  <input
                    type="checkbox"
                    checked={exportOptions.includeArtifacts}
                    onChange={(e) => handleOptionChange('includeArtifacts', e.target.checked)}
                    className="w-4 h-4 text-blue-600"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm text-gray-700 dark:text-gray-300">Include system messages</label>
                  <input
                    type="checkbox"
                    checked={exportOptions.includeSystemMessages}
                    onChange={(e) => handleOptionChange('includeSystemMessages', e.target.checked)}
                    className="w-4 h-4 text-blue-600"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm text-gray-700 dark:text-gray-300">Enable compression</label>
                  <input
                    type="checkbox"
                    checked={exportOptions.compressionEnabled}
                    onChange={(e) => handleOptionChange('compressionEnabled', e.target.checked)}
                    className="w-4 h-4 text-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                    Custom filename (optional)
                  </label>
                  <input
                    type="text"
                    value={exportOptions.customFilename}
                    onChange={(e) => handleOptionChange('customFilename', e.target.value)}
                    placeholder={`conversations_${format(new Date(), 'yyyy-MM-dd')}`}
                    className="w-full p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Export Summary */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Export Summary</h3>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Conversations:</span>
                <span className="font-medium">{exportStats.totalConversations}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Messages:</span>
                <span className="font-medium">{exportStats.totalMessages.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Tokens:</span>
                <span className="font-medium">{exportStats.totalTokens.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Format:</span>
                <span className="font-medium">{selectedFormat?.name}</span>
              </div>
            </div>

            {exportStats.dateRange && (
              <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                <div className="text-gray-500">Date Range:</div>
                <div className="font-medium">
                  {format(exportStats.dateRange.start, 'MMM dd, yyyy')} -{' '}
                  {format(exportStats.dateRange.end, 'MMM dd, yyyy')}
                </div>
              </div>
            )}
          </div>

          {/* Export Button */}
          <div className="flex-1 p-4">
            <button
              onClick={handleExport}
              disabled={isExporting || exportOptions.selectedConversations.size === 0}
              className={cn(
                'w-full py-3 px-4 rounded-md font-medium text-center',
                exportOptions.selectedConversations.size > 0 && !isExporting
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              {isExporting ? (
                <div className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Exporting... {exportProgress}%
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export {exportStats.totalConversations} Conversation{exportStats.totalConversations !== 1 ? 's' : ''}
                </div>
              )}
            </button>

            {exportOptions.selectedConversations.size === 0 && (
              <p className="text-center text-sm text-gray-500 mt-2">
                Select at least one conversation to export
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
})

ConversationExport.displayName = 'ConversationExport'

export default ConversationExport