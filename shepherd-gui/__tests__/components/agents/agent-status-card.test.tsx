import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import AgentStatusCard from '@/components/agents/agent-status-card'
import type { AgentStatus } from '@/components/agents/agent-status-card'

// Mock UI store
jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    reducedMotion: false,
    theme: 'light'
  }))
}))

const mockAgent: AgentStatus = {
  id: 'agent-1',
  name: 'Test Agent',
  type: 'task',
  status: 'active',
  currentTask: 'Processing data analysis',
  tasksCompleted: 42,
  efficiency: 0.87,
  memoryUsage: 512,
  cpuUsage: 45,
  lastActive: new Date('2024-01-01T10:00:00Z'),
  uptime: 3600, // 1 hour
  tools: ['filesystem', 'analysis', 'web-search', 'calculator', 'database'],
  errorCount: 2,
  successRate: 0.95
}

const defaultProps = {
  agent: mockAgent,
  onPause: jest.fn(),
  onResume: jest.fn(),
  onRestart: jest.fn(),
  onViewDetails: jest.fn()
}

describe('AgentStatusCard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    test('renders agent information correctly', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      expect(screen.getByText('Test Agent')).toBeInTheDocument()
      expect(screen.getByText('Task')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument()
      expect(screen.getByText('87%')).toBeInTheDocument()
    })

    test('renders compact mode correctly', () => {
      render(<AgentStatusCard {...defaultProps} compact={true} />)
      
      expect(screen.getByText('Test Agent')).toBeInTheDocument()
      expect(screen.getByText('Task')).toBeInTheDocument()
      expect(screen.getByText('42 tasks')).toBeInTheDocument()
      expect(screen.getByText('87%')).toBeInTheDocument()
      expect(screen.getByText('512MB')).toBeInTheDocument()
    })

    test('displays current task when provided', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      expect(screen.getByText('Current Task:')).toBeInTheDocument()
      expect(screen.getByText('Processing data analysis')).toBeInTheDocument()
    })

    test('hides current task section when not provided', () => {
      const agentWithoutTask = { ...mockAgent, currentTask: undefined }
      render(<AgentStatusCard {...defaultProps} agent={agentWithoutTask} />)
      
      expect(screen.queryByText('Current Task:')).not.toBeInTheDocument()
    })
  })

  describe('Agent Types', () => {
    const agentTypes: Array<{ type: AgentStatus['type']; label: string; colorClass: string }> = [
      { type: 'system', label: 'System', colorClass: 'bg-blue-500' },
      { type: 'task', label: 'Task', colorClass: 'bg-green-500' },
      { type: 'research', label: 'Research', colorClass: 'bg-purple-500' },
      { type: 'creative', label: 'Creative', colorClass: 'bg-pink-500' },
      { type: 'analytical', label: 'Analytical', colorClass: 'bg-indigo-500' },
      { type: 'communication', label: 'Communication', colorClass: 'bg-teal-500' }
    ]

    agentTypes.forEach(({ type, label, colorClass }) => {
      test(`renders ${type} agent type correctly`, () => {
        const agentWithType = { ...mockAgent, type }
        const { container } = render(<AgentStatusCard {...defaultProps} agent={agentWithType} />)
        
        expect(screen.getByText(label)).toBeInTheDocument()
        expect(container.querySelector(`.${colorClass.replace('-', '\\-')}`)).toBeInTheDocument()
      })
    })
  })

  describe('Agent Status States', () => {
    const statusStates: Array<{ status: AgentStatus['status']; label: string; colorClass: string }> = [
      { status: 'idle', label: 'Idle', colorClass: 'text-gray-500' },
      { status: 'active', label: 'Active', colorClass: 'text-green-600' },
      { status: 'busy', label: 'Busy', colorClass: 'text-orange-600' },
      { status: 'error', label: 'Error', colorClass: 'text-red-600' },
      { status: 'paused', label: 'Paused', colorClass: 'text-yellow-600' }
    ]

    statusStates.forEach(({ status, label, colorClass }) => {
      test(`renders ${status} status correctly`, () => {
        const agentWithStatus = { ...mockAgent, status }
        const { container } = render(<AgentStatusCard {...defaultProps} agent={agentWithStatus} />)
        
        expect(screen.getByText(label)).toBeInTheDocument()
        expect(container.querySelector(`.${colorClass.replace('-', '\\-')}`)).toBeInTheDocument()
      })
    })

    test('shows pulse animation for active status', () => {
      const activeAgent = { ...mockAgent, status: 'active' as const }
      const { useUIStore } = require('@/stores/ui-store')
      useUIStore.mockReturnValue({ reducedMotion: false, theme: 'light' })
      
      const { container } = render(<AgentStatusCard {...defaultProps} agent={activeAgent} />)
      
      const pulseElement = container.querySelector('.animate-pulse')
      expect(pulseElement).toBeInTheDocument()
    })

    test('respects reduced motion preference', () => {
      const { useUIStore } = require('@/stores/ui-store')
      useUIStore.mockReturnValue({ reducedMotion: true, theme: 'light' })
      
      const activeAgent = { ...mockAgent, status: 'active' as const }
      const { container } = render(<AgentStatusCard {...defaultProps} agent={activeAgent} />)
      
      const pulseElement = container.querySelector('.animate-pulse')
      expect(pulseElement).not.toBeInTheDocument()
    })
  })

  describe('Resource Usage Display', () => {
    test('formats memory usage correctly', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('512MB')).toBeInTheDocument()
    })

    test('formats large memory usage in GB', () => {
      const agentWithLargeMemory = { ...mockAgent, memoryUsage: 2048 }
      render(<AgentStatusCard {...defaultProps} agent={agentWithLargeMemory} />)
      expect(screen.getByText('2.0GB')).toBeInTheDocument()
    })

    test('displays CPU usage when provided', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('45%')).toBeInTheDocument()
    })

    test('hides CPU usage when not provided', () => {
      const agentWithoutCpu = { ...mockAgent, cpuUsage: undefined }
      render(<AgentStatusCard {...defaultProps} agent={agentWithoutCpu} />)
      
      expect(screen.queryByText('CPU')).not.toBeInTheDocument()
    })

    test('formats uptime correctly', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('1h')).toBeInTheDocument()
      
      // Test different uptime formats
      const agentWithMinutes = { ...mockAgent, uptime: 300 } // 5 minutes
      const { rerender } = render(<AgentStatusCard {...defaultProps} agent={agentWithMinutes} />)
      expect(screen.getByText('5m')).toBeInTheDocument()
      
      const agentWithSeconds = { ...mockAgent, uptime: 30 }
      rerender(<AgentStatusCard {...defaultProps} agent={agentWithSeconds} />)
      expect(screen.getByText('30s')).toBeInTheDocument()
      
      const agentWithDays = { ...mockAgent, uptime: 86400 * 2 } // 2 days
      rerender(<AgentStatusCard {...defaultProps} agent={agentWithDays} />)
      expect(screen.getByText('2d')).toBeInTheDocument()
    })
  })

  describe('Success Rate and Error Handling', () => {
    test('displays success rate when provided', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('95% success')).toBeInTheDocument()
    })

    test('displays error count when present', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('2 errors')).toBeInTheDocument()
    })

    test('handles singular error count', () => {
      const agentWithOneError = { ...mockAgent, errorCount: 1 }
      render(<AgentStatusCard {...defaultProps} agent={agentWithOneError} />)
      expect(screen.getByText('1 error')).toBeInTheDocument()
    })

    test('shows error indicator in compact mode', () => {
      const agentWithErrors = { ...mockAgent, errorCount: 5 }
      const { container } = render(<AgentStatusCard {...defaultProps} agent={agentWithErrors} compact={true} />)
      
      const errorIndicator = container.querySelector('.bg-red-500')
      expect(errorIndicator).toBeInTheDocument()
    })
  })

  describe('Tools Display', () => {
    test('displays first 3 tools', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      expect(screen.getByText('filesystem')).toBeInTheDocument()
      expect(screen.getByText('analysis')).toBeInTheDocument()
      expect(screen.getByText('web-search')).toBeInTheDocument()
    })

    test('shows additional tools count', () => {
      render(<AgentStatusCard {...defaultProps} />)
      expect(screen.getByText('+2 more')).toBeInTheDocument()
    })

    test('handles agents with few tools', () => {
      const agentWithFewTools = { ...mockAgent, tools: ['filesystem'] }
      render(<AgentStatusCard {...defaultProps} agent={agentWithFewTools} />)
      
      expect(screen.getByText('filesystem')).toBeInTheDocument()
      expect(screen.queryByText('+0 more')).not.toBeInTheDocument()
    })
  })

  describe('Action Buttons', () => {
    test('shows pause button for active agent', async () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.mouseEnter(card)
      
      await waitFor(() => {
        const pauseButton = screen.getByTitle('Pause Agent')
        expect(pauseButton).toBeInTheDocument()
      })
    })

    test('shows resume button for paused agent', async () => {
      const pausedAgent = { ...mockAgent, status: 'paused' as const }
      render(<AgentStatusCard {...defaultProps} agent={pausedAgent} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.mouseEnter(card)
      
      await waitFor(() => {
        const resumeButton = screen.getByTitle('Resume Agent')
        expect(resumeButton).toBeInTheDocument()
      })
    })

    test('calls onPause when pause button clicked', async () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.mouseEnter(card)
      
      await waitFor(() => {
        const pauseButton = screen.getByTitle('Pause Agent')
        fireEvent.click(pauseButton)
        expect(defaultProps.onPause).toHaveBeenCalledWith('agent-1')
      })
    })

    test('calls onResume when resume button clicked', async () => {
      const pausedAgent = { ...mockAgent, status: 'paused' as const }
      render(<AgentStatusCard {...defaultProps} agent={pausedAgent} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.mouseEnter(card)
      
      await waitFor(() => {
        const resumeButton = screen.getByTitle('Resume Agent')
        fireEvent.click(resumeButton)
        expect(defaultProps.onResume).toHaveBeenCalledWith('agent-1')
      })
    })

    test('calls onViewDetails when details link clicked', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      const detailsLink = screen.getByText('View Details →')
      fireEvent.click(detailsLink)
      
      expect(defaultProps.onViewDetails).toHaveBeenCalledWith('agent-1')
    })

    test('calls onViewDetails when compact card clicked', () => {
      render(<AgentStatusCard {...defaultProps} compact={true} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.click(card)
      
      expect(defaultProps.onViewDetails).toHaveBeenCalledWith('agent-1')
    })
  })

  describe('Timestamp Display', () => {
    test('displays last active time', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      expect(screen.getByText(/Last active:/)).toBeInTheDocument()
      expect(screen.getByText(/10:00:00 AM/)).toBeInTheDocument()
    })

    test('handles different timestamp formats', () => {
      const agentWithDifferentTime = { 
        ...mockAgent, 
        lastActive: new Date('2024-01-01T15:30:45Z') 
      }
      render(<AgentStatusCard {...defaultProps} agent={agentWithDifferentTime} />)
      
      expect(screen.getByText(/3:30:45 PM/)).toBeInTheDocument()
    })
  })

  describe('Theme Support', () => {
    test('applies dark theme styles', () => {
      const { useUIStore } = require('@/stores/ui-store')
      useUIStore.mockReturnValue({
        reducedMotion: false,
        theme: 'dark'
      })

      const { container } = render(<AgentStatusCard {...defaultProps} />)
      
      // Check for dark theme classes
      const darkElements = container.querySelectorAll('.dark\\:bg-gray-800')
      expect(darkElements.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    test('has proper button roles and labels', async () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      const card = screen.getByText('Test Agent').closest('div')!
      fireEvent.mouseEnter(card)
      
      await waitFor(() => {
        const pauseButton = screen.getByTitle('Pause Agent')
        expect(pauseButton).toHaveAttribute('title', 'Pause Agent')
        expect(pauseButton.tagName).toBe('BUTTON')
      })
    })

    test('supports keyboard navigation', () => {
      render(<AgentStatusCard {...defaultProps} />)
      
      const detailsLink = screen.getByText('View Details →')
      
      // Should be focusable
      detailsLink.focus()
      expect(detailsLink).toHaveFocus()
      
      // Should respond to Enter key
      fireEvent.keyDown(detailsLink, { key: 'Enter' })
      expect(defaultProps.onViewDetails).toHaveBeenCalledWith('agent-1')
    })
  })

  describe('Performance', () => {
    test('memoizes component correctly', () => {
      const { rerender } = render(<AgentStatusCard {...defaultProps} />)
      
      // Re-render with same props
      rerender(<AgentStatusCard {...defaultProps} />)
      
      // Component should be memoized
      expect(AgentStatusCard.displayName).toBe('AgentStatusCard')
    })

    test('handles frequent updates efficiently', () => {
      const { rerender } = render(<AgentStatusCard {...defaultProps} />)
      
      // Simulate frequent updates
      const startTime = performance.now()
      
      for (let i = 0; i < 10; i++) {
        const updatedAgent = {
          ...mockAgent,
          cpuUsage: Math.random() * 100,
          memoryUsage: 500 + Math.random() * 100
        }
        rerender(<AgentStatusCard {...defaultProps} agent={updatedAgent} />)
      }
      
      const endTime = performance.now()
      
      // Should handle updates efficiently
      expect(endTime - startTime).toBeLessThan(100)
    })
  })

  describe('Edge Cases', () => {
    test('handles missing optional properties', () => {
      const minimalAgent: AgentStatus = {
        id: 'minimal-agent',
        name: 'Minimal Agent',
        type: 'system',
        status: 'idle',
        tasksCompleted: 0,
        efficiency: 0,
        memoryUsage: 0,
        lastActive: new Date(),
        uptime: 0,
        tools: []
      }

      render(<AgentStatusCard {...defaultProps} agent={minimalAgent} />)
      
      expect(screen.getByText('Minimal Agent')).toBeInTheDocument()
      expect(screen.getByText('System')).toBeInTheDocument()
      expect(screen.getByText('0')).toBeInTheDocument() // tasks completed
    })

    test('handles very large numbers', () => {
      const agentWithLargeNumbers = {
        ...mockAgent,
        tasksCompleted: 999999,
        memoryUsage: 10240, // 10GB
        uptime: 86400 * 365 // 1 year
      }

      render(<AgentStatusCard {...defaultProps} agent={agentWithLargeNumbers} />)
      
      expect(screen.getByText('999999')).toBeInTheDocument()
      expect(screen.getByText('10.0GB')).toBeInTheDocument()
      expect(screen.getByText('365d')).toBeInTheDocument()
    })

    test('handles zero values', () => {
      const agentWithZeros = {
        ...mockAgent,
        tasksCompleted: 0,
        efficiency: 0,
        memoryUsage: 0,
        cpuUsage: 0,
        uptime: 0
      }

      render(<AgentStatusCard {...defaultProps} agent={agentWithZeros} />)
      
      expect(screen.getByText('0')).toBeInTheDocument() // tasks
      expect(screen.getByText('0%')).toBeInTheDocument() // efficiency
      expect(screen.getByText('0MB')).toBeInTheDocument() // memory
      expect(screen.getByText('0s')).toBeInTheDocument() // uptime
    })
  })
})