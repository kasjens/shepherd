/**
 * Integration tests for Phase 4: Advanced Features & Integrations
 * Tests advanced components including Analytics Dashboard, Artifacts Browser,
 * Advanced Settings, Conversation Export, and Learning Insights
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { jest } from '@jest/globals'

// Mock Zustand store
const mockUIStore = {
  theme: 'light' as const,
  reducedMotion: false,
  sidebarCollapsed: false,
  setSidebarCollapsed: jest.fn(),
  setTheme: jest.fn(),
  setReducedMotion: jest.fn()
}

jest.mock('../../src/stores/ui-store', () => ({
  useUIStore: (selector: any) => selector ? selector(mockUIStore) : mockUIStore
}))

// Mock react-grid-layout
jest.mock('react-grid-layout', () => ({
  __esModule: true,
  Responsive: ({ children }: any) => <div data-testid="grid-layout">{children}</div>,
  WidthProvider: (Component: any) => Component
}))

// Mock react-window
jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemCount }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 10) }, (_, index) =>
        children({ index, style: {} })
      )}
    </div>
  )
}))

// Mock react-virtualized-auto-sizer
jest.mock('react-virtualized-auto-sizer', () => {
  return function AutoSizer({ children }: any) {
    return children({ height: 600, width: 800 })
  }
})

// Mock recharts
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  RadarChart: ({ children }: any) => <div data-testid="radar-chart">{children}</div>,
  Radar: () => <div data-testid="radar" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  Cell: () => <div data-testid="cell" />,
  PolarGrid: () => <div data-testid="polar-grid" />,
  PolarAngleAxis: () => <div data-testid="polar-angle-axis" />,
  PolarRadiusAxis: () => <div data-testid="polar-radius-axis" />
}))

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date, formatStr) => {
    if (typeof date === 'string') return date
    return '2024-01-15'
  }),
  subDays: jest.fn((date, days) => new Date(2024, 0, 15 - days)),
  startOfDay: jest.fn((date) => date),
  endOfDay: jest.fn((date) => date)
}))

// Import components
import AnalyticsDashboard, { DashboardConfig } from '../../src/components/analytics/analytics-dashboard'
import FileBrowser, { FileItem } from '../../src/components/artifacts/file-browser'
import FilePreview from '../../src/components/artifacts/file-preview'
import AdvancedSettings, { AdvancedSettingsConfig } from '../../src/components/settings/advanced-settings'
import ConversationExport, { ConversationData, ExportOptions } from '../../src/components/export/conversation-export'
import LearningInsights, { PatternData, LearningMetrics, Recommendation } from '../../src/components/learning/learning-insights'

describe('Phase 4: Advanced Features Integration Tests', () => {
  const user = userEvent.setup()

  describe('Analytics Dashboard', () => {
    const mockDashboardConfig: DashboardConfig = {
      id: 'test-dashboard',
      name: 'Test Dashboard',
      layout: [
        { i: 'widget-1', x: 0, y: 0, w: 4, h: 3 },
        { i: 'widget-2', x: 4, y: 0, w: 4, h: 3 }
      ],
      widgets: [
        {
          id: 'widget-1',
          title: 'Test Metric',
          type: 'metric',
          data: { value: 1234, previousValue: 1100, label: 'Test', color: 'blue', icon: 'Activity' }
        },
        {
          id: 'widget-2',
          title: 'Test Chart',
          type: 'chart',
          data: {
            chartType: 'line',
            data: [
              { name: 'Jan', value: 400 },
              { name: 'Feb', value: 300 }
            ],
            xKey: 'name',
            yKey: 'value',
            colors: ['#3B82F6']
          }
        }
      ],
      settings: {
        autoRefresh: true,
        refreshInterval: 30,
        compactMode: false,
        showGrid: true
      }
    }

    it('renders dashboard with widgets correctly', () => {
      const onConfigChange = jest.fn()
      
      render(
        <AnalyticsDashboard
          config={mockDashboardConfig}
          onConfigChange={onConfigChange}
        />
      )

      expect(screen.getByText('Test Dashboard')).toBeInTheDocument()
      expect(screen.getByText('2 widgets')).toBeInTheDocument()
      expect(screen.getByTestId('grid-layout')).toBeInTheDocument()
    })

    it('handles edit mode toggle', async () => {
      const onConfigChange = jest.fn()
      const onEditToggle = jest.fn()
      
      render(
        <AnalyticsDashboard
          config={mockDashboardConfig}
          onConfigChange={onConfigChange}
          onEditToggle={onEditToggle}
        />
      )

      const editButton = screen.getByRole('button', { name: /edit layout/i })
      await user.click(editButton)

      expect(onEditToggle).toHaveBeenCalledWith(true)
    })

    it('can add new widgets in edit mode', async () => {
      const onConfigChange = jest.fn()
      
      render(
        <AnalyticsDashboard
          config={mockDashboardConfig}
          onConfigChange={onConfigChange}
          isEditing={true}
        />
      )

      // Should show widget add buttons in edit mode
      expect(screen.getByText('Add Widget:')).toBeInTheDocument()
      
      const metricButton = screen.getByRole('button', { name: /metric/i })
      await user.click(metricButton)

      expect(onConfigChange).toHaveBeenCalled()
      const call = onConfigChange.mock.calls[0][0]
      expect(call.widgets).toHaveLength(3)
      expect(call.widgets[2].type).toBe('metric')
    })

    it('handles export functionality', async () => {
      const onExport = jest.fn()
      
      render(
        <AnalyticsDashboard
          config={mockDashboardConfig}
          onExport={onExport}
        />
      )

      // Hover over export button to show dropdown
      const exportButton = screen.getByTitle('Export Dashboard')
      fireEvent.mouseEnter(exportButton)

      await waitFor(() => {
        const pdfButton = screen.getByText('Export as PDF')
        expect(pdfButton).toBeInTheDocument()
      })
    })

    it('supports auto-refresh functionality', () => {
      jest.useFakeTimers()
      
      const config = {
        ...mockDashboardConfig,
        settings: { ...mockDashboardConfig.settings, autoRefresh: true, refreshInterval: 1 }
      }
      
      render(<AnalyticsDashboard config={config} />)

      // Fast-forward time to trigger refresh
      jest.advanceTimersByTime(2000)
      
      jest.useRealTimers()
    })
  })

  describe('File Browser & Preview', () => {
    const mockFiles: FileItem[] = [
      {
        id: 'file-1',
        name: 'test.py',
        type: 'file',
        size: 1024,
        mimeType: 'text/x-python',
        extension: 'py',
        path: '/test.py',
        parentPath: '/',
        createdAt: new Date('2024-01-01'),
        modifiedAt: new Date('2024-01-15'),
        permissions: { read: true, write: true, execute: false },
        starred: false,
        tags: ['python', 'script'],
        content: 'print("Hello World")'
      },
      {
        id: 'folder-1',
        name: 'Documents',
        type: 'folder',
        path: '/Documents',
        parentPath: '/',
        createdAt: new Date('2024-01-01'),
        modifiedAt: new Date('2024-01-10'),
        permissions: { read: true, write: true, execute: true },
        starred: true,
        tags: ['docs']
      }
    ]

    it('renders file browser with files and folders', () => {
      const mockHandlers = {
        onNavigate: jest.fn(),
        onSelectFiles: jest.fn(),
        onViewModeChange: jest.fn(),
        onSortChange: jest.fn(),
        onSearchChange: jest.fn(),
        onFilterChange: jest.fn(),
        onFileAction: jest.fn(),
        onCreateFolder: jest.fn(),
        onUploadFiles: jest.fn(),
        onRefresh: jest.fn()
      }

      render(
        <FileBrowser
          files={mockFiles}
          currentPath="/"
          selectedFiles={new Set()}
          viewMode="list"
          sortBy="name"
          sortOrder="asc"
          searchQuery=""
          filterType="all"
          {...mockHandlers}
        />
      )

      expect(screen.getByText('test.py')).toBeInTheDocument()
      expect(screen.getByText('Documents')).toBeInTheDocument()
      expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
    })

    it('handles file selection and actions', async () => {
      const onSelectFiles = jest.fn()
      const onFileAction = jest.fn()
      
      const mockHandlers = {
        onNavigate: jest.fn(),
        onSelectFiles,
        onViewModeChange: jest.fn(),
        onSortChange: jest.fn(),
        onSearchChange: jest.fn(),
        onFilterChange: jest.fn(),
        onFileAction,
        onCreateFolder: jest.fn(),
        onUploadFiles: jest.fn(),
        onRefresh: jest.fn()
      }

      render(
        <FileBrowser
          files={mockFiles}
          currentPath="/"
          selectedFiles={new Set()}
          viewMode="list"
          sortBy="name"
          sortOrder="asc"
          searchQuery=""
          filterType="all"
          {...mockHandlers}
        />
      )

      // Test file selection (simulating click on file)
      const fileElement = screen.getByText('test.py')
      await user.click(fileElement)

      expect(onSelectFiles).toHaveBeenCalled()
    })

    it('supports search and filtering', async () => {
      const onSearchChange = jest.fn()
      const onFilterChange = jest.fn()
      
      const mockHandlers = {
        onNavigate: jest.fn(),
        onSelectFiles: jest.fn(),
        onViewModeChange: jest.fn(),
        onSortChange: jest.fn(),
        onSearchChange,
        onFilterChange,
        onFileAction: jest.fn(),
        onCreateFolder: jest.fn(),
        onUploadFiles: jest.fn(),
        onRefresh: jest.fn()
      }

      render(
        <FileBrowser
          files={mockFiles}
          currentPath="/"
          selectedFiles={new Set()}
          viewMode="list"
          sortBy="name"
          sortOrder="asc"
          searchQuery=""
          filterType="all"
          {...mockHandlers}
        />
      )

      const searchInput = screen.getByPlaceholderText('Search files...')
      await user.type(searchInput, 'test')

      expect(onSearchChange).toHaveBeenCalled()

      const filterSelect = screen.getByDisplayValue('All Items')
      await user.selectOptions(filterSelect, 'files')

      expect(onFilterChange).toHaveBeenCalledWith('files')
    })

    it('renders file preview with syntax highlighting', () => {
      const onClose = jest.fn()
      
      render(
        <FilePreview
          file={mockFiles[0]}
          onClose={onClose}
        />
      )

      expect(screen.getByText('test.py')).toBeInTheDocument()
      expect(screen.getByText('text/x-python')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument()
    })

    it('handles file preview actions', async () => {
      const onClose = jest.fn()
      const onDownload = jest.fn()
      
      render(
        <FilePreview
          file={mockFiles[0]}
          onClose={onClose}
          onDownload={onDownload}
        />
      )

      const downloadButton = screen.getByTitle('Download File')
      await user.click(downloadButton)

      expect(onDownload).toHaveBeenCalledWith(mockFiles[0])

      const closeButton = screen.getByTitle('Close')
      await user.click(closeButton)

      expect(onClose).toHaveBeenCalled()
    })
  })

  describe('Advanced Settings', () => {
    const mockConfig: AdvancedSettingsConfig = {
      general: {
        autoSave: true,
        autoSaveInterval: 30,
        confirmBeforeExit: true,
        enableAnalytics: true,
        maxRecentItems: 10,
        defaultWorkspace: 'default'
      },
      appearance: {
        theme: 'light',
        compactMode: false,
        reducedMotion: false,
        showLineNumbers: true,
        fontSize: 'medium',
        sidebarWidth: 280
      },
      notifications: {
        enableDesktop: true,
        enableSound: false,
        taskCompletion: true,
        errorAlerts: true,
        systemUpdates: true,
        emailDigest: false,
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        }
      },
      performance: {
        maxMemoryUsage: 1024,
        enableCaching: true,
        cacheSize: 100,
        backgroundSync: true,
        hardwareAcceleration: true,
        preloadNextPage: false,
        virtualScrolling: true
      },
      security: {
        enableEncryption: false,
        sessionTimeout: 24,
        requirePasswordForSensitiveActions: false,
        enableTwoFactor: false,
        auditLogging: true,
        ipWhitelist: [],
        allowedFileTypes: ['txt', 'md', 'json']
      },
      data: {
        maxHistoryItems: 1000,
        autoBackup: false,
        backupInterval: 'daily',
        retentionPeriod: 90,
        exportFormat: 'json',
        compressionEnabled: true,
        cloudSync: false
      }
    }

    it('renders settings with all tabs', () => {
      const mockHandlers = {
        onConfigChange: jest.fn(),
        onSave: jest.fn(),
        onReset: jest.fn(),
        onImport: jest.fn(),
        onExport: jest.fn()
      }

      render(
        <AdvancedSettings
          config={mockConfig}
          {...mockHandlers}
        />
      )

      expect(screen.getByText('Settings')).toBeInTheDocument()
      expect(screen.getByText('General')).toBeInTheDocument()
      expect(screen.getByText('Appearance')).toBeInTheDocument()
      expect(screen.getByText('Notifications')).toBeInTheDocument()
      expect(screen.getByText('Performance')).toBeInTheDocument()
      expect(screen.getByText('Security')).toBeInTheDocument()
      expect(screen.getByText('Data & Storage')).toBeInTheDocument()
    })

    it('handles tab navigation', async () => {
      const mockHandlers = {
        onConfigChange: jest.fn(),
        onSave: jest.fn(),
        onReset: jest.fn(),
        onImport: jest.fn(),
        onExport: jest.fn()
      }

      render(
        <AdvancedSettings
          config={mockConfig}
          {...mockHandlers}
        />
      )

      const appearanceTab = screen.getByText('Appearance')
      await user.click(appearanceTab)

      expect(screen.getByText('Appearance Settings')).toBeInTheDocument()
      expect(screen.getByText('Theme')).toBeInTheDocument()
    })

    it('handles setting changes', async () => {
      const onConfigChange = jest.fn()
      const mockHandlers = {
        onConfigChange,
        onSave: jest.fn(),
        onReset: jest.fn(),
        onImport: jest.fn(),
        onExport: jest.fn()
      }

      render(
        <AdvancedSettings
          config={mockConfig}
          {...mockHandlers}
        />
      )

      const autoSaveCheckbox = screen.getByLabelText(/auto-save/i)
      await user.click(autoSaveCheckbox)

      expect(onConfigChange).toHaveBeenCalledWith({
        ...mockConfig,
        general: { ...mockConfig.general, autoSave: false }
      })
    })

    it('handles save and reset actions', async () => {
      const onSave = jest.fn()
      const onReset = jest.fn()
      const mockHandlers = {
        onConfigChange: jest.fn(),
        onSave,
        onReset,
        onImport: jest.fn(),
        onExport: jest.fn()
      }

      render(
        <AdvancedSettings
          config={mockConfig}
          {...mockHandlers}
        />
      )

      const resetButton = screen.getByRole('button', { name: /reset/i })
      await user.click(resetButton)

      expect(onReset).toHaveBeenCalled()
    })
  })

  describe('Conversation Export', () => {
    const mockConversations: ConversationData[] = [
      {
        id: 'conv-1',
        title: 'Test Conversation',
        participants: ['user', 'assistant'],
        messageCount: 10,
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-15'),
        totalTokens: 1500,
        status: 'active',
        tags: ['test', 'example'],
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Hello',
            timestamp: new Date('2024-01-01'),
            tokens: 50
          }
        ]
      }
    ]

    it('renders export interface with conversations', () => {
      const mockHandlers = {
        onExport: jest.fn(),
        onPreview: jest.fn()
      }

      render(
        <ConversationExport
          conversations={mockConversations}
          {...mockHandlers}
        />
      )

      expect(screen.getByText('Export Conversations')).toBeInTheDocument()
      expect(screen.getByText('Test Conversation')).toBeInTheDocument()
      expect(screen.getByText('10 messages')).toBeInTheDocument()
    })

    it('handles format selection', async () => {
      const mockHandlers = {
        onExport: jest.fn(),
        onPreview: jest.fn()
      }

      render(
        <ConversationExport
          conversations={mockConversations}
          {...mockHandlers}
        />
      )

      const jsonFormatButton = screen.getByText('JSON')
      await user.click(jsonFormatButton)

      // Should show JSON as selected format
      expect(screen.getByText('JSON').closest('button')).toHaveClass('border-blue-500')
    })

    it('handles conversation selection and export', async () => {
      const onExport = jest.fn().mockResolvedValue(undefined)
      const mockHandlers = {
        onExport,
        onPreview: jest.fn()
      }

      render(
        <ConversationExport
          conversations={mockConversations}
          {...mockHandlers}
        />
      )

      // Select conversation
      const conversationElement = screen.getByText('Test Conversation')
      await user.click(conversationElement)

      // Export button should be enabled
      const exportButton = screen.getByRole('button', { name: /export 1 conversation/i })
      expect(exportButton).not.toBeDisabled()

      await user.click(exportButton)
      expect(onExport).toHaveBeenCalled()
    })

    it('supports search and filtering', async () => {
      const mockHandlers = {
        onExport: jest.fn(),
        onPreview: jest.fn()
      }

      render(
        <ConversationExport
          conversations={mockConversations}
          {...mockHandlers}
        />
      )

      const searchInput = screen.getByPlaceholderText('Search conversations...')
      await user.type(searchInput, 'Test')

      // Conversation should still be visible
      expect(screen.getByText('Test Conversation')).toBeInTheDocument()
    })
  })

  describe('Learning Insights', () => {
    const mockPatterns: PatternData[] = [
      {
        id: 'pattern-1',
        name: 'User Workflow Optimization',
        type: 'workflow',
        description: 'Users tend to perform tasks more efficiently in the morning',
        confidence: 85,
        frequency: 24,
        impact: 'high',
        trend: 'increasing',
        discoveredAt: new Date('2024-01-01'),
        lastSeen: new Date('2024-01-15'),
        examples: [
          {
            id: 'ex-1',
            description: 'Morning efficiency spike',
            timestamp: new Date('2024-01-15'),
            context: {}
          }
        ]
      }
    ]

    const mockMetrics: LearningMetrics = {
      totalPatterns: 42,
      newPatternsThisWeek: 5,
      accuracyScore: 89,
      predictionSuccess: 76,
      adaptationRate: 68,
      knowledgeGrowth: 12
    }

    const mockRecommendations: Recommendation[] = [
      {
        id: 'rec-1',
        type: 'optimization',
        priority: 'high',
        title: 'Optimize Morning Workflows',
        description: 'Consider scheduling complex tasks in the morning hours',
        expectedImpact: '15% efficiency improvement',
        effort: 'low',
        category: 'workflow',
        actionItems: ['Adjust task scheduling', 'Update user recommendations'],
        createdAt: new Date('2024-01-15')
      }
    ]

    it('renders learning insights overview', () => {
      const mockHandlers = {
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights: jest.fn()
      }

      render(
        <LearningInsights
          patterns={mockPatterns}
          metrics={mockMetrics}
          recommendations={mockRecommendations}
          {...mockHandlers}
        />
      )

      expect(screen.getByText('Learning Insights')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument() // Total patterns
      expect(screen.getByText('89%')).toBeInTheDocument() // Accuracy score
    })

    it('handles tab navigation', async () => {
      const mockHandlers = {
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights: jest.fn()
      }

      render(
        <LearningInsights
          patterns={mockPatterns}
          metrics={mockMetrics}
          recommendations={mockRecommendations}
          {...mockHandlers}
        />
      )

      const patternsTab = screen.getByText('Patterns')
      await user.click(patternsTab)

      expect(screen.getByText('User Workflow Optimization')).toBeInTheDocument()
    })

    it('handles pattern details and recommendations', async () => {
      const onPatternDetails = jest.fn()
      const onRecommendationAction = jest.fn()
      const mockHandlers = {
        onPatternDetails,
        onRecommendationAction,
        onExportInsights: jest.fn()
      }

      render(
        <LearningInsights
          patterns={mockPatterns}
          metrics={mockMetrics}
          recommendations={mockRecommendations}
          {...mockHandlers}
        />
      )

      // Go to patterns tab
      const patternsTab = screen.getByText('Patterns')
      await user.click(patternsTab)

      const detailsButton = screen.getByRole('button', { name: /details/i })
      await user.click(detailsButton)

      expect(onPatternDetails).toHaveBeenCalledWith('pattern-1')

      // Go to recommendations tab
      const recommendationsTab = screen.getByText('Recommendations')
      await user.click(recommendationsTab)

      const implementButton = screen.getByRole('button', { name: /implement/i })
      await user.click(implementButton)

      expect(onRecommendationAction).toHaveBeenCalledWith('rec-1', 'implement')
    })

    it('displays charts and visualizations', () => {
      const mockHandlers = {
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights: jest.fn()
      }

      render(
        <LearningInsights
          patterns={mockPatterns}
          metrics={mockMetrics}
          recommendations={mockRecommendations}
          {...mockHandlers}
        />
      )

      expect(screen.getByTestId('line-chart')).toBeInTheDocument()
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
      expect(screen.getByTestId('radar-chart')).toBeInTheDocument()
    })

    it('handles export functionality', async () => {
      const onExportInsights = jest.fn()
      const mockHandlers = {
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights
      }

      render(
        <LearningInsights
          patterns={mockPatterns}
          metrics={mockMetrics}
          recommendations={mockRecommendations}
          {...mockHandlers}
        />
      )

      const exportButton = screen.getByRole('button', { name: /export report/i })
      await user.click(exportButton)

      expect(onExportInsights).toHaveBeenCalledWith('pdf')
    })
  })

  describe('Integration Scenarios', () => {
    it('handles component interactions and state management', async () => {
      // Test scenario: User navigates through advanced features
      const mockDashboardConfig: DashboardConfig = {
        id: 'integration-test',
        name: 'Integration Test Dashboard',
        layout: [],
        widgets: [],
        settings: {
          autoRefresh: false,
          refreshInterval: 30,
          compactMode: false,
          showGrid: true
        }
      }

      const onConfigChange = jest.fn()
      
      render(
        <AnalyticsDashboard
          config={mockDashboardConfig}
          onConfigChange={onConfigChange}
          isEditing={true}
        />
      )

      // Add a metric widget
      const metricButton = screen.getByRole('button', { name: /metric/i })
      await user.click(metricButton)

      expect(onConfigChange).toHaveBeenCalled()
      
      // Add a chart widget
      const chartButton = screen.getByRole('button', { name: /chart/i })
      await user.click(chartButton)

      expect(onConfigChange).toHaveBeenCalledTimes(2)
    })

    it('handles error states and edge cases', () => {
      // Test empty states
      render(
        <FileBrowser
          files={[]}
          currentPath="/"
          selectedFiles={new Set()}
          viewMode="list"
          sortBy="name"
          sortOrder="asc"
          searchQuery=""
          filterType="all"
          onNavigate={jest.fn()}
          onSelectFiles={jest.fn()}
          onViewModeChange={jest.fn()}
          onSortChange={jest.fn()}
          onSearchChange={jest.fn()}
          onFilterChange={jest.fn()}
          onFileAction={jest.fn()}
          onCreateFolder={jest.fn()}
          onUploadFiles={jest.fn()}
          onRefresh={jest.fn()}
        />
      )

      expect(screen.getByText(/this folder is empty/i)).toBeInTheDocument()
    })

    it('maintains accessibility standards', () => {
      const mockHandlers = {
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights: jest.fn()
      }

      render(
        <LearningInsights
          patterns={[]}
          metrics={{
            totalPatterns: 0,
            newPatternsThisWeek: 0,
            accuracyScore: 0,
            predictionSuccess: 0,
            adaptationRate: 0,
            knowledgeGrowth: 0
          }}
          recommendations={[]}
          {...mockHandlers}
        />
      )

      // Check for proper ARIA labels and roles
      const mainHeading = screen.getByRole('heading', { level: 1 })
      expect(mainHeading).toBeInTheDocument()
      
      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).toBeInTheDocument()
      })
    })
  })
})

describe('Phase 4 Component Performance', () => {
  it('handles large datasets efficiently', () => {
    const largeFileList: FileItem[] = Array.from({ length: 1000 }, (_, i) => ({
      id: `file-${i}`,
      name: `test-file-${i}.txt`,
      type: 'file',
      size: 1024,
      mimeType: 'text/plain',
      extension: 'txt',
      path: `/test-file-${i}.txt`,
      parentPath: '/',
      createdAt: new Date(),
      modifiedAt: new Date(),
      permissions: { read: true, write: false, execute: false },
      starred: false,
      tags: []
    }))

    const start = performance.now()
    
    render(
      <FileBrowser
        files={largeFileList}
        currentPath="/"
        selectedFiles={new Set()}
        viewMode="list"
        sortBy="name"
        sortOrder="asc"
        searchQuery=""
        filterType="all"
        onNavigate={jest.fn()}
        onSelectFiles={jest.fn()}
        onViewModeChange={jest.fn()}
        onSortChange={jest.fn()}
        onSearchChange={jest.fn()}
        onFilterChange={jest.fn()}
        onFileAction={jest.fn()}
        onCreateFolder={jest.fn()}
        onUploadFiles={jest.fn()}
        onRefresh={jest.fn()}
      />
    )

    const end = performance.now()
    const renderTime = end - start

    // Should render within reasonable time (< 100ms)
    expect(renderTime).toBeLessThan(100)
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
  })

  it('efficiently updates dashboard widgets', () => {
    const config: DashboardConfig = {
      id: 'perf-test',
      name: 'Performance Test',
      layout: [],
      widgets: Array.from({ length: 20 }, (_, i) => ({
        id: `widget-${i}`,
        title: `Widget ${i}`,
        type: 'metric' as const,
        data: { value: i * 100, label: `Metric ${i}`, color: 'blue', icon: 'Activity' }
      })),
      settings: {
        autoRefresh: false,
        refreshInterval: 30,
        compactMode: false,
        showGrid: true
      }
    }

    const onConfigChange = jest.fn()
    
    const start = performance.now()
    
    render(
      <AnalyticsDashboard
        config={config}
        onConfigChange={onConfigChange}
      />
    )

    const end = performance.now()
    const renderTime = end - start

    // Should render many widgets efficiently
    expect(renderTime).toBeLessThan(150)
    expect(screen.getByTestId('grid-layout')).toBeInTheDocument()
  })
})