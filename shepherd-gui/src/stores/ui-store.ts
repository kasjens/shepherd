import { create } from 'zustand'
import { subscribeWithSelector, devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { shallow } from 'zustand/shallow'
import { Theme } from '@/lib/types'

export interface UIState {
  // Layout state
  sidebarCollapsed: boolean
  sidebarWidth: number
  
  // Modal state
  analyticsOpen: boolean
  artifactsOpen: boolean
  settingsOpen: boolean
  
  // Theme and appearance
  theme: Theme
  
  // Performance preferences
  reducedMotion: boolean
  enableAnimations: boolean
  
  // Notifications
  notifications: Notification[]
  
  // Loading states
  globalLoading: boolean
  loadingOperations: Set<string>
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  dismissed?: boolean
  autoRemove?: boolean
}

export interface UIActions {
  // Layout actions
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setSidebarWidth: (width: number) => void
  
  // Modal actions
  setAnalyticsOpen: (open: boolean) => void
  setArtifactsOpen: (open: boolean) => void
  setSettingsOpen: (open: boolean) => void
  closeAllModals: () => void
  
  // Theme actions
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
  
  // Performance actions
  setReducedMotion: (enabled: boolean) => void
  setEnableAnimations: (enabled: boolean) => void
  
  // Notification actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  dismissNotification: (id: string) => void
  clearAllNotifications: () => void
  
  // Loading actions
  setGlobalLoading: (loading: boolean) => void
  startOperation: (operationId: string) => void
  finishOperation: (operationId: string) => void
  isOperationLoading: (operationId: string) => boolean
}

export type UIStore = UIState & UIActions

const generateId = () => Math.random().toString(36).substr(2, 9)

export const useUIStore = create<UIStore>()(
  devtools(
    persist(
      immer(
        subscribeWithSelector((set, get) => ({
          // Initial state
          sidebarCollapsed: false,
          sidebarWidth: 280,
          analyticsOpen: false,
          artifactsOpen: false,
          settingsOpen: false,
          theme: 'light' as Theme,
          reducedMotion: false,
          enableAnimations: true,
          notifications: [],
          globalLoading: false,
          loadingOperations: new Set(),

          // Layout actions
          toggleSidebar: () =>
            set((state) => {
              state.sidebarCollapsed = !state.sidebarCollapsed
            }),

          setSidebarCollapsed: (collapsed) =>
            set((state) => {
              state.sidebarCollapsed = collapsed
            }),

          setSidebarWidth: (width) =>
            set((state) => {
              state.sidebarWidth = Math.max(200, Math.min(600, width))
            }),

          // Modal actions
          setAnalyticsOpen: (open) =>
            set((state) => {
              state.analyticsOpen = open
            }),

          setArtifactsOpen: (open) =>
            set((state) => {
              state.artifactsOpen = open
            }),

          setSettingsOpen: (open) =>
            set((state) => {
              state.settingsOpen = open
            }),

          closeAllModals: () =>
            set((state) => {
              state.analyticsOpen = false
              state.artifactsOpen = false
              state.settingsOpen = false
            }),

          // Theme actions
          setTheme: (theme) =>
            set((state) => {
              state.theme = theme
              
              // Apply theme to document
              if (typeof document !== 'undefined') {
                document.documentElement.className = 
                  theme === 'dark' ? 'dark' : 
                  theme === 'blue' ? 'theme-blue' : ''
              }
            }),

          toggleTheme: () => {
            const { theme } = get()
            const themes: Theme[] = ['light', 'dark', 'blue']
            const currentIndex = themes.indexOf(theme)
            const nextTheme = themes[(currentIndex + 1) % themes.length]
            get().setTheme(nextTheme)
          },

          // Performance actions
          setReducedMotion: (enabled) =>
            set((state) => {
              state.reducedMotion = enabled
              state.enableAnimations = !enabled
            }),

          setEnableAnimations: (enabled) =>
            set((state) => {
              state.enableAnimations = enabled
            }),

          // Notification actions
          addNotification: (notification) =>
            set((state) => {
              const newNotification: Notification = {
                ...notification,
                id: generateId(),
                timestamp: new Date(),
              }
              
              state.notifications.push(newNotification)
              
              // Auto-remove after 5 seconds if specified
              if (notification.autoRemove !== false) {
                setTimeout(() => {
                  get().removeNotification(newNotification.id)
                }, 5000)
              }
            }),

          removeNotification: (id) =>
            set((state) => {
              state.notifications = state.notifications.filter(n => n.id !== id)
            }),

          dismissNotification: (id) =>
            set((state) => {
              const notification = state.notifications.find(n => n.id === id)
              if (notification) {
                notification.dismissed = true
              }
            }),

          clearAllNotifications: () =>
            set((state) => {
              state.notifications = []
            }),

          // Loading actions
          setGlobalLoading: (loading) =>
            set((state) => {
              state.globalLoading = loading
            }),

          startOperation: (operationId) =>
            set((state) => {
              state.loadingOperations.add(operationId)
            }),

          finishOperation: (operationId) =>
            set((state) => {
              state.loadingOperations.delete(operationId)
            }),

          isOperationLoading: (operationId) => {
            return get().loadingOperations.has(operationId)
          },
        }))
      ),
      {
        name: 'shepherd-ui-store',
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          sidebarWidth: state.sidebarWidth,
          theme: state.theme,
          reducedMotion: state.reducedMotion,
          enableAnimations: state.enableAnimations,
        }),
      }
    ),
    {
      name: 'ui-store',
    }
  )
)

// Performance-optimized selectors
export const uiSelectors = {
  // Layout selectors
  layout: (state: UIStore) => ({
    sidebarCollapsed: state.sidebarCollapsed,
    sidebarWidth: state.sidebarWidth,
  }),
  
  // Modal selectors
  modals: (state: UIStore) => ({
    analyticsOpen: state.analyticsOpen,
    artifactsOpen: state.artifactsOpen,
    settingsOpen: state.settingsOpen,
  }),
  
  // Theme selectors
  theme: (state: UIStore) => ({
    theme: state.theme,
    reducedMotion: state.reducedMotion,
    enableAnimations: state.enableAnimations,
  }),
  
  // Loading selectors
  loading: (state: UIStore) => ({
    globalLoading: state.globalLoading,
    hasActiveOperations: state.loadingOperations.size > 0,
    activeOperationsCount: state.loadingOperations.size,
  }),
  
  // Notifications selector
  notifications: (state: UIStore) => 
    state.notifications.filter(n => !n.dismissed),
}

// Typed hooks for better DX
export const useUILayout = () => useUIStore(uiSelectors.layout, shallow)
export const useUIModals = () => useUIStore(uiSelectors.modals, shallow)
export const useUITheme = () => useUIStore(uiSelectors.theme, shallow)
export const useUILoading = () => useUIStore(uiSelectors.loading, shallow)
export const useUINotifications = () => useUIStore(uiSelectors.notifications, shallow)

// Initialize theme from system preferences
if (typeof window !== 'undefined') {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
  
  // Set initial theme if not already set
  const currentState = useUIStore.getState()
  if (currentState.theme === 'light' && mediaQuery.matches) {
    currentState.setTheme('dark')
  }
  
  // Set reduced motion preference
  if (prefersReducedMotion.matches) {
    currentState.setReducedMotion(true)
  }
  
  // Listen for changes
  mediaQuery.addEventListener('change', (e) => {
    if (e.matches) {
      useUIStore.getState().setTheme('dark')
    } else {
      useUIStore.getState().setTheme('light')
    }
  })
  
  prefersReducedMotion.addEventListener('change', (e) => {
    useUIStore.getState().setReducedMotion(e.matches)
  })
}