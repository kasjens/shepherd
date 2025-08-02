/**
 * Test setup utilities for Shepherd GUI tests
 */

// Re-export everything from React Testing Library
export * from '@testing-library/react'

// Mock data for testing
export const mockAgentStatus = {
  id: 'test-agent-1',
  name: 'Test Agent',
  type: 'task',
  status: 'working' as const,
  currentTask: 'Testing functionality',
  progress: 75,
}

export const mockConversation = {
  id: 'conv-1',
  title: 'Test Conversation',
  messages: [
    {
      id: 'msg-1',
      role: 'user' as const,
      content: 'Hello, test message',
      timestamp: new Date().toISOString(),
    },
    {
      id: 'msg-2',
      role: 'assistant' as const,
      content: 'Hello! This is a test response.',
      timestamp: new Date().toISOString(),
    },
  ],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
}

// Helper functions for common test scenarios
export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0))

export const flushPromises = () => new Promise(setImmediate)