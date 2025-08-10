'use client'

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react'
import { X, Bell, CheckCircle, AlertTriangle, AlertCircle, Info, Zap, MessageSquare, User, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useWebSocket } from '@/hooks/use-websocket'

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'system' | 'message' | 'workflow' | 'agent'

export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Notification {
  id: string
  type: NotificationType
  priority: NotificationPriority
  title: string
  message: string
  timestamp: Date
  read: boolean
  persistent: boolean
  autoClose: boolean
  duration: number
  actions?: NotificationAction[]
  data?: any
}

export interface NotificationAction {
  id: string
  label: string
  action: (notification: Notification) => void
  style?: 'primary' | 'secondary' | 'danger'
}

interface NotificationState {
  notifications: Notification[]
  toasts: Notification[]
  unreadCount: number
  settings: {
    enableSound: boolean
    enableDesktop: boolean
    enableToasts: boolean
    defaultDuration: number
    maxToasts: number
  }
}

type NotificationAction_Type = 
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'MARK_READ'; payload: string }
  | { type: 'MARK_ALL_READ' }
  | { type: 'CLEAR_ALL' }
  | { type: 'ADD_TOAST'; payload: Notification }
  | { type: 'REMOVE_TOAST'; payload: string }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<NotificationState['settings']> }

const initialState: NotificationState = {
  notifications: [],
  toasts: [],
  unreadCount: 0,
  settings: {
    enableSound: true,
    enableDesktop: true,
    enableToasts: true,
    defaultDuration: 5000,
    maxToasts: 5
  }
}

function notificationReducer(state: NotificationState, action: NotificationAction_Type): NotificationState {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      const newNotification = action.payload
      return {
        ...state,
        notifications: [newNotification, ...state.notifications],
        unreadCount: state.unreadCount + 1
      }

    case 'REMOVE_NOTIFICATION':
      const filteredNotifications = state.notifications.filter(n => n.id !== action.payload)
      const removedNotification = state.notifications.find(n => n.id === action.payload)
      return {
        ...state,
        notifications: filteredNotifications,
        unreadCount: removedNotification && !removedNotification.read 
          ? state.unreadCount - 1 
          : state.unreadCount
      }

    case 'MARK_READ':
      const updatedNotifications = state.notifications.map(n =>
        n.id === action.payload ? { ...n, read: true } : n
      )
      const wasUnread = state.notifications.find(n => n.id === action.payload && !n.read)
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: wasUnread ? state.unreadCount - 1 : state.unreadCount
      }

    case 'MARK_ALL_READ':
      return {
        ...state,
        notifications: state.notifications.map(n => ({ ...n, read: true })),
        unreadCount: 0
      }

    case 'CLEAR_ALL':
      return {
        ...state,
        notifications: [],
        unreadCount: 0
      }

    case 'ADD_TOAST':
      const newToast = action.payload
      const toasts = [...state.toasts, newToast]
      
      // Limit number of toasts
      if (toasts.length > state.settings.maxToasts) {
        toasts.shift()
      }
      
      return {
        ...state,
        toasts
      }

    case 'REMOVE_TOAST':
      return {
        ...state,
        toasts: state.toasts.filter(t => t.id !== action.payload)
      }

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      }

    default:
      return state
  }
}

interface NotificationContextType {
  state: NotificationState
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => string
  removeNotification: (id: string) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  clearAll: () => void
  showToast: (type: NotificationType, title: string, message?: string, options?: Partial<Notification>) => string
  updateSettings: (settings: Partial<NotificationState['settings']>) => void
}

const NotificationContext = createContext<NotificationContextType | null>(null)

export function useNotifications(): NotificationContextType {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

interface NotificationProviderProps {
  children: React.ReactNode
  enableWebSocket?: boolean
  enableDesktopNotifications?: boolean
}

export function NotificationProvider({ 
  children, 
  enableWebSocket = true,
  enableDesktopNotifications = true
}: NotificationProviderProps) {
  const [state, dispatch] = useReducer(notificationReducer, initialState)

  // WebSocket integration for real-time notifications
  const ws = useWebSocket({
    autoConnect: enableWebSocket,
    onMessage: (message) => {
      if (message.type === 'notification') {
        addNotification(message.data)
      }
    }
  })

  // Request desktop notification permission
  useEffect(() => {
    if (enableDesktopNotifications && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [enableDesktopNotifications])

  const generateId = useCallback(() => {
    return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

  const addNotification = useCallback((
    notification: Omit<Notification, 'id' | 'timestamp' | 'read'>
  ): string => {
    const id = generateId()
    const defaults = {
      id,
      timestamp: new Date(),
      read: false,
      autoClose: true,
      duration: state.settings.defaultDuration,
      persistent: false
    }
    
    const fullNotification: Notification = {
      ...defaults,
      ...notification
    }

    dispatch({ type: 'ADD_NOTIFICATION', payload: fullNotification })

    // Show toast if enabled
    if (state.settings.enableToasts && !notification.persistent) {
      dispatch({ type: 'ADD_TOAST', payload: fullNotification })
      
      // Auto-remove toast
      if (fullNotification.autoClose) {
        setTimeout(() => {
          dispatch({ type: 'REMOVE_TOAST', payload: id })
        }, fullNotification.duration)
      }
    }

    // Show desktop notification if enabled and permitted
    if (state.settings.enableDesktop && 'Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: id
      })
    }

    // Play sound if enabled
    if (state.settings.enableSound && notification.priority !== 'low') {
      playNotificationSound(notification.type, notification.priority)
    }

    return id
  }, [generateId, state.settings])

  const removeNotification = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id })
  }, [])

  const markAsRead = useCallback((id: string) => {
    dispatch({ type: 'MARK_READ', payload: id })
  }, [])

  const markAllAsRead = useCallback(() => {
    dispatch({ type: 'MARK_ALL_READ' })
  }, [])

  const clearAll = useCallback(() => {
    dispatch({ type: 'CLEAR_ALL' })
  }, [])

  const showToast = useCallback((
    type: NotificationType, 
    title: string, 
    message: string = '', 
    options: Partial<Notification> = {}
  ): string => {
    const notification = {
      type,
      title,
      message,
      priority: 'medium' as const,
      persistent: false,
      autoClose: true,
      duration: state.settings.defaultDuration,
      ...options
    }
    
    return addNotification(notification)
  }, [addNotification])

  const updateSettings = useCallback((settings: Partial<NotificationState['settings']>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings })
  }, [])

  // Subscribe to WebSocket events for real-time notifications
  useEffect(() => {
    if (!enableWebSocket || !ws.isConnected) return

    const subscriptions = [
      ws.subscribe('workflow:started', (data) => {
        showToast('workflow', 'Workflow Started', `${data.workflowName} has started execution`, { 
          priority: 'medium',
          data 
        })
      }),

      ws.subscribe('workflow:completed', (data) => {
        showToast('success', 'Workflow Completed', `${data.workflowName} completed successfully`, { 
          priority: 'medium',
          data
        })
      }),

      ws.subscribe('workflow:failed', (data) => {
        showToast('error', 'Workflow Failed', `${data.workflowName} failed: ${data.error}`, {
          priority: 'high',
          persistent: true,
          data
        })
      }),

      ws.subscribe('agent:status_change', (data) => {
        showToast('agent', 'Agent Status Update', `${data.agentName} is now ${data.status}`, {
          priority: 'low',
          data
        })
      }),

      ws.subscribe('system:error', (data) => {
        showToast('error', 'System Error', data.message || 'An unexpected error occurred', {
          priority: 'urgent',
          persistent: true,
          data
        })
      }),

      ws.subscribe('message:received', (data) => {
        if (data.userId !== 'current_user') { // Don't notify for own messages
          showToast('message', 'New Message', `${data.senderName}: ${data.preview}`, {
            priority: 'medium',
            data
          })
        }
      })
    ]

    return () => {
      subscriptions.forEach(unsubscribe => unsubscribe())
    }
  }, [ws, enableWebSocket, addNotification])

  const value: NotificationContextType = {
    state,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    showToast,
    updateSettings
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <ToastContainer />
    </NotificationContext.Provider>
  )
}

// Toast Container Component
function ToastContainer() {
  const { state, markAsRead } = useNotifications()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {state.toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          notification={toast}
          onClose={() => markAsRead(toast.id)}
        />
      ))}
    </div>
  )
}

// Individual Toast Notification Component
function ToastNotification({ 
  notification, 
  onClose 
}: { 
  notification: Notification
  onClose: () => void 
}) {
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />
      case 'system':
        return <Settings className="w-5 h-5 text-gray-500" />
      case 'message':
        return <MessageSquare className="w-5 h-5 text-purple-500" />
      case 'workflow':
        return <Zap className="w-5 h-5 text-orange-500" />
      case 'agent':
        return <User className="w-5 h-5 text-indigo-500" />
      default:
        return <Bell className="w-5 h-5 text-gray-500" />
    }
  }

  const getPriorityStyles = () => {
    switch (notification.priority) {
      case 'urgent':
        return 'border-l-4 border-l-red-500 bg-red-50 dark:bg-red-950'
      case 'high':
        return 'border-l-4 border-l-orange-500 bg-orange-50 dark:bg-orange-950'
      case 'medium':
        return 'border-l-4 border-l-blue-500 bg-blue-50 dark:bg-blue-950'
      case 'low':
        return 'border-l-4 border-l-gray-500 bg-gray-50 dark:bg-gray-950'
      default:
        return 'border-l-4 border-l-gray-500 bg-white dark:bg-gray-900'
    }
  }

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg shadow-lg max-w-sm',
        'transform transition-all duration-300 ease-in-out',
        'animate-in slide-in-from-right',
        getPriorityStyles()
      )}
    >
      <div className="flex-shrink-0">
        {getIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
          {notification.title}
        </div>
        
        {notification.message && (
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {notification.message}
          </div>
        )}
        
        {notification.actions && notification.actions.length > 0 && (
          <div className="flex gap-2 mt-2">
            {notification.actions.map((action) => (
              <button
                key={action.id}
                onClick={() => action.action(notification)}
                className={cn(
                  'px-2 py-1 text-xs rounded',
                  action.style === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
                  action.style === 'danger' && 'bg-red-600 text-white hover:bg-red-700',
                  action.style === 'secondary' && 'bg-gray-600 text-white hover:bg-gray-700',
                  !action.style && 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                )}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
        
        <div className="text-xs text-gray-500 mt-1">
          {notification.timestamp.toLocaleTimeString()}
        </div>
      </div>
      
      <button
        onClick={onClose}
        className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

// Utility function to play notification sounds
function playNotificationSound(type: NotificationType, priority: NotificationPriority) {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    
    // Create different tones based on type and priority
    const frequency = {
      success: 800,
      error: 300,
      warning: 600,
      info: 500,
      system: 400,
      message: 700,
      workflow: 550,
      agent: 450
    }[type]

    const duration = priority === 'urgent' ? 300 : priority === 'high' ? 200 : 150

    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime)
    oscillator.type = 'sine'

    gainNode.gain.setValueAtTime(0, audioContext.currentTime)
    gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01)
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + duration / 1000)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + duration / 1000)
  } catch (error) {
    console.warn('Could not play notification sound:', error)
  }
}