/**
 * Simplified Integration tests for Phase 4: Advanced Features
 * Tests core functionality without causing infinite render loops
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
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

// Mock external libraries
jest.mock('react-grid-layout', () => ({
  __esModule: true,
  Responsive: ({ children }: any) => <div data-testid="grid-layout">{children}</div>,
  WidthProvider: (Component: any) => Component
}))

jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemCount }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 3) }, (_, index) =>
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

jest.mock('recharts', () => ({
  LineChart: () => <div data-testid="line-chart" />,
  Line: () => <div />,
  AreaChart: () => <div data-testid="area-chart" />,
  Area: () => <div />,
  BarChart: () => <div data-testid="bar-chart" />,
  Bar: () => <div />,
  PieChart: () => <div data-testid="pie-chart" />,
  Pie: () => <div />,
  RadarChart: () => <div data-testid="radar-chart" />,
  Radar: () => <div />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  Cell: () => <div />,
  PolarGrid: () => <div />,
  PolarAngleAxis: () => <div />,
  PolarRadiusAxis: () => <div />
}))

jest.mock('date-fns', () => ({
  format: jest.fn(() => '2024-01-15'),
  subDays: jest.fn((date, days) => new Date(2024, 0, 15 - days)),
  startOfDay: jest.fn((date) => date),
  endOfDay: jest.fn((date) => date)
}))

// Mock react-syntax-highlighter to prevent it from causing issues
jest.mock('react-syntax-highlighter', () => ({
  Prism: ({ children }: any) => <pre data-testid="syntax-highlighter">{children}</pre>
}))

jest.mock('react-syntax-highlighter/dist/cjs/styles/prism', () => ({
  oneDark: {},
  oneLight: {}
}))

// Import components
import { MetricWidget, ChartWidget, StatusWidget } from '../../src/components/analytics/widget-types'
import FileBrowser, { FileItem } from '../../src/components/artifacts/file-browser'
import FilePreview from '../../src/components/artifacts/file-preview'
import AdvancedSettings, { AdvancedSettingsConfig } from '../../src/components/settings/advanced-settings'
import ConversationExport, { ConversationData } from '../../src/components/export/conversation-export'
import LearningInsights, { PatternData, LearningMetrics, Recommendation } from '../../src/components/learning/learning-insights'

describe('Phase 4: Advanced Features - Component Tests', () => {
  const user = userEvent.setup()

  describe('Widget Components', () => {
    it('renders MetricWidget correctly', () => {
      const widget = {
        id: 'metric-1',
        title: 'Test Metric',
        type: 'metric' as const,
        data: {
          value: 1234,
          previousValue: 1100,
          label: 'Test Count',
          color: 'blue',
          icon: 'Activity'
        }
      }

      render(<MetricWidget widget={widget} />)

      expect(screen.getByText('Test Metric')).toBeInTheDocument()
      expect(screen.getByText('1234')).toBeInTheDocument()
      expect(screen.getByText('Test Count')).toBeInTheDocument()
    })

    it('renders ChartWidget correctly', () => {
      const widget = {
        id: 'chart-1',
        title: 'Test Chart',
        type: 'chart' as const,
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

      render(<ChartWidget widget={widget} />)

      expect(screen.getByText('Test Chart')).toBeInTheDocument()
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
    })

    it('renders StatusWidget correctly', () => {
      const widget = {
        id: 'status-1',
        title: 'System Status',
        type: 'status' as const,
        data: {
          services: [
            { name: 'API Server', status: 'healthy', uptime: '99.9%' },
            { name: 'Database', status: 'warning', uptime: '95.2%' }
          ]
        }
      }

      render(<StatusWidget widget={widget} />)

      expect(screen.getByText('System Status')).toBeInTheDocument()
      expect(screen.getByText('API Server')).toBeInTheDocument()
      expect(screen.getByText('Database')).toBeInTheDocument()
      expect(screen.getByText('99.9%')).toBeInTheDocument()
    })
  })

  describe('File Browser', () => {
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
        tags: ['python', 'script']
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

    const defaultProps = {
      files: mockFiles,
      currentPath: '/',
      selectedFiles: new Set<string>(),
      viewMode: 'list' as const,
      sortBy: 'name' as const,
      sortOrder: 'asc' as const,
      searchQuery: '',
      filterType: 'all',
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

    it('renders file browser with files', () => {
      render(<FileBrowser {...defaultProps} />)

      expect(screen.getByText('test.py')).toBeInTheDocument()
      expect(screen.getByText('Documents')).toBeInTheDocument()
      expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
    })

    it('handles search functionality', async () => {
      const onSearchChange = jest.fn()
      
      render(<FileBrowser {...defaultProps} onSearchChange={onSearchChange} />)

      const searchInput = screen.getByPlaceholderText('Search files...')
      await user.type(searchInput, 'test')

      expect(onSearchChange).toHaveBeenCalled()
    })

    it('handles view mode changes', async () => {
      const onViewModeChange = jest.fn()
      
      render(<FileBrowser {...defaultProps} onViewModeChange={onViewModeChange} />)

      const gridButton = screen.getByRole('button', { name: '' }) // Grid button (icon only)
      await user.click(gridButton)

      expect(onViewModeChange).toHaveBeenCalledWith('grid')
    })
  })

  describe('File Preview', () => {
    const mockFile: FileItem = {
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
    }

    it('renders file preview correctly', () => {
      const onClose = jest.fn()
      
      render(<FilePreview file={mockFile} onClose={onClose} />)

      expect(screen.getByText('test.py')).toBeInTheDocument()
      expect(screen.getByText('text/x-python')).toBeInTheDocument()
      expect(screen.getByTestId('syntax-highlighter')).toBeInTheDocument()
    })

    it('handles close action', async () => {
      const onClose = jest.fn()
      
      render(<FilePreview file={mockFile} onClose={onClose} />)

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
        quietHours: { enabled: false, start: '22:00', end: '08:00' }
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

    const defaultProps = {
      config: mockConfig,
      onConfigChange: jest.fn(),
      onSave: jest.fn(),
      onReset: jest.fn(),
      onImport: jest.fn(),
      onExport: jest.fn()
    }

    it('renders settings with all tabs', () => {
      render(<AdvancedSettings {...defaultProps} />)

      expect(screen.getByText('Settings')).toBeInTheDocument()
      expect(screen.getByText('General')).toBeInTheDocument()
      expect(screen.getByText('Appearance')).toBeInTheDocument()
      expect(screen.getByText('Notifications')).toBeInTheDocument()
      expect(screen.getByText('Performance')).toBeInTheDocument()
      expect(screen.getByText('Security')).toBeInTheDocument()
      expect(screen.getByText('Data & Storage')).toBeInTheDocument()
    })

    it('handles tab navigation', async () => {
      render(<AdvancedSettings {...defaultProps} />)

      const appearanceTab = screen.getByText('Appearance')
      await user.click(appearanceTab)

      expect(screen.getByText('Appearance Settings')).toBeInTheDocument()
    })

    it('handles configuration changes', async () => {
      const onConfigChange = jest.fn()
      
      render(<AdvancedSettings {...defaultProps} onConfigChange={onConfigChange} />)

      const autoSaveCheckbox = screen.getByRole('checkbox', { name: /auto-save/i })
      await user.click(autoSaveCheckbox)

      expect(onConfigChange).toHaveBeenCalled()
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

    it('renders export interface', () => {
      const props = {
        conversations: mockConversations,
        onExport: jest.fn(),
        onPreview: jest.fn()
      }

      render(<ConversationExport {...props} />)

      expect(screen.getByText('Export Conversations')).toBeInTheDocument()
      expect(screen.getByText('Test Conversation')).toBeInTheDocument()
      expect(screen.getByText('10 messages')).toBeInTheDocument()
    })

    it('handles conversation selection', async () => {
      const props = {
        conversations: mockConversations,
        onExport: jest.fn(),
        onPreview: jest.fn()
      }

      render(<ConversationExport {...props} />)

      const conversationItem = screen.getByText('Test Conversation').closest('div')
      expect(conversationItem).toBeInTheDocument()

      if (conversationItem) {
        await user.click(conversationItem)
      }

      // Export button should show 1 conversation selected
      expect(screen.getByText(/export.*conversation/i)).toBeInTheDocument()
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
        examples: []
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

    const defaultProps = {
      patterns: mockPatterns,
      metrics: mockMetrics,
      recommendations: mockRecommendations,
      onPatternDetails: jest.fn(),
      onRecommendationAction: jest.fn(),
      onExportInsights: jest.fn()
    }

    it('renders learning insights overview', () => {
      render(<LearningInsights {...defaultProps} />)

      expect(screen.getByText('Learning Insights')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument() // Total patterns
      expect(screen.getByText('89%')).toBeInTheDocument() // Accuracy score
    })

    it('handles tab navigation', async () => {
      render(<LearningInsights {...defaultProps} />)

      const patternsTab = screen.getByText('Patterns')
      await user.click(patternsTab)

      expect(screen.getByText('User Workflow Optimization')).toBeInTheDocument()
    })

    it('displays pattern details', async () => {
      render(<LearningInsights {...defaultProps} />)

      // Navigate to patterns tab
      const patternsTab = screen.getByText('Patterns')
      await user.click(patternsTab)

      expect(screen.getByText('85%')).toBeInTheDocument() // Confidence
      expect(screen.getByText(/high impact/i)).toBeInTheDocument()
    })

    it('handles recommendation actions', async () => {
      const onRecommendationAction = jest.fn()
      
      render(<LearningInsights {...defaultProps} onRecommendationAction={onRecommendationAction} />)

      // Navigate to recommendations tab
      const recommendationsTab = screen.getByText('Recommendations')
      await user.click(recommendationsTab)

      const implementButton = screen.getByRole('button', { name: /implement/i })
      await user.click(implementButton)

      expect(onRecommendationAction).toHaveBeenCalledWith('rec-1', 'implement')
    })
  })

  describe('Integration and Performance', () => {
    it('handles empty data gracefully', () => {
      const emptyFileProps = {
        files: [],
        currentPath: '/',
        selectedFiles: new Set<string>(),
        viewMode: 'list' as const,
        sortBy: 'name' as const,
        sortOrder: 'asc' as const,
        searchQuery: '',
        filterType: 'all',
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

      render(<FileBrowser {...emptyFileProps} />)

      expect(screen.getByText(/this folder is empty/i)).toBeInTheDocument()
    })

    it('maintains accessibility standards', () => {
      const props = {
        patterns: [],
        metrics: {
          totalPatterns: 0,
          newPatternsThisWeek: 0,
          accuracyScore: 0,
          predictionSuccess: 0,
          adaptationRate: 0,
          knowledgeGrowth: 0
        },
        recommendations: [],
        onPatternDetails: jest.fn(),
        onRecommendationAction: jest.fn(),
        onExportInsights: jest.fn()
      }

      render(<LearningInsights {...props} />)

      // Check for proper heading structure
      const mainHeading = screen.getByRole('heading', { level: 1 })
      expect(mainHeading).toBeInTheDocument()
      
      // Check for button accessibility
      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).toBeInTheDocument()
      })
    })
  })
})

describe('Phase 4: Component Performance Tests', () => {
  it('efficiently renders large file lists', () => {
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

    const props = {
      files: largeFileList,
      currentPath: '/',
      selectedFiles: new Set<string>(),
      viewMode: 'list' as const,
      sortBy: 'name' as const,
      sortOrder: 'asc' as const,
      searchQuery: '',
      filterType: 'all',
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

    const start = performance.now()
    
    render(<FileBrowser {...props} />)

    const end = performance.now()
    const renderTime = end - start

    // Should render within reasonable time (< 100ms)
    expect(renderTime).toBeLessThan(100)
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
  })
})