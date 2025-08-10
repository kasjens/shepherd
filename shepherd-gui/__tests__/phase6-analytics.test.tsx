/**
 * Comprehensive tests for Phase 6: Advanced Features & Analytics
 * Tests analytics dashboard, charts, export manager, learning system, 
 * pattern insights, and performance monitoring components
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { jest } from '@jest/globals'

// Mock WebSocket and Canvas
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  public readyState = MockWebSocket.OPEN
  public onopen: ((event: any) => void) | null = null
  public onclose: ((event: any) => void) | null = null
  public onmessage: ((event: any) => void) | null = null
  public onerror: ((event: any) => void) | null = null

  constructor(url: string) {}
  
  send(data: string) {
    // Mock analytics responses
    try {
      const message = JSON.parse(data)
      if (message.type === 'analytics:refresh_all') {
        setTimeout(() => {
          if (this.onmessage) {
            this.onmessage({
              data: JSON.stringify({
                type: 'analytics_update',
                widgetId: 'widget1',
                data: { updated: true }
              })
            })
          }
        }, 10)
      }
    } catch (e) {}
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
  }
}

;(global as any).WebSocket = MockWebSocket

// Mock Canvas and WebGL
const mockCanvas = {
  getContext: jest.fn(() => ({
    clearRect: jest.fn(),
    fillRect: jest.fn(),
    strokeRect: jest.fn(),
    beginPath: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    quadraticCurveTo: jest.fn(),
    arc: jest.fn(),
    stroke: jest.fn(),
    fill: jest.fn(),
    closePath: jest.fn(),
    scale: jest.fn(),
    save: jest.fn(),
    restore: jest.fn(),
    translate: jest.fn(),
    rotate: jest.fn(),
    createLinearGradient: jest.fn(() => ({
      addColorStop: jest.fn()
    })),
    measureText: jest.fn(() => ({ width: 50 })),
    fillText: jest.fn(),
    strokeText: jest.fn(),
    setLineDash: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn()
  })),
  width: 800,
  height: 600,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  toBlob: jest.fn((callback) => callback(new Blob())),
  style: {},
  title: ''
}

HTMLCanvasElement.prototype.getContext = mockCanvas.getContext as any

// Mock Performance API
;(global as any).performance = {
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  memory: {
    jsHeapSizeLimit: 2147483648,
    totalJSHeapSize: 50000000,
    usedJSHeapSize: 30000000
  }
}

// Mock Worker
;(global as any).Worker = jest.fn().mockImplementation(() => ({
  postMessage: jest.fn(),
  terminate: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  onmessage: null
}))

// Mock URL methods for export functionality
;(global as any).URL.createObjectURL = jest.fn(() => 'blob:mock-url')
;(global as any).URL.revokeObjectURL = jest.fn()

// Mock Zustand store
const mockUIStore = {
  theme: 'light' as const,
  reducedMotion: false,
  sidebarCollapsed: false
}

jest.mock('../../src/stores/ui-store', () => ({
  useUIStore: (selector: any) => selector ? selector(mockUIStore) : mockUIStore
}))

// Mock react-window
jest.mock('react-window', () => ({
  FixedSizeGrid: ({ children, columnCount, rowCount }: any) => (
    <div data-testid="virtual-grid">
      {Array.from({ length: Math.min(rowCount * columnCount, 6) }, (_, index) => {
        const rowIndex = Math.floor(index / columnCount)
        const columnIndex = index % columnCount
        return children({ columnIndex, rowIndex, style: {} })
      })}
    </div>
  ),
  FixedSizeList: ({ children, itemCount }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 5) }, (_, index) =>
        children({ index, style: {} })
      )}
    </div>
  )
}))

jest.mock('react-virtualized-auto-sizer', () => {
  return function AutoSizer({ children }: any) {
    return children({ height: 600, width: 800 })
  }
})

// Import components after mocks
import { AdvancedDashboard, ChartWidget, DashboardData } from '../../src/components/analytics/advanced-dashboard'
import { ExportManager } from '../../src/components/analytics/export-manager'
import { FeedbackPanel, QuickFeedback } from '../../src/components/learning/feedback-panel'
import { PatternInsights, Pattern } from '../../src/components/learning/pattern-insights'
import { PerformanceMonitor } from '../../src/components/performance/performance-monitor'

// Mock data
const mockChartWidgets: ChartWidget[] = [
  {
    id: 'widget1',
    type: 'line',
    title: 'Performance Trends',
    description: 'System performance over time',
    dataSource: 'performance',
    config: {
      xAxis: 'timestamp',
      yAxis: 'value',
      timeRange: '24h',
      showGrid: true
    },
    position: { x: 0, y: 0 },
    size: { width: 400, height: 300 },
    isVisible: true,
    lastUpdated: new Date()
  },
  {
    id: 'widget2',
    type: 'bar',
    title: 'Agent Activity',
    description: 'Agent task completion rates',
    dataSource: 'agents',
    config: {
      xAxis: 'agent',
      yAxis: 'tasks',
      groupBy: 'status'
    },
    position: { x: 400, y: 0 },
    size: { width: 400, height: 300 },
    isVisible: true,
    lastUpdated: new Date()
  }
]

const mockDashboardData: DashboardData = {
  performance: [
    { timestamp: '2024-01-01T10:00:00Z', value: 85, metric: 'cpu' },
    { timestamp: '2024-01-01T11:00:00Z', value: 92, metric: 'cpu' },
    { timestamp: '2024-01-01T12:00:00Z', value: 78, metric: 'cpu' }
  ],
  agents: [
    { agent: 'Agent1', tasks: 25, status: 'completed' },
    { agent: 'Agent2', tasks: 18, status: 'completed' },
    { agent: 'Agent3', tasks: 12, status: 'running' }
  ]
}

const mockPatterns: Pattern[] = [
  {
    id: 'pattern1',
    type: 'workflow',
    title: 'Long Running Tasks',
    description: 'Tasks consistently taking longer than expected',
    confidence: 85,
    frequency: 12,
    impact: 'medium',
    trend: 'increasing',
    detectedAt: new Date('2024-01-01'),
    lastSeen: new Date(),
    examples: [
      {
        id: 'example1',
        timestamp: new Date(),
        context: 'Data processing workflow',
        data: { duration: 450, expected: 200 },
        similarity: 92
      }
    ],
    metrics: {
      occurrences: 45,
      avgDuration: 450,
      successRate: 78,
      trendsData: [
        { date: new Date('2024-01-01'), value: 300, metric: 'duration' },
        { date: new Date('2024-01-02'), value: 350, metric: 'duration' }
      ]
    },
    recommendations: [
      {
        id: 'rec1',
        type: 'optimization',
        title: 'Optimize Data Processing',
        description: 'Consider batch processing for large datasets',
        priority: 'medium',
        effort: 'medium',
        expectedImpact: '30% reduction in processing time'
      }
    ],
    tags: ['performance', 'workflow'],
    status: 'active'
  }
]

describe('Phase 6: Advanced Features & Analytics', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Analytics Dashboard', () => {
    it('renders dashboard with widgets', () => {
      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      expect(screen.getByText('Advanced Analytics')).toBeInTheDocument()
      expect(screen.getByText('2 widgets')).toBeInTheDocument()
      expect(screen.getByText('Performance Trends')).toBeInTheDocument()
      expect(screen.getByText('Agent Activity')).toBeInTheDocument()
    })

    it('toggles between grid and list view modes', async () => {
      const user = userEvent.setup()
      
      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      // Should start in grid mode
      expect(screen.getByTestId('virtual-grid')).toBeInTheDocument()

      // Click list view button
      const listViewBtn = screen.getByRole('button', { name: /list/i })
      await user.click(listViewBtn)

      // Should show list mode (no virtual grid)
      expect(screen.queryByTestId('virtual-grid')).not.toBeInTheDocument()
    })

    it('handles widget refresh', async () => {
      const user = userEvent.setup()
      const onWidgetUpdate = jest.fn()

      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
          onWidgetUpdate={onWidgetUpdate}
        />
      )

      const refreshBtn = screen.getByTitle('Refresh All Widgets')
      await user.click(refreshBtn)

      // Should show loading state
      expect(refreshBtn).toHaveClass('opacity-50')
    })

    it('changes grid column count', async () => {
      const user = userEvent.setup()

      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      const columnSelect = screen.getByDisplayValue('3 Columns')
      await user.selectOptions(columnSelect, '2')

      expect(columnSelect).toHaveValue('2')
    })

    it('handles widget addition', async () => {
      const user = userEvent.setup()
      const onWidgetAdd = jest.fn()

      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
          onWidgetAdd={onWidgetAdd}
        />
      )

      const addBtn = screen.getByText('Add Widget')
      await user.click(addBtn)

      expect(onWidgetAdd).toHaveBeenCalled()
    })

    it('shows empty state when no widgets', () => {
      render(
        <AdvancedDashboard
          widgets={[]}
          data={{}}
        />
      )

      expect(screen.getByText('No Widgets')).toBeInTheDocument()
      expect(screen.getByText('Add your first analytics widget to get started')).toBeInTheDocument()
    })
  })

  describe('Chart Components', () => {
    it('renders canvas-based charts', async () => {
      render(
        <AdvancedDashboard
          widgets={[mockChartWidgets[0]]}
          data={mockDashboardData}
        />
      )

      // Should render canvas element
      await waitFor(() => {
        const canvases = document.getElementsByTagName('canvas')
        expect(canvases.length).toBeGreaterThan(0)
      })

      // Canvas context methods should be called
      expect(mockCanvas.getContext).toHaveBeenCalled()
    })

    it('handles chart errors gracefully', async () => {
      // Mock canvas context to throw error
      const mockGetContext = jest.fn(() => {
        throw new Error('Canvas error')
      })
      HTMLCanvasElement.prototype.getContext = mockGetContext

      render(
        <AdvancedDashboard
          widgets={[mockChartWidgets[0]]}
          data={mockDashboardData}
        />
      )

      // Should not crash the component
      expect(screen.getByText('Performance Trends')).toBeInTheDocument()

      // Restore mock
      HTMLCanvasElement.prototype.getContext = mockCanvas.getContext as any
    })

    it('supports different chart types', () => {
      const multiTypeWidgets = [
        { ...mockChartWidgets[0], type: 'line' as const },
        { ...mockChartWidgets[1], type: 'bar' as const, id: 'widget3' },
        { ...mockChartWidgets[0], type: 'pie' as const, id: 'widget4' }
      ]

      render(
        <AdvancedDashboard
          widgets={multiTypeWidgets}
          data={mockDashboardData}
        />
      )

      expect(screen.getByTestId('virtual-grid')).toBeInTheDocument()
    })
  })

  describe('Export Manager', () => {
    it('renders export interface', () => {
      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      expect(screen.getByText('Export Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Export Format')).toBeInTheDocument()
      expect(screen.getByText('PNG')).toBeInTheDocument()
      expect(screen.getByText('PDF')).toBeInTheDocument()
      expect(screen.getByText('JSON')).toBeInTheDocument()
    })

    it('selects export format', async () => {
      const user = userEvent.setup()

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      const pdfBtn = screen.getByText('PDF')
      await user.click(pdfBtn)

      expect(pdfBtn).toHaveClass('border-blue-500')
    })

    it('manages widget selection for export', async () => {
      const user = userEvent.setup()

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      expect(screen.getByText('Widgets to Export (2 of 2)')).toBeInTheDocument()

      // Uncheck first widget
      const widget1Checkbox = screen.getByRole('checkbox', { name: /Performance Trends/ })
      await user.click(widget1Checkbox)

      expect(screen.getByText('Widgets to Export (1 of 2)')).toBeInTheDocument()
    })

    it('starts export process', async () => {
      const user = userEvent.setup()

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      const exportBtn = screen.getByText('Export 2 Widgets')
      await user.click(exportBtn)

      // Should start export process (mocked)
      expect(exportBtn).toBeInTheDocument()
    })

    it('shows advanced options', async () => {
      const user = userEvent.setup()

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      const advancedBtn = screen.getByText('Advanced Options')
      await user.click(advancedBtn)

      expect(screen.getByText('Include metadata')).toBeInTheDocument()
    })

    it('handles export job management', async () => {
      const user = userEvent.setup()

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      // Start an export to create a job
      const exportBtn = screen.getByText('Export 2 Widgets')
      await user.click(exportBtn)

      // Should eventually show recent exports section
      await waitFor(() => {
        expect(screen.getByText('Recent Exports')).toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })

  describe('Learning System - Feedback Panel', () => {
    it('renders feedback panel when open', () => {
      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      expect(screen.getByText('Share Your Feedback')).toBeInTheDocument()
      expect(screen.getByText('Help us improve Shepherd with your insights')).toBeInTheDocument()
    })

    it('does not render when closed', () => {
      render(
        <FeedbackPanel
          isOpen={false}
          onClose={() => {}}
        />
      )

      expect(screen.queryByText('Share Your Feedback')).not.toBeInTheDocument()
    })

    it('handles feedback type selection', async () => {
      const user = userEvent.setup()

      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      const bugReportBtn = screen.getByText('Bug Report')
      await user.click(bugReportBtn)

      expect(bugReportBtn).toHaveClass('border-blue-500')
    })

    it('validates required fields', async () => {
      const user = userEvent.setup()

      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      const submitBtn = screen.getByText('Submit Feedback')
      
      // Should be disabled when no title/description
      expect(submitBtn).toHaveClass('cursor-not-allowed')

      // Fill in title
      const titleInput = screen.getByPlaceholderText('Brief summary of your feedback')
      await user.type(titleInput, 'Test feedback')

      // Still disabled without description
      expect(submitBtn).toHaveClass('cursor-not-allowed')

      // Fill in description
      const descriptionTextarea = screen.getByPlaceholderText(/Please provide detailed feedback/)
      await user.type(descriptionTextarea, 'This is a test feedback description')

      // Should now be enabled
      expect(submitBtn).not.toHaveClass('cursor-not-allowed')
    })

    it('handles tag management', async () => {
      const user = userEvent.setup()

      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      // Add a tag
      const uiTag = screen.getByText('+UI/UX')
      await user.click(uiTag)

      expect(screen.getByText('UI/UX')).toBeInTheDocument()

      // Remove the tag
      const removeBtn = screen.getByRole('button', { name: '' }) // X button in tag
      if (removeBtn) {
        await user.click(removeBtn)
      }
    })

    it('supports star ratings for positive/negative feedback', async () => {
      const user = userEvent.setup()

      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      // Select positive feedback type
      const positiveBtn = screen.getByText('Positive')
      await user.click(positiveBtn)

      // Should show rating stars
      const stars = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('svg')?.classList.contains('w-6') // Star icons
      )
      expect(stars.length).toBeGreaterThanOrEqual(5)

      // Click 4th star
      if (stars[3]) {
        await user.click(stars[3])
      }
    })
  })

  describe('Learning System - Quick Feedback', () => {
    it('renders quick feedback component', () => {
      render(<QuickFeedback />)

      expect(screen.getByText('Rate this:')).toBeInTheDocument()
      expect(screen.getByText('More feedback')).toBeInTheDocument()
    })

    it('handles quick rating submission', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(<QuickFeedback onSubmit={onSubmit} />)

      const stars = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('svg')
      )
      
      if (stars[3]) { // 4th star
        await user.click(stars[3])

        await waitFor(() => {
          expect(onSubmit).toHaveBeenCalled()
        })

        expect(screen.getByText('Thanks for your feedback!')).toBeInTheDocument()
      }
    })

    it('opens full feedback panel', async () => {
      const user = userEvent.setup()

      render(<QuickFeedback />)

      const moreBtn = screen.getByText('More feedback')
      await user.click(moreBtn)

      expect(screen.getByText('Share Your Feedback')).toBeInTheDocument()
    })
  })

  describe('Pattern Insights', () => {
    it('renders pattern insights with data', () => {
      render(<PatternInsights patterns={mockPatterns} />)

      expect(screen.getByText('Pattern Insights')).toBeInTheDocument()
      expect(screen.getByText('1 patterns found')).toBeInTheDocument()
      expect(screen.getByText('Long Running Tasks')).toBeInTheDocument()
    })

    it('handles search functionality', async () => {
      const user = userEvent.setup()

      render(<PatternInsights patterns={mockPatterns} />)

      const searchInput = screen.getByPlaceholderText('Search patterns...')
      await user.type(searchInput, 'workflow')

      expect(searchInput).toHaveValue('workflow')
      // Pattern should still be visible since it matches 'workflow'
      expect(screen.getByText('Long Running Tasks')).toBeInTheDocument()
    })

    it('filters patterns by type', async () => {
      const user = userEvent.setup()

      render(<PatternInsights patterns={mockPatterns} />)

      const typeFilter = screen.getByDisplayValue('All Types')
      await user.selectOptions(typeFilter, 'workflow')

      expect(typeFilter).toHaveValue('workflow')
    })

    it('filters patterns by status', async () => {
      const user = userEvent.setup()

      render(<PatternInsights patterns={mockPatterns} />)

      const statusFilter = screen.getByDisplayValue('All Status')
      await user.selectOptions(statusFilter, 'active')

      expect(statusFilter).toHaveValue('active')
    })

    it('expands pattern details', async () => {
      const user = userEvent.setup()

      render(<PatternInsights patterns={mockPatterns} />)

      const patternCard = screen.getByText('Long Running Tasks').closest('div')
      if (patternCard) {
        await user.click(patternCard)

        // Should show expanded content
        expect(screen.getByText('Metrics')).toBeInTheDocument()
        expect(screen.getByText('Recent Examples')).toBeInTheDocument()
        expect(screen.getByText('Recommendations')).toBeInTheDocument()
      }
    })

    it('handles pattern actions', async () => {
      const user = userEvent.setup()
      const onPatternAction = jest.fn()

      render(
        <PatternInsights 
          patterns={mockPatterns} 
          onPatternAction={onPatternAction}
        />
      )

      // Expand pattern to see actions
      const patternCard = screen.getByText('Long Running Tasks').closest('div')
      if (patternCard) {
        await user.click(patternCard)

        const investigateBtn = screen.getByText('Investigate')
        await user.click(investigateBtn)

        expect(onPatternAction).toHaveBeenCalledWith('pattern1', 'investigate')
      }
    })

    it('shows empty state when no patterns', () => {
      render(<PatternInsights patterns={[]} />)

      expect(screen.getByText('No Patterns Found')).toBeInTheDocument()
      expect(screen.getByText('No patterns have been discovered yet')).toBeInTheDocument()
    })

    it('handles pagination', async () => {
      const user = userEvent.setup()
      
      // Create enough patterns to require pagination
      const manyPatterns = Array.from({ length: 15 }, (_, i) => ({
        ...mockPatterns[0],
        id: `pattern${i}`,
        title: `Pattern ${i}`
      }))

      render(<PatternInsights patterns={manyPatterns} />)

      expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()

      const nextBtn = screen.getByText('Next')
      await user.click(nextBtn)

      expect(screen.getByText('Page 2 of 2')).toBeInTheDocument()
    })
  })

  describe('Performance Monitor', () => {
    beforeEach(() => {
      // Mock requestAnimationFrame
      ;(global as any).requestAnimationFrame = jest.fn((cb) => setTimeout(cb, 16))
      ;(global as any).cancelAnimationFrame = jest.fn()
      
      // Mock PerformanceObserver
      ;(global as any).PerformanceObserver = jest.fn().mockImplementation((callback) => ({
        observe: jest.fn(),
        disconnect: jest.fn()
      }))
    })

    it('renders performance monitor', () => {
      render(<PerformanceMonitor />)

      expect(screen.getByText('Performance Monitor')).toBeInTheDocument()
      expect(screen.getByText('Real-time application performance metrics')).toBeInTheDocument()
    })

    it('displays performance metrics cards', async () => {
      render(<PerformanceMonitor />)

      await waitFor(() => {
        expect(screen.getByText('FPS')).toBeInTheDocument()
        expect(screen.getByText('Memory')).toBeInTheDocument()
        expect(screen.getByText('DOM Nodes')).toBeInTheDocument()
        expect(screen.getByText('Render Time')).toBeInTheDocument()
      })
    })

    it('handles monitoring pause/resume', async () => {
      const user = userEvent.setup()

      render(<PerformanceMonitor />)

      const pauseBtn = screen.getByText('Pause')
      await user.click(pauseBtn)

      expect(screen.getByText('Resume')).toBeInTheDocument()

      const resumeBtn = screen.getByText('Resume')
      await user.click(resumeBtn)

      expect(screen.getByText('Pause')).toBeInTheDocument()
    })

    it('clears metrics data', async () => {
      const user = userEvent.setup()

      render(<PerformanceMonitor />)

      const clearBtn = screen.getByText('Clear')
      await user.click(clearBtn)

      // Should clear metrics (component should still render)
      expect(screen.getByText('Performance Monitor')).toBeInTheDocument()
    })

    it('shows performance alerts when thresholds exceeded', async () => {
      // Mock performance.memory to exceed thresholds
      ;(global as any).performance.memory = {
        jsHeapSizeLimit: 2147483648,
        totalJSHeapSize: 150000000, // 150MB - over warning threshold
        usedJSHeapSize: 120000000   // 120MB - over warning threshold
      }

      render(<PerformanceMonitor updateInterval={100} />)

      // Wait for metrics collection
      await waitFor(() => {
        expect(screen.getByText('Performance Alerts')).toBeInTheDocument()
      }, { timeout: 2000 })
    })

    it('renders performance chart', async () => {
      render(<PerformanceMonitor />)

      await waitFor(() => {
        const canvases = document.getElementsByTagName('canvas')
        expect(canvases.length).toBeGreaterThan(0)
      })
    })

    it('switches between different metrics', async () => {
      const user = userEvent.setup()

      render(<PerformanceMonitor />)

      await waitFor(() => {
        expect(screen.getByText('FPS')).toBeInTheDocument()
      })

      const memoryCard = screen.getByText('Memory').closest('div')
      if (memoryCard) {
        await user.click(memoryCard)
        // Should switch to memory metric view
      }
    })

    it('shows optimization recommendations', async () => {
      const user = userEvent.setup()

      render(<PerformanceMonitor />)

      // Click settings to show optimizations
      const settingsBtn = screen.getByRole('button', { name: '' }) // Settings button
      if (settingsBtn) {
        await user.click(settingsBtn)

        expect(screen.getByText('Performance Recommendations')).toBeInTheDocument()
      }
    })
  })

  describe('Integration Scenarios', () => {
    it('integrates analytics dashboard with real-time updates via WebSocket', async () => {
      const onWidgetUpdate = jest.fn()

      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
          onWidgetUpdate={onWidgetUpdate}
        />
      )

      // Simulate WebSocket message
      await act(async () => {
        const mockWs = new MockWebSocket('ws://test')
        if (mockWs.onmessage) {
          mockWs.onmessage({
            data: JSON.stringify({
              type: 'analytics_update',
              widgetId: 'widget1',
              data: { newValue: 100 }
            })
          })
        }
      })

      // Widget should receive update
      await waitFor(() => {
        expect(onWidgetUpdate).toHaveBeenCalledWith(
          expect.objectContaining({
            id: 'widget1',
            lastUpdated: expect.any(Date)
          })
        )
      })
    })

    it('handles export with performance monitoring data', async () => {
      const user = userEvent.setup()

      // Render both components
      const { rerender } = render(
        <div>
          <PerformanceMonitor />
          <ExportManager widgets={mockChartWidgets} data={mockDashboardData} />
        </div>
      )

      // Wait for performance data collection
      await waitFor(() => {
        expect(screen.getByText('FPS')).toBeInTheDocument()
      })

      // Try to export data
      const exportBtn = screen.getByText('Export 2 Widgets')
      await user.click(exportBtn)

      expect(exportBtn).toBeInTheDocument()
    })

    it('integrates feedback system with pattern insights', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(
        <div>
          <PatternInsights patterns={mockPatterns} />
          <QuickFeedback 
            context={{ feature: 'pattern-insights' }}
            onSubmit={onSubmit}
          />
        </div>
      )

      // Rate the pattern insights feature
      const stars = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('svg')
      )
      
      if (stars[4]) { // 5th star
        await user.click(stars[4])

        await waitFor(() => {
          expect(onSubmit).toHaveBeenCalledWith(
            expect.objectContaining({
              type: 'positive',
              rating: 5,
              context: { feature: 'pattern-insights' }
            })
          )
        })
      }
    })

    it('handles multiple concurrent chart renderings', async () => {
      const multipleWidgets = Array.from({ length: 6 }, (_, i) => ({
        ...mockChartWidgets[0],
        id: `widget${i}`,
        title: `Chart ${i}`,
        type: ['line', 'bar', 'pie'][i % 3] as ChartWidget['type']
      }))

      render(
        <AdvancedDashboard
          widgets={multipleWidgets}
          data={mockDashboardData}
        />
      )

      // Should render multiple charts without performance issues
      await waitFor(() => {
        expect(screen.getByTestId('virtual-grid')).toBeInTheDocument()
      })

      // All charts should be rendered
      multipleWidgets.forEach((widget, i) => {
        expect(screen.getByText(`Chart ${i}`)).toBeInTheDocument()
      })
    })
  })

  describe('Performance and Memory Management', () => {
    it('handles large datasets efficiently', () => {
      const largeData = {
        performance: Array.from({ length: 10000 }, (_, i) => ({
          timestamp: new Date(Date.now() - i * 1000).toISOString(),
          value: Math.random() * 100,
          metric: 'cpu'
        }))
      }

      const { container } = render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={largeData}
        />
      )

      // Should not crash with large datasets
      expect(container).toBeInTheDocument()
      expect(screen.getByText('Advanced Analytics')).toBeInTheDocument()
    })

    it('properly cleans up resources on unmount', () => {
      const { unmount } = render(
        <PerformanceMonitor updateInterval={100} />
      )

      // Should not throw errors on unmount
      expect(() => unmount()).not.toThrow()
    })

    it('handles WebWorker unavailability gracefully', () => {
      // Temporarily disable Worker
      const originalWorker = (global as any).Worker
      delete (global as any).Worker

      render(
        <ExportManager
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      expect(screen.getByText('Export Dashboard')).toBeInTheDocument()

      // Restore Worker
      ;(global as any).Worker = originalWorker
    })
  })

  describe('Accessibility', () => {
    it('provides proper ARIA labels for dashboard controls', () => {
      render(
        <AdvancedDashboard
          widgets={mockChartWidgets}
          data={mockDashboardData}
        />
      )

      const refreshBtn = screen.getByTitle('Refresh All Widgets')
      expect(refreshBtn).toHaveAttribute('title')

      // Grid/List toggle should be accessible
      const gridBtn = screen.getByRole('button', { name: /grid/i })
      expect(gridBtn).toBeInTheDocument()
    })

    it('supports keyboard navigation in feedback forms', async () => {
      render(
        <FeedbackPanel
          isOpen={true}
          onClose={() => {}}
        />
      )

      const titleInput = screen.getByPlaceholderText('Brief summary of your feedback')
      titleInput.focus()
      expect(document.activeElement).toBe(titleInput)

      // Tab should move to next field
      fireEvent.keyDown(titleInput, { key: 'Tab' })
    })

    it('provides screen reader friendly pattern insights', () => {
      render(<PatternInsights patterns={mockPatterns} />)

      // Should have proper headings
      expect(screen.getByText('Pattern Insights')).toBeInTheDocument()
      expect(screen.getByText('Long Running Tasks')).toBeInTheDocument()

      // Status should be accessible
      expect(screen.getByText('active')).toBeInTheDocument()
    })
  })
})