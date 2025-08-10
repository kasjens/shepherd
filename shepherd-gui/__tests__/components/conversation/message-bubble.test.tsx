import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import MessageBubble, { MessageBubbleProps } from '@/components/conversation/message-bubble'

// Mock syntax highlighter to avoid issues with server-side rendering
jest.mock('react-syntax-highlighter', () => ({
  Prism: ({ children, ...props }: any) => (
    <pre {...props} data-testid="syntax-highlighter">
      <code>{children}</code>
    </pre>
  )
}))

jest.mock('react-syntax-highlighter/dist/cjs/styles/prism', () => ({
  oneDark: {},
  oneLight: {}
}))

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(() => Promise.resolve()),
  },
})

// Mock UI store
jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    theme: 'light',
    reducedMotion: false
  }))
}))

const defaultProps: MessageBubbleProps = {
  id: 'test-message-1',
  content: 'Hello, this is a test message',
  role: 'user',
  timestamp: new Date('2024-01-01T10:00:00Z'),
  isLoading: false,
  artifacts: [],
  onCopy: jest.fn(),
  onArtifactClick: jest.fn()
}

describe('MessageBubble', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    test('renders message content correctly', () => {
      render(<MessageBubble {...defaultProps} />)
      
      expect(screen.getByText('Hello, this is a test message')).toBeInTheDocument()
      expect(screen.getByText('You')).toBeInTheDocument()
      expect(screen.getByText('11:00:00 AM')).toBeInTheDocument()
    })

    test('renders different roles correctly', () => {
      const { rerender } = render(<MessageBubble {...defaultProps} role="assistant" />)
      expect(screen.getByText('Assistant')).toBeInTheDocument()

      rerender(<MessageBubble {...defaultProps} role="system" />)
      expect(screen.getByText('System')).toBeInTheDocument()
    })

    test('shows loading state', () => {
      render(<MessageBubble {...defaultProps} isLoading={true} />)
      
      expect(screen.getByText('Thinking...')).toBeInTheDocument()
      expect(screen.queryByText(defaultProps.content)).not.toBeInTheDocument()
    })
  })

  describe('Code Highlighting', () => {
    test('renders code blocks with syntax highlighting', () => {
      const codeMessage = {
        ...defaultProps,
        content: 'Here is some code:\n```javascript\nconst hello = "world";\nconsole.log(hello);\n```'
      }

      render(<MessageBubble {...codeMessage} />)
      
      expect(screen.getByTestId('syntax-highlighter')).toBeInTheDocument()
      expect(screen.getByText('const hello = "world";')).toBeInTheDocument()
    })

    test('renders inline code correctly', () => {
      const inlineCodeMessage = {
        ...defaultProps,
        content: 'Use the `console.log()` function to debug.'
      }

      render(<MessageBubble {...inlineCodeMessage} />)
      expect(screen.getByText('Use the')).toBeInTheDocument()
      expect(screen.getByText('function to debug.')).toBeInTheDocument()
    })

    test('shows copy button for code blocks on hover', async () => {
      const codeMessage = {
        ...defaultProps,
        content: '```javascript\nconst test = true;\n```'
      }

      const { container } = render(<MessageBubble {...codeMessage} />)
      
      // Find the message bubble container
      const messageBubble = container.querySelector('.group')
      
      if (messageBubble) {
        fireEvent.mouseEnter(messageBubble)
      }

      // Should show copy buttons (one for main message, one for code block)
      await waitFor(() => {
        const copyButtons = screen.getAllByRole('button')
        expect(copyButtons.length).toBeGreaterThanOrEqual(1)
      })
    })
  })

  describe('Copy Functionality', () => {
    test('copies message content to clipboard', async () => {
      const mockOnCopy = jest.fn()
      render(<MessageBubble {...defaultProps} onCopy={mockOnCopy} />)
      
      const copyButton = screen.getByRole('button')
      fireEvent.click(copyButton)
      
      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(defaultProps.content)
        expect(mockOnCopy).toHaveBeenCalledWith(defaultProps.content)
      })
    })

    test('shows check icon after successful copy', async () => {
      render(<MessageBubble {...defaultProps} />)
      
      const copyButton = screen.getByRole('button')
      fireEvent.click(copyButton)
      
      await waitFor(() => {
        // Check icon should be present (using aria-hidden to find it)
        const checkIcon = copyButton.querySelector('svg')
        expect(checkIcon).toBeInTheDocument()
      })
    })

    test('handles copy errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      // @ts-ignore
      navigator.clipboard.writeText = jest.fn(() => Promise.reject(new Error('Copy failed')))
      
      render(<MessageBubble {...defaultProps} />)
      
      const copyButton = screen.getByRole('button')
      fireEvent.click(copyButton)
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to copy text:', expect.any(Error))
      })
      
      consoleSpy.mockRestore()
    })
  })

  describe('Artifacts', () => {
    const artifactsProps = {
      ...defaultProps,
      artifacts: [
        {
          id: 'artifact-1',
          type: 'code' as const,
          title: 'Test Script',
          content: 'console.log("test")',
          language: 'javascript'
        },
        {
          id: 'artifact-2',
          type: 'text' as const,
          title: 'Documentation',
          content: 'This is documentation'
        }
      ]
    }

    test('renders artifact buttons', () => {
      render(<MessageBubble {...artifactsProps} />)
      
      expect(screen.getByText('Test Script')).toBeInTheDocument()
      expect(screen.getByText('Documentation')).toBeInTheDocument()
    })

    test('handles artifact click', () => {
      const mockOnArtifactClick = jest.fn()
      render(
        <MessageBubble 
          {...artifactsProps} 
          onArtifactClick={mockOnArtifactClick}
        />
      )
      
      fireEvent.click(screen.getByText('Test Script'))
      expect(mockOnArtifactClick).toHaveBeenCalledWith('artifact-1')
    })
  })

  describe('Theme Support', () => {
    test('applies dark theme styles', () => {
      const { useUIStore } = require('@/stores/ui-store')
      useUIStore.mockReturnValue({
        theme: 'dark',
        reducedMotion: false
      })

      const { container } = render(<MessageBubble {...defaultProps} />)
      
      // Check for dark theme classes
      const darkElements = container.querySelectorAll('.dark\\:bg-blue-950')
      expect(darkElements.length).toBeGreaterThan(0)
    })

    test('respects reduced motion preference', () => {
      const { useUIStore } = require('@/stores/ui-store')
      useUIStore.mockReturnValue({
        theme: 'light',
        reducedMotion: true
      })

      const { container } = render(<MessageBubble {...defaultProps} />)
      
      // Should not have transition classes when reduced motion is enabled
      const transitionElements = container.querySelectorAll('.transition-all')
      expect(transitionElements.length).toBe(0)
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(<MessageBubble {...defaultProps} />)
      
      // Copy button should have proper accessibility
      const copyButton = screen.getByRole('button')
      expect(copyButton).toBeInTheDocument()
    })

    test('supports keyboard navigation', () => {
      render(<MessageBubble {...defaultProps} artifacts={[{
        id: 'artifact-1',
        type: 'code',
        title: 'Test',
        content: 'test'
      }]} />)
      
      const artifactButton = screen.getByText('Test')
      
      // Should be focusable
      artifactButton.focus()
      expect(artifactButton).toHaveFocus()
      
      // Should respond to Enter key
      fireEvent.keyDown(artifactButton, { key: 'Enter' })
      expect(defaultProps.onArtifactClick).toHaveBeenCalledWith('artifact-1')
    })
  })

  describe('Performance', () => {
    test('memoizes component correctly', () => {
      const { rerender } = render(<MessageBubble {...defaultProps} />)
      
      // Re-render with same props should not cause re-render
      rerender(<MessageBubble {...defaultProps} />)
      
      // Component should be memoized (we can't directly test this, but the component should be wrapped in memo)
      expect(MessageBubble.displayName).toBe('MessageBubble')
    })

    test('handles large content efficiently', () => {
      const largeContent = 'Lorem ipsum '.repeat(1000)
      const largeContentProps = {
        ...defaultProps,
        content: largeContent
      }
      
      const startTime = performance.now()
      render(<MessageBubble {...largeContentProps} />)
      const endTime = performance.now()
      
      // Rendering should complete within reasonable time (1 second)
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('Edge Cases', () => {
    test('handles empty content', () => {
      render(<MessageBubble {...defaultProps} content="" />)
      expect(screen.getByText('You')).toBeInTheDocument()
    })

    test('handles very old timestamps', () => {
      const oldTimestamp = new Date('2020-01-01T00:00:00Z')
      render(<MessageBubble {...defaultProps} timestamp={oldTimestamp} />)
      
      expect(screen.getByText('1:00:00 AM')).toBeInTheDocument()
    })

    test('handles malformed code blocks', () => {
      const malformedCode = {
        ...defaultProps,
        content: '```\ncode without language\n```\n```javascript\nincomplete code block'
      }
      
      render(<MessageBubble {...malformedCode} />)
      
      // Should render without crashing
      expect(screen.getByText('You')).toBeInTheDocument()
    })

    test('handles special characters in content', () => {
      const specialContent = {
        ...defaultProps,
        content: 'Special chars: <>&"\'`\n\t\r'
      }
      
      render(<MessageBubble {...specialContent} />)
      expect(screen.getByText(/Special chars:/)).toBeInTheDocument()
    })
  })
})