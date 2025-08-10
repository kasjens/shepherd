'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { User, Circle, MessageCircle, Edit3, MousePointer, Eye, Wifi, WifiOff } from 'lucide-react'
import { cn } from '@/lib/utils'
import { usePresence } from '@/hooks/use-websocket'

export interface UserPresence {
  userId: string
  displayName: string
  avatar?: string
  email?: string
  role?: string
  status: 'online' | 'away' | 'busy' | 'offline'
  lastSeen: Date
  currentPage?: string
  currentSection?: string
  cursor?: {
    x: number
    y: number
    elementId?: string
  }
  isTyping?: boolean
  typingIn?: string
  customStatus?: string
}

export interface CollaborationState {
  currentUser: UserPresence | null
  onlineUsers: Map<string, UserPresence>
  cursors: Map<string, UserPresence['cursor']>
  typingUsers: Set<string>
  isConnected: boolean
}

interface CollaborationContextType {
  state: CollaborationState
  updatePresence: (updates: Partial<UserPresence>) => void
  updateCursor: (position: { x: number; y: number; elementId?: string }) => void
  setTyping: (isTyping: boolean, elementId?: string) => void
  updateCurrentSection: (section: string) => void
  setStatus: (status: UserPresence['status'], customMessage?: string) => void
}

const CollaborationContext = createContext<CollaborationContextType | null>(null)

export function useCollaboration(): CollaborationContextType {
  const context = useContext(CollaborationContext)
  if (!context) {
    throw new Error('useCollaboration must be used within a CollaborationProvider')
  }
  return context
}

interface CollaborationProviderProps {
  children: React.ReactNode
  currentUser: {
    userId: string
    displayName: string
    avatar?: string
    email?: string
    role?: string
  }
  enabled?: boolean
}

export function CollaborationProvider({ 
  children, 
  currentUser,
  enabled = true
}: CollaborationProviderProps) {
  const [cursors, setCursors] = useState<Map<string, UserPresence['cursor']>>(new Map())
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set())
  const [currentSection, setCurrentSection] = useState<string>('/')

  // Initialize presence with WebSocket
  const ws = usePresence(
    currentUser.userId,
    {
      displayName: currentUser.displayName,
      avatar: currentUser.avatar,
      email: currentUser.email,
      role: currentUser.role,
      status: 'online',
      lastSeen: new Date(),
      currentPage: window?.location?.pathname || '/'
    },
    { autoConnect: enabled }
  )

  // Transform online users to our format
  const onlineUsers = new Map<string, UserPresence>()
  ws.onlineUsers.forEach((user, userId) => {
    if (userId !== currentUser.userId) {
      onlineUsers.set(userId, {
        userId,
        displayName: user.displayName || 'Unknown User',
        avatar: user.avatar,
        email: user.email,
        role: user.role,
        status: user.status || 'online',
        lastSeen: new Date(user.lastSeen || Date.now()),
        currentPage: user.currentPage,
        currentSection: user.currentSection,
        cursor: user.cursor,
        isTyping: user.isTyping,
        typingIn: user.typingIn,
        customStatus: user.customStatus
      })
    }
  })

  const currentUserPresence: UserPresence = {
    userId: currentUser.userId,
    displayName: currentUser.displayName,
    avatar: currentUser.avatar,
    email: currentUser.email,
    role: currentUser.role,
    status: ws.isConnected ? 'online' : 'offline',
    lastSeen: new Date(),
    currentPage: window?.location?.pathname || '/',
    currentSection
  }

  const state: CollaborationState = {
    currentUser: currentUserPresence,
    onlineUsers,
    cursors,
    typingUsers,
    isConnected: ws.isConnected
  }

  // Subscribe to cursor movements
  useEffect(() => {
    if (!ws.isConnected) return

    const unsubscribeCursor = ws.subscribe('presence:cursor_move', (data) => {
      if (data.userId !== currentUser.userId) {
        setCursors(prev => new Map(prev.set(data.userId, data.cursor)))
      }
    })

    const unsubscribeTyping = ws.subscribe('presence:typing', (data) => {
      if (data.userId !== currentUser.userId) {
        setTypingUsers(prev => {
          const next = new Set(prev)
          if (data.isTyping) {
            next.add(data.userId)
          } else {
            next.delete(data.userId)
          }
          return next
        })
      }
    })

    return () => {
      unsubscribeCursor()
      unsubscribeTyping()
    }
  }, [ws, currentUser.userId])

  const updatePresence = useCallback((updates: Partial<UserPresence>) => {
    ws.updatePresence(updates)
  }, [ws])

  const updateCursor = useCallback((position: { x: number; y: number; elementId?: string }) => {
    ws.send('presence:cursor_move', {
      userId: currentUser.userId,
      cursor: position
    }).catch(console.error)
  }, [ws, currentUser.userId])

  const setTyping = useCallback((isTyping: boolean, elementId?: string) => {
    ws.send('presence:typing', {
      userId: currentUser.userId,
      isTyping,
      typingIn: elementId
    }).catch(console.error)
  }, [ws, currentUser.userId])

  const updateCurrentSection = useCallback((section: string) => {
    setCurrentSection(section)
    updatePresence({ currentSection: section })
  }, [updatePresence])

  const setStatus = useCallback((status: UserPresence['status'], customMessage?: string) => {
    updatePresence({ 
      status, 
      customStatus: customMessage,
      lastSeen: new Date()
    })
  }, [updatePresence])

  // Track mouse movements for cursor sharing
  useEffect(() => {
    if (!enabled || !ws.isConnected) return

    let throttleTimeout: NodeJS.Timeout
    
    const handleMouseMove = (e: MouseEvent) => {
      clearTimeout(throttleTimeout)
      throttleTimeout = setTimeout(() => {
        const elementUnderCursor = document.elementFromPoint(e.clientX, e.clientY)
        updateCursor({
          x: e.clientX,
          y: e.clientY,
          elementId: elementUnderCursor?.id
        })
      }, 100) // Throttle cursor updates
    }

    document.addEventListener('mousemove', handleMouseMove)
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      clearTimeout(throttleTimeout)
    }
  }, [enabled, ws.isConnected, updateCursor])

  // Update presence on page/section changes
  useEffect(() => {
    updatePresence({ 
      currentPage: window.location.pathname,
      lastSeen: new Date()
    })
  }, [updatePresence])

  const value: CollaborationContextType = {
    state,
    updatePresence,
    updateCursor,
    setTyping,
    updateCurrentSection,
    setStatus
  }

  return (
    <CollaborationContext.Provider value={value}>
      {children}
      <CursorOverlay />
      <TypingIndicators />
    </CollaborationContext.Provider>
  )
}

// Cursor Overlay Component
function CursorOverlay() {
  const { state } = useCollaboration()

  if (!state.isConnected) return null

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {Array.from(state.cursors.entries()).map(([userId, cursor]) => {
        const user = state.onlineUsers.get(userId)
        if (!cursor || !user) return null

        return (
          <div
            key={userId}
            className="absolute pointer-events-none transform transition-all duration-100"
            style={{
              left: cursor.x,
              top: cursor.y,
              transform: 'translate(-2px, -2px)'
            }}
          >
            <MousePointer 
              className="w-4 h-4 text-blue-500 drop-shadow-sm"
              style={{ color: getUserColor(userId) }}
            />
            <div 
              className="ml-4 -mt-1 px-2 py-1 bg-black/80 text-white text-xs rounded whitespace-nowrap"
              style={{ backgroundColor: getUserColor(userId) }}
            >
              {user.displayName}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Typing Indicators Component
function TypingIndicators() {
  const { state } = useCollaboration()

  if (!state.isConnected || state.typingUsers.size === 0) return null

  const typingUsersList = Array.from(state.typingUsers)
    .map(userId => state.onlineUsers.get(userId))
    .filter(Boolean)

  if (typingUsersList.length === 0) return null

  return (
    <div className="fixed bottom-4 left-4 z-40">
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3 max-w-sm">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {typingUsersList.length === 1 
              ? `${typingUsersList[0]!.displayName} is typing...`
              : typingUsersList.length === 2
              ? `${typingUsersList[0]!.displayName} and ${typingUsersList[1]!.displayName} are typing...`
              : `${typingUsersList[0]!.displayName} and ${typingUsersList.length - 1} others are typing...`
            }
          </div>
        </div>
      </div>
    </div>
  )
}

// User Avatar Component
interface UserAvatarProps {
  user: UserPresence
  size?: 'sm' | 'md' | 'lg'
  showStatus?: boolean
  className?: string
}

export function UserAvatar({ user, size = 'md', showStatus = true, className }: UserAvatarProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base'
  }

  const statusColors = {
    online: 'bg-green-500',
    away: 'bg-yellow-500',
    busy: 'bg-red-500',
    offline: 'bg-gray-500'
  }

  return (
    <div className={cn('relative', className)}>
      {user.avatar ? (
        <img
          src={user.avatar}
          alt={user.displayName}
          className={cn('rounded-full object-cover', sizeClasses[size])}
        />
      ) : (
        <div 
          className={cn(
            'rounded-full flex items-center justify-center font-medium text-white',
            sizeClasses[size]
          )}
          style={{ backgroundColor: getUserColor(user.userId) }}
        >
          {user.displayName.charAt(0).toUpperCase()}
        </div>
      )}
      
      {showStatus && (
        <div className={cn(
          'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800',
          statusColors[user.status]
        )} />
      )}
    </div>
  )
}

// Online Users List Component
interface OnlineUsersListProps {
  maxVisible?: number
  showSelf?: boolean
  className?: string
}

export function OnlineUsersList({ maxVisible = 5, showSelf = false, className }: OnlineUsersListProps) {
  const { state } = useCollaboration()

  const users = Array.from(state.onlineUsers.values())
  if (showSelf && state.currentUser) {
    users.unshift(state.currentUser)
  }

  const visibleUsers = users.slice(0, maxVisible)
  const hiddenCount = users.length - maxVisible

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex items-center -space-x-2">
        {visibleUsers.map((user) => (
          <div
            key={user.userId}
            className="relative group"
            title={`${user.displayName} (${user.status})`}
          >
            <UserAvatar user={user} size="md" />
          </div>
        ))}
        
        {hiddenCount > 0 && (
          <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-400">
            +{hiddenCount}
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-1 text-sm text-gray-500">
        {state.isConnected ? (
          <Wifi className="w-4 h-4 text-green-500" />
        ) : (
          <WifiOff className="w-4 h-4 text-red-500" />
        )}
        <span>{users.length} online</span>
      </div>
    </div>
  )
}

// Connection Status Component
export function ConnectionStatus() {
  const { state } = useCollaboration()

  return (
    <div className={cn(
      'flex items-center gap-2 px-3 py-1 rounded-full text-sm',
      state.isConnected 
        ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
        : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
    )}>
      {state.isConnected ? (
        <>
          <Circle className="w-2 h-2 fill-current" />
          <span>Connected</span>
        </>
      ) : (
        <>
          <Circle className="w-2 h-2 fill-current animate-pulse" />
          <span>Connecting...</span>
        </>
      )}
    </div>
  )
}

// Utility function to generate consistent colors for users
function getUserColor(userId: string): string {
  const colors = [
    '#3B82F6', // Blue
    '#EF4444', // Red
    '#10B981', // Green
    '#F59E0B', // Yellow
    '#8B5CF6', // Purple
    '#06B6D4', // Cyan
    '#EC4899', // Pink
    '#84CC16', // Lime
    '#F97316', // Orange
    '#6366F1', // Indigo
  ]
  
  let hash = 0
  for (let i = 0; i < userId.length; i++) {
    hash = userId.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  return colors[Math.abs(hash) % colors.length]
}