'use client'

import React, { memo, useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { FixedSizeList as List, ListChildComponentProps } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'
import { Search, MessageCircle, Clock, Archive, Trash2, Pin } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'
import { debounce } from '@/lib/performance'

export interface Conversation {
  id: string
  title: string
  preview: string
  timestamp: Date
  messageCount: number
  status: 'active' | 'archived' | 'pinned'
  tags?: string[]
  lastAgent?: string
  unreadCount?: number
}

export interface ConversationListProps {
  conversations: Conversation[]
  selectedId?: string
  isLoading?: boolean
  onSelect?: (conversation: Conversation) => void
  onArchive?: (id: string) => void
  onDelete?: (id: string) => void
  onPin?: (id: string) => void
  onSearch?: (query: string) => void
  className?: string
}

const ITEM_HEIGHT = 80
const SEARCH_DEBOUNCE = 300

const ConversationItem = memo<ListChildComponentProps<{
  filteredConversations: Conversation[]
  selectedId?: string
  onSelect?: (conversation: Conversation) => void
  onArchive?: (id: string) => void
  onDelete?: (id: string) => void
  onPin?: (id: string) => void
}>>(({ index, style, data }) => {
  const { filteredConversations, selectedId, onSelect, onArchive, onDelete, onPin } = data
  const conversation = filteredConversations[index]
  const { reducedMotion, theme } = useUIStore(state => ({
    reducedMotion: state.reducedMotion,
    theme: state.theme
  }))

  const [isHovered, setIsHovered] = useState(false)
  const isSelected = conversation.id === selectedId

  const handleSelect = useCallback(() => {
    onSelect?.(conversation)
  }, [onSelect, conversation])

  const handleArchive = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onArchive?.(conversation.id)
  }, [onArchive, conversation.id])

  const handleDelete = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.(conversation.id)
  }, [onDelete, conversation.id])

  const handlePin = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onPin?.(conversation.id)
  }, [onPin, conversation.id])

  const formatTimestamp = useCallback((date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }, [])

  return (
    <div
      style={style}
      className={cn(
        'px-3 py-2 cursor-pointer select-none',
        !reducedMotion && 'transition-all duration-200'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleSelect}
    >
      <div className={cn(
        'relative p-3 rounded-lg border',
        'bg-white dark:bg-gray-900',
        isSelected 
          ? 'border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-950' 
          : 'border-gray-200 dark:border-gray-700',
        isHovered && !isSelected && 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-850',
        !reducedMotion && 'transition-colors duration-200'
      )}>
        {/* Status Indicators */}
        <div className="absolute top-2 right-2 flex items-center gap-1">
          {conversation.status === 'pinned' && (
            <Pin className="w-3 h-3 text-orange-500" fill="currentColor" />
          )}
          {conversation.unreadCount && conversation.unreadCount > 0 && (
            <div className="w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {conversation.unreadCount > 9 ? '9+' : conversation.unreadCount}
            </div>
          )}
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-2 pr-8">
          <h3 className={cn(
            'font-medium text-sm line-clamp-1',
            isSelected 
              ? 'text-blue-900 dark:text-blue-100' 
              : 'text-gray-900 dark:text-gray-100'
          )}>
            {conversation.title || 'Untitled Conversation'}
          </h3>
        </div>

        {/* Preview */}
        <p className={cn(
          'text-xs mb-2 line-clamp-2',
          isSelected 
            ? 'text-blue-700 dark:text-blue-300' 
            : 'text-gray-600 dark:text-gray-400'
        )}>
          {conversation.preview || 'No messages yet'}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <div className={cn(
              'flex items-center gap-1',
              isSelected 
                ? 'text-blue-600 dark:text-blue-400' 
                : 'text-gray-500 dark:text-gray-500'
            )}>
              <Clock className="w-3 h-3" />
              <span>{formatTimestamp(conversation.timestamp)}</span>
            </div>
            
            <div className={cn(
              'flex items-center gap-1',
              isSelected 
                ? 'text-blue-600 dark:text-blue-400' 
                : 'text-gray-500 dark:text-gray-500'
            )}>
              <MessageCircle className="w-3 h-3" />
              <span>{conversation.messageCount}</span>
            </div>

            {conversation.lastAgent && (
              <div className={cn(
                'px-2 py-0.5 rounded text-xs',
                'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              )}>
                {conversation.lastAgent}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {isHovered && (
            <div className="flex items-center gap-1">
              <button
                onClick={handlePin}
                className={cn(
                  'p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200',
                  conversation.status === 'pinned' 
                    ? 'text-orange-500' 
                    : 'text-gray-400 hover:text-gray-600'
                )}
                title={conversation.status === 'pinned' ? 'Unpin' : 'Pin'}
              >
                <Pin className="w-3 h-3" fill={conversation.status === 'pinned' ? 'currentColor' : 'none'} />
              </button>
              
              <button
                onClick={handleArchive}
                className={cn(
                  'p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300',
                  'hover:bg-gray-200 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
                title="Archive"
              >
                <Archive className="w-3 h-3" />
              </button>
              
              <button
                onClick={handleDelete}
                className={cn(
                  'p-1 rounded text-gray-400 hover:text-red-500',
                  'hover:bg-red-50 dark:hover:bg-red-950',
                  !reducedMotion && 'transition-colors duration-200'
                )}
                title="Delete"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        {/* Tags */}
        {conversation.tags && conversation.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {conversation.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className={cn(
                  'px-1.5 py-0.5 rounded text-xs',
                  'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                )}
              >
                {tag}
              </span>
            ))}
            {conversation.tags.length > 3 && (
              <span className="text-xs text-gray-500">
                +{conversation.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
})

ConversationItem.displayName = 'ConversationItem'

const ConversationList = memo<ConversationListProps>(({
  conversations,
  selectedId,
  isLoading = false,
  onSelect,
  onArchive,
  onDelete,
  onPin,
  onSearch,
  className
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const { reducedMotion } = useUIStore(state => ({ reducedMotion: state.reducedMotion }))
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Debounced search handler
  const debouncedSearch = useMemo(
    () => debounce((query: string) => {
      onSearch?.(query)
    }, SEARCH_DEBOUNCE),
    [onSearch]
  )

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    debouncedSearch(query)
  }, [debouncedSearch])

  const handleSearchClear = useCallback(() => {
    setSearchQuery('')
    onSearch?.('')
    searchInputRef.current?.focus()
  }, [onSearch])

  // Filter and sort conversations
  const filteredConversations = useMemo(() => {
    let filtered = conversations

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(conv => 
        conv.title.toLowerCase().includes(query) ||
        conv.preview.toLowerCase().includes(query) ||
        conv.tags?.some(tag => tag.toLowerCase().includes(query)) ||
        conv.lastAgent?.toLowerCase().includes(query)
      )
    }

    // Sort by pinned first, then by timestamp
    return filtered.sort((a, b) => {
      if (a.status === 'pinned' && b.status !== 'pinned') return -1
      if (a.status !== 'pinned' && b.status === 'pinned') return 1
      return b.timestamp.getTime() - a.timestamp.getTime()
    })
  }, [conversations, searchQuery])

  const itemData = useMemo(() => ({
    filteredConversations,
    selectedId,
    onSelect,
    onArchive,
    onDelete,
    onPin
  }), [filteredConversations, selectedId, onSelect, onArchive, onDelete, onPin])

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Search Header */}
      <div className="p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search conversations..."
            className={cn(
              'w-full pl-10 pr-10 py-2 text-sm',
              'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600',
              'rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              'placeholder:text-gray-400',
              !reducedMotion && 'transition-colors duration-200'
            )}
          />
          {searchQuery && (
            <button
              onClick={handleSearchClear}
              className={cn(
                'absolute right-2 top-1/2 -translate-y-1/2 p-1',
                'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300',
                'rounded-full hover:bg-gray-100 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              ×
            </button>
          )}
        </div>
        
        {/* Results Count */}
        {searchQuery && (
          <div className="mt-2 text-xs text-gray-500">
            {filteredConversations.length} conversation{filteredConversations.length !== 1 ? 's' : ''} found
          </div>
        )}
      </div>

      {/* Conversation List */}
      <div className="flex-1">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="flex items-center gap-2 text-gray-500">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
              <span className="text-sm">Loading conversations...</span>
            </div>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <MessageCircle className="w-8 h-8 mb-2 opacity-50" />
            <span className="text-sm">
              {searchQuery ? 'No conversations match your search' : 'No conversations yet'}
            </span>
            {searchQuery && (
              <button
                onClick={handleSearchClear}
                className="mt-2 text-xs text-blue-500 hover:text-blue-600"
              >
                Clear search
              </button>
            )}
          </div>
        ) : (
          <AutoSizer>
            {({ height, width }) => (
              <List
                height={height}
                width={width}
                itemCount={filteredConversations.length}
                itemSize={ITEM_HEIGHT}
                itemData={itemData}
                overscanCount={5}
              >
                {ConversationItem}
              </List>
            )}
          </AutoSizer>
        )}
      </div>
    </div>
  )
})

ConversationList.displayName = 'ConversationList'

export default ConversationList