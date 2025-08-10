import { act, renderHook } from '@testing-library/react'
import { useUIStore, uiSelectors, type UIStore } from '@/stores/ui-store'

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
})

// Mock document
Object.defineProperty(document, 'documentElement', {
  value: { className: '' },
  writable: true,
})

describe('UI Store', () => {
  beforeEach(() => {
    // Reset store state
    useUIStore.getState().setSidebarCollapsed(false)
    useUIStore.getState().setTheme('light')
    useUIStore.getState().closeAllModals()
    useUIStore.getState().clearAllNotifications()
    jest.clearAllMocks()
  })

  describe('Layout State', () => {
    test('toggles sidebar correctly', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.sidebarCollapsed).toBe(false)
      
      act(() => {
        result.current.toggleSidebar()
      })
      
      expect(result.current.sidebarCollapsed).toBe(true)
      
      act(() => {
        result.current.toggleSidebar()
      })
      
      expect(result.current.sidebarCollapsed).toBe(false)
    })

    test('sets sidebar width with constraints', () => {
      const { result } = renderHook(() => useUIStore())
      
      // Test normal width
      act(() => {
        result.current.setSidebarWidth(320)
      })
      expect(result.current.sidebarWidth).toBe(320)
      
      // Test minimum constraint
      act(() => {
        result.current.setSidebarWidth(100)
      })
      expect(result.current.sidebarWidth).toBe(200)
      
      // Test maximum constraint
      act(() => {
        result.current.setSidebarWidth(800)
      })
      expect(result.current.sidebarWidth).toBe(600)
    })
  })

  describe('Modal State', () => {
    test('manages individual modals', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.analyticsOpen).toBe(false)
      expect(result.current.artifactsOpen).toBe(false)
      expect(result.current.settingsOpen).toBe(false)
      
      act(() => {
        result.current.setAnalyticsOpen(true)
      })
      expect(result.current.analyticsOpen).toBe(true)
      
      act(() => {
        result.current.setArtifactsOpen(true)
      })
      expect(result.current.artifactsOpen).toBe(true)
      
      act(() => {
        result.current.closeAllModals()
      })
      expect(result.current.analyticsOpen).toBe(false)
      expect(result.current.artifactsOpen).toBe(false)
      expect(result.current.settingsOpen).toBe(false)
    })
  })

  describe('Theme Management', () => {
    test('sets theme and updates document class', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.setTheme('dark')
      })
      expect(result.current.theme).toBe('dark')
      expect(document.documentElement.className).toBe('dark')
      
      act(() => {
        result.current.setTheme('blue')
      })
      expect(result.current.theme).toBe('blue')
      expect(document.documentElement.className).toBe('theme-blue')
      
      act(() => {
        result.current.setTheme('light')
      })
      expect(result.current.theme).toBe('light')
      expect(document.documentElement.className).toBe('')
    })

    test('toggles through themes correctly', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.theme).toBe('light')
      
      act(() => {
        result.current.toggleTheme()
      })
      expect(result.current.theme).toBe('dark')
      
      act(() => {
        result.current.toggleTheme()
      })
      expect(result.current.theme).toBe('blue')
      
      act(() => {
        result.current.toggleTheme()
      })
      expect(result.current.theme).toBe('light')
    })
  })

  describe('Notification Management', () => {
    test('adds and manages notifications', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.addNotification({
          type: 'info',
          title: 'Test',
          message: 'Test message',
        })
      })
      
      expect(result.current.notifications).toHaveLength(1)
      expect(result.current.notifications[0].type).toBe('info')
      expect(result.current.notifications[0].title).toBe('Test')
      
      const notificationId = result.current.notifications[0].id
      
      act(() => {
        result.current.dismissNotification(notificationId)
      })
      
      expect(result.current.notifications[0].dismissed).toBe(true)
      
      act(() => {
        result.current.clearAllNotifications()
      })
      
      expect(result.current.notifications).toHaveLength(0)
    })

    test('auto-removes notifications by default', (done) => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.addNotification({
          type: 'success',
          title: 'Auto Remove',
          message: 'This should be removed automatically',
        })
      })
      
      expect(result.current.notifications).toHaveLength(1)
      
      // Check that it gets removed after timeout
      setTimeout(() => {
        expect(result.current.notifications).toHaveLength(0)
        done()
      }, 5100) // Slightly more than the 5s timeout
    })

    test('respects autoRemove false flag', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.addNotification({
          type: 'error',
          title: 'Persistent',
          message: 'This should not be auto-removed',
          autoRemove: false,
        })
      })
      
      expect(result.current.notifications).toHaveLength(1)
      
      // Should still be there after a short wait
      setTimeout(() => {
        expect(result.current.notifications).toHaveLength(1)
      }, 100)
    })
  })

  describe('Loading Operations', () => {
    test('manages global loading state', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.globalLoading).toBe(false)
      
      act(() => {
        result.current.setGlobalLoading(true)
      })
      
      expect(result.current.globalLoading).toBe(true)
      
      act(() => {
        result.current.setGlobalLoading(false)
      })
      
      expect(result.current.globalLoading).toBe(false)
    })

    test('tracks individual operations', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.isOperationLoading('test-op')).toBe(false)
      
      act(() => {
        result.current.startOperation('test-op')
      })
      
      expect(result.current.isOperationLoading('test-op')).toBe(true)
      expect(result.current.loadingOperations.has('test-op')).toBe(true)
      
      act(() => {
        result.current.finishOperation('test-op')
      })
      
      expect(result.current.isOperationLoading('test-op')).toBe(false)
      expect(result.current.loadingOperations.has('test-op')).toBe(false)
    })

    test('handles multiple concurrent operations', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.startOperation('op1')
        result.current.startOperation('op2')
        result.current.startOperation('op3')
      })
      
      expect(result.current.loadingOperations.size).toBe(3)
      expect(result.current.isOperationLoading('op1')).toBe(true)
      expect(result.current.isOperationLoading('op2')).toBe(true)
      expect(result.current.isOperationLoading('op3')).toBe(true)
      
      act(() => {
        result.current.finishOperation('op2')
      })
      
      expect(result.current.loadingOperations.size).toBe(2)
      expect(result.current.isOperationLoading('op1')).toBe(true)
      expect(result.current.isOperationLoading('op2')).toBe(false)
      expect(result.current.isOperationLoading('op3')).toBe(true)
    })
  })

  describe('Selectors', () => {
    test('layout selector returns correct data', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.setSidebarCollapsed(true)
        result.current.setSidebarWidth(400)
      })
      
      const layout = uiSelectors.layout(result.current)
      
      expect(layout).toEqual({
        sidebarCollapsed: true,
        sidebarWidth: 400,
      })
    })

    test('modals selector calculates hasOpenModals', () => {
      const { result } = renderHook(() => useUIStore())
      
      let modals = uiSelectors.modals(result.current)
      expect(modals.hasOpenModals).toBe(false)
      
      act(() => {
        result.current.setAnalyticsOpen(true)
      })
      
      modals = uiSelectors.modals(result.current)
      expect(modals.hasOpenModals).toBe(true)
    })

    test('notifications selector filters and counts correctly', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.addNotification({
          type: 'error',
          title: 'Error',
          message: 'Error message',
          autoRemove: false,
        })
        result.current.addNotification({
          type: 'warning',
          title: 'Warning',
          message: 'Warning message',
          autoRemove: false,
        })
        result.current.addNotification({
          type: 'info',
          title: 'Info',
          message: 'Info message',
          autoRemove: false,
        })
      })
      
      const notifications = uiSelectors.notifications(result.current)
      
      expect(notifications.totalCount).toBe(3)
      expect(notifications.errorCount).toBe(1)
      expect(notifications.warningCount).toBe(1)
      expect(notifications.hasErrors).toBe(true)
      expect(notifications.hasWarnings).toBe(true)
    })
  })

  describe('Persistence', () => {
    test('persists correct state properties', () => {
      const { result } = renderHook(() => useUIStore())
      
      act(() => {
        result.current.setSidebarCollapsed(true)
        result.current.setSidebarWidth(350)
        result.current.setTheme('dark')
        result.current.setReducedMotion(true)
      })
      
      // The persistence is handled by zustand middleware
      // We can verify the state is correct for persistence
      expect(result.current.sidebarCollapsed).toBe(true)
      expect(result.current.sidebarWidth).toBe(350)
      expect(result.current.theme).toBe('dark')
      expect(result.current.reducedMotion).toBe(true)
      expect(result.current.enableAnimations).toBe(false)
    })
  })

  describe('Performance Preferences', () => {
    test('manages reduced motion preference', () => {
      const { result } = renderHook(() => useUIStore())
      
      expect(result.current.reducedMotion).toBe(false)
      expect(result.current.enableAnimations).toBe(true)
      
      act(() => {
        result.current.setReducedMotion(true)
      })
      
      expect(result.current.reducedMotion).toBe(true)
      expect(result.current.enableAnimations).toBe(false)
      
      act(() => {
        result.current.setReducedMotion(false)
      })
      
      expect(result.current.reducedMotion).toBe(false)
      // enableAnimations should remain false as it was set separately
      expect(result.current.enableAnimations).toBe(false)
      
      act(() => {
        result.current.setEnableAnimations(true)
      })
      
      expect(result.current.enableAnimations).toBe(true)
    })
  })
})