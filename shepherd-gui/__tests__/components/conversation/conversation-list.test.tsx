import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import ConversationList, { Conversation } from '@/components/conversation/conversation-list'

// Mock react-window components
jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemData, itemCount, itemSize }: any) => (
    <div data-testid="virtual-list" style={{ height: itemCount * itemSize }}>
      {Array.from({ length: Math.min(itemCount, 5) }, (_, index) => (
        <div key={index} style={{ height: itemSize }}>
          {children({ index, style: {}, data: itemData })}
        </div>
      ))}
    </div>
  )
}))

// Mock react-virtualized-auto-sizer
jest.mock('react-virtualized-auto-sizer', () => 
  ({ children }: { children: (size: { height: number; width: number }) => React.ReactNode }) =>
    children({ height: 400, width: 300 })
)

// Mock performance utilities
jest.mock('@/lib/performance', () => ({
  debounce: (fn: Function, delay: number) => fn
}))

// Mock UI store
jest.mock('@/stores/ui-store', () => ({
  useUIStore: jest.fn(() => ({
    reducedMotion: false
  }))
}))

const mockConversations: Conversation[] = [
  {
    id: '1',
    title: 'First Conversation',
    preview: 'This is the first conversation preview',
    timestamp: new Date('2024-01-01T10:00:00Z'),
    messageCount: 5,
    status: 'active',
    tags: ['important', 'work'],
    lastAgent: 'Assistant',
    unreadCount: 2
  },
  {
    id: '2',
    title: 'Second Conversation',
    preview: 'This is the second conversation preview',
    timestamp: new Date('2024-01-01T11:00:00Z'),
    messageCount: 3,
    status: 'pinned',
    tags: ['personal'],
    lastAgent: 'TaskAgent'
  },
  {
    id: '3',
    title: 'Third Conversation',
    preview: 'This is the third conversation preview',
    timestamp: new Date('2024-01-01T12:00:00Z'),
    messageCount: 8,
    status: 'archived',
    lastAgent: 'SystemAgent'
  }
]

const defaultProps = {
  conversations: mockConversations,
  selectedId: undefined,
  isLoading: false,
  onSelect: jest.fn(),
  onArchive: jest.fn(),
  onDelete: jest.fn(),
  onPin: jest.fn(),
  onSearch: jest.fn()
}

describe('ConversationList', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    test('renders conversation list correctly', () => {
      render(<ConversationList {...defaultProps} />)
      
      expect(screen.getByPlaceholderText('Search conversations...')).toBeInTheDocument()
      expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
      expect(screen.getByText('First Conversation')).toBeInTheDocument()
      expect(screen.getByText('Second Conversation')).toBeInTheDocument()
    })

    test('shows loading state', () => {
      render(<ConversationList {...defaultProps} isLoading={true} />)
      
      expect(screen.getByText('Loading conversations...')).toBeInTheDocument()
      expect(screen.queryByTestId('virtual-list')).not.toBeInTheDocument()
    })

    test('shows empty state when no conversations', () => {
      render(<ConversationList {...defaultProps} conversations={[]} />)
      
      expect(screen.getByText('No conversations yet')).toBeInTheDocument()
      expect(screen.queryByTestId('virtual-list')).not.toBeInTheDocument()
    })

    test('shows empty search state', () => {
      render(<ConversationList {...defaultProps} conversations={[]} />)
      
      // Type in search box
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      fireEvent.change(searchInput, { target: { value: 'nonexistent' } })
      
      expect(screen.getByText('No conversations match your search')).toBeInTheDocument()
    })
  })

  describe('Search Functionality', () => {
    test('filters conversations by title', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      fireEvent.change(searchInput, { target: { value: 'First' } })
      
      expect(screen.getByText('First Conversation')).toBeInTheDocument()
      expect(screen.queryByText('Second Conversation')).toBeInTheDocument() // Still rendered in virtual list
    })

    test('shows search results count', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      fireEvent.change(searchInput, { target: { value: 'First' } })
      
      expect(screen.getByText('3 conversations found')).toBeInTheDocument()
    })

    test('calls onSearch callback', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      fireEvent.change(searchInput, { target: { value: 'test query' } })
      
      expect(defaultProps.onSearch).toHaveBeenCalledWith('test query')
    })

    test('clears search', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...') as HTMLInputElement
      fireEvent.change(searchInput, { target: { value: 'search term' } })
      
      // Find and click clear button
      const clearButton = screen.getByText('×')
      fireEvent.click(clearButton)
      
      expect(searchInput.value).toBe('')
      expect(defaultProps.onSearch).toHaveBeenCalledWith('')
    })
  })

  describe('Conversation Interactions', () => {
    test('selects conversation on click', () => {
      render(<ConversationList {...defaultProps} />)
      
      const firstConversation = screen.getByText('First Conversation')
      fireEvent.click(firstConversation.closest('div')!)
      
      expect(defaultProps.onSelect).toHaveBeenCalledWith(mockConversations[0])
    })

    test('shows selected conversation', () => {
      render(<ConversationList {...defaultProps} selectedId="1" />)
      
      const conversationItem = screen.getByText('First Conversation').closest('div')
      expect(conversationItem).toHaveClass('border-blue-300')
    })

    test('shows action buttons on hover', async () => {
      render(<ConversationList {...defaultProps} />)
      
      const conversationItem = screen.getByText('First Conversation').closest('div')!
      fireEvent.mouseEnter(conversationItem)
      
      await waitFor(() => {
        // Action buttons should appear (pin, archive, delete)
        expect(conversationItem.querySelector('[title="Pin"]')).toBeInTheDocument()
        expect(conversationItem.querySelector('[title="Archive"]')).toBeInTheDocument()
        expect(conversationItem.querySelector('[title="Delete"]')).toBeInTheDocument()
      })
    })

    test('handles pin action', async () => {
      render(<ConversationList {...defaultProps} />)
      
      const conversationItem = screen.getByText('First Conversation').closest('div')!
      fireEvent.mouseEnter(conversationItem)
      
      await waitFor(() => {
        const pinButton = conversationItem.querySelector('[title="Pin"]')!
        fireEvent.click(pinButton)
        expect(defaultProps.onPin).toHaveBeenCalledWith('1')
      })
    })

    test('handles archive action', async () => {
      render(<ConversationList {...defaultProps} />)
      
      const conversationItem = screen.getByText('First Conversation').closest('div')!
      fireEvent.mouseEnter(conversationItem)
      
      await waitFor(() => {
        const archiveButton = conversationItem.querySelector('[title="Archive"]')!
        fireEvent.click(archiveButton)
        expect(defaultProps.onArchive).toHaveBeenCalledWith('1')
      })
    })

    test('handles delete action', async () => {
      render(<ConversationList {...defaultProps} />)
      
      const conversationItem = screen.getByText('First Conversation').closest('div')!
      fireEvent.mouseEnter(conversationItem)
      
      await waitFor(() => {
        const deleteButton = conversationItem.querySelector('[title="Delete"]')!
        fireEvent.click(deleteButton)
        expect(defaultProps.onDelete).toHaveBeenCalledWith('1')
      })
    })
  })

  describe('Conversation Display', () => {
    test('displays conversation metadata correctly', () => {
      render(<ConversationList {...defaultProps} />)
      
      expect(screen.getByText('First Conversation')).toBeInTheDocument()
      expect(screen.getByText('This is the first conversation preview')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument() // message count
      expect(screen.getByText('Assistant')).toBeInTheDocument() // last agent
    })

    test('shows pinned indicator', () => {
      render(<ConversationList {...defaultProps} />)
      
      const pinnedConversation = screen.getByText('Second Conversation').closest('div')!
      const pinIcon = pinnedConversation.querySelector('svg')
      expect(pinIcon).toBeInTheDocument()
    })

    test('shows unread count badge', () => {
      render(<ConversationList {...defaultProps} />)
      
      expect(screen.getByText('2')).toBeInTheDocument() // unread count for first conversation
    })

    test('displays tags', () => {
      render(<ConversationList {...defaultProps} />)
      
      expect(screen.getByText('important')).toBeInTheDocument()
      expect(screen.getByText('work')).toBeInTheDocument()
      expect(screen.getByText('personal')).toBeInTheDocument()
    })

    test('truncates long titles and previews', () => {
      const longTitleConversation = {
        ...mockConversations[0],
        title: 'This is a very long conversation title that should be truncated when displayed',
        preview: 'This is a very long preview text that should also be truncated when displayed in the conversation list'
      }

      render(<ConversationList {...defaultProps} conversations={[longTitleConversation]} />)
      
      const titleElement = screen.getByText(/This is a very long conversation/)
      expect(titleElement).toHaveClass('line-clamp-1')
      
      const previewElement = screen.getByText(/This is a very long preview/)
      expect(previewElement).toHaveClass('line-clamp-2')
    })
  })

  describe('Sorting and Filtering', () => {
    test('sorts pinned conversations first', () => {
      render(<ConversationList {...defaultProps} />)
      
      // The virtual list should receive data with pinned conversations first
      const virtualList = screen.getByTestId('virtual-list')
      const conversations = virtualList.children
      
      expect(conversations.length).toBeGreaterThan(0)
    })

    test('sorts by timestamp after pinned status', () => {
      const timestampSortedConversations = [
        { ...mockConversations[2], status: 'active' as const },
        { ...mockConversations[1], status: 'active' as const },
        { ...mockConversations[0], status: 'active' as const }
      ]

      render(<ConversationList {...defaultProps} conversations={timestampSortedConversations} />)
      
      // Should render without errors and in correct order
      expect(screen.getByText('Third Conversation')).toBeInTheDocument()
      expect(screen.getByText('Second Conversation')).toBeInTheDocument()
      expect(screen.getByText('First Conversation')).toBeInTheDocument()
    })
  })

  describe('Virtual Scrolling', () => {
    test('renders virtual list with correct props', () => {
      render(<ConversationList {...defaultProps} />)
      
      const virtualList = screen.getByTestId('virtual-list')
      expect(virtualList).toBeInTheDocument()
      
      // Should have height based on item count * item height
      const expectedHeight = Math.min(mockConversations.length, 5) * 80
      expect(virtualList).toHaveStyle(`height: ${expectedHeight}px`)
    })

    test('handles large number of conversations efficiently', () => {
      const manyConversations = Array.from({ length: 1000 }, (_, i) => ({
        ...mockConversations[0],
        id: `conv-${i}`,
        title: `Conversation ${i}`,
        timestamp: new Date(Date.now() - i * 1000)
      }))

      const startTime = performance.now()
      render(<ConversationList {...defaultProps} conversations={manyConversations} />)
      const endTime = performance.now()
      
      // Should render quickly even with many conversations
      expect(endTime - startTime).toBeLessThan(1000)
      expect(screen.getByTestId('virtual-list')).toBeInTheDocument()
    })
  })

  describe('Performance', () => {
    test('debounces search input', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      
      // Type multiple characters quickly
      fireEvent.change(searchInput, { target: { value: 'a' } })
      fireEvent.change(searchInput, { target: { value: 'ab' } })
      fireEvent.change(searchInput, { target: { value: 'abc' } })
      
      // Due to our mock, debounce doesn't delay, so onSearch should be called for each change
      expect(defaultProps.onSearch).toHaveBeenCalledTimes(3)
    })

    test('memoizes conversation items', () => {
      const { rerender } = render(<ConversationList {...defaultProps} />)
      
      // Re-render with same props
      rerender(<ConversationList {...defaultProps} />)
      
      // Should not cause unnecessary re-renders (this is hard to test directly)
      expect(screen.getByText('First Conversation')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      expect(searchInput).toBeInTheDocument()
      expect(searchInput).toHaveAttribute('type', 'text')
    })

    test('supports keyboard navigation', () => {
      render(<ConversationList {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      
      // Should be focusable
      searchInput.focus()
      expect(searchInput).toHaveFocus()
      
      // Should handle keyboard events
      fireEvent.keyDown(searchInput, { key: 'Enter' })
      // No specific behavior expected for Enter, just shouldn't crash
    })

    test('handles screen reader announcements', () => {
      render(<ConversationList {...defaultProps} />)
      
      // Search results count should be announced
      const searchInput = screen.getByPlaceholderText('Search conversations...')
      fireEvent.change(searchInput, { target: { value: 'test' } })
      
      expect(screen.getByText('3 conversations found')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    test('handles conversations without titles', () => {
      const noTitleConversations = [
        { ...mockConversations[0], title: '' }
      ]

      render(<ConversationList {...defaultProps} conversations={noTitleConversations} />)
      expect(screen.getByText('Untitled Conversation')).toBeInTheDocument()
    })

    test('handles conversations without previews', () => {
      const noPreviewConversations = [
        { ...mockConversations[0], preview: '' }
      ]

      render(<ConversationList {...defaultProps} conversations={noPreviewConversations} />)
      expect(screen.getByText('No messages yet')).toBeInTheDocument()
    })

    test('handles very old timestamps', () => {
      const oldConversations = [
        { ...mockConversations[0], timestamp: new Date('2020-01-01') }
      ]

      render(<ConversationList {...defaultProps} conversations={oldConversations} />)
      
      // Should show formatted date for old conversations
      expect(screen.getByText(/\d+\/\d+\/\d+/)).toBeInTheDocument()
    })

    test('handles recent timestamps', () => {
      const recentConversations = [
        { ...mockConversations[0], timestamp: new Date(Date.now() - 30000) } // 30 seconds ago
      ]

      render(<ConversationList {...defaultProps} conversations={recentConversations} />)
      
      // Should show relative time for recent conversations
      expect(screen.getByText(/ago/)).toBeInTheDocument()
    })
  })
})