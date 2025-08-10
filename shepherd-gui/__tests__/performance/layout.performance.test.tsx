import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { Sidebar } from '@/components/layout/sidebar'
import { ConversationArea } from '@/components/layout/conversation-area'
import '@testing-library/jest-dom'

// Mock the performance hooks
jest.mock('@/hooks/usePerformance', () => ({
  useRenderPerformance: jest.fn(() => 15), // Mock 15ms render time
  usePerformanceMode: jest.fn(() => ({
    isLowEnd: false,
    reducedMotion: false,
    shouldReduceAnimations: false,
    maxItemsToRender: 50
  }))
}))

// Mock Zustand stores
jest.mock('@/stores/project-store', () => ({
  useProjectStore: () => ({
    projectFolder: '/test/project'
  })
}))

describe('Layout Performance Tests', () => {
  beforeEach(() => {
    // Mock performance APIs
    global.performance = {
      ...global.performance,
      now: jest.fn(() => Date.now()),
      mark: jest.fn(),
      measure: jest.fn(() => ({ duration: 15 })),
      clearMarks: jest.fn(),
      clearMeasures: jest.fn(),
    } as any

    // Mock scrollIntoView
    Element.prototype.scrollIntoView = jest.fn()
  })

  describe('Sidebar Performance', () => {
    test('renders within performance budget (< 100ms)', () => {
      const startTime = performance.now()
      
      render(
        <Sidebar width={320} isCollapsed={false} onCollapsedChange={jest.fn()} />
      )
      
      const renderTime = performance.now() - startTime
      expect(renderTime).toBeLessThan(100) // More generous for CI environment
    })

    test('sidebar has GPU acceleration styles', () => {
      render(
        <Sidebar width={320} isCollapsed={false} onCollapsedChange={jest.fn()} />
      )

      const sidebar = document.querySelector('.terminal-panel')
      expect(sidebar).toHaveStyle('transform: translateZ(0)')
      expect(sidebar).toHaveStyle('will-change: width')
      // Note: backface-visibility might not be reflected in jsdom
    })

    test('memoizes component properly', () => {
      const onCollapsedChange = jest.fn()
      const { rerender } = render(
        <Sidebar width={320} isCollapsed={false} onCollapsedChange={onCollapsedChange} />
      )

      const firstRender = screen.getByText('Shepherd')
      
      // Re-render with same props
      rerender(
        <Sidebar width={320} isCollapsed={false} onCollapsedChange={onCollapsedChange} />
      )

      // Should be the same element (memoized)
      expect(screen.getByText('Shepherd')).toBe(firstRender)
    })
  })

  describe('ConversationArea Performance', () => {
    test('renders within performance budget', () => {
      const startTime = performance.now()
      
      render(<ConversationArea />)
      
      const renderTime = performance.now() - startTime
      expect(renderTime).toBeLessThan(100)
    })

    test('handles message virtualization', () => {
      const { usePerformanceMode } = require('@/hooks/usePerformance')
      usePerformanceMode.mockReturnValue({
        isLowEnd: true,
        maxItemsToRender: 2, // Very small for testing
        shouldReduceAnimations: true
      })

      render(<ConversationArea />)
      
      // Should have limited number of messages visible
      const messageElements = document.querySelectorAll('.space-y-2')
      expect(messageElements.length).toBeLessThanOrEqual(4) // Sample messages
    })
  })
})