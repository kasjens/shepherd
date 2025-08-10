import { QueryClient } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { apiClient, conversationsApi, workflowsApi, ApiError } from '@/lib/api-client'
import { queryClient } from '@/lib/react-query'

// Mock fetch
global.fetch = jest.fn()

// Mock React Query client
jest.mock('@/lib/react-query', () => ({
  queryClient: {
    invalidateQueries: jest.fn(),
    setQueryData: jest.fn(),
    removeQueries: jest.fn(),
  },
  queryKeys: {
    conversations: {
      all: ['conversations'],
      list: () => ['conversations', 'list'],
      detail: (id: string) => ['conversations', 'detail', id],
      tokenUsage: (id: string) => ['conversations', 'token-usage', id],
    },
    workflows: {
      metrics: () => ['workflows', 'metrics'],
      history: () => ['workflows', 'history'],
    },
  },
  optimisticUpdates: {
    addConversation: jest.fn(),
    updateConversation: jest.fn(),
  },
  errorHandling: {
    getErrorMessage: (error: any) => error?.message || 'Unknown error',
  },
}))

const mockFetch = fetch as jest.MockedFunction<typeof fetch>

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    jest.clearAllMocks()
    
    // Mock successful response by default
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true, data: {} }),
    } as Response)
  })

  describe('ApiClient Class', () => {
    test('makes GET requests correctly', async () => {
      const responseData = { id: '1', name: 'test' }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(responseData),
      } as Response)

      const result = await apiClient.get('/test')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      )
      expect(result).toEqual(responseData)
    })

    test('makes POST requests with data', async () => {
      const requestData = { name: 'test' }
      const responseData = { id: '1', ...requestData }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 201,
        json: () => Promise.resolve(responseData),
      } as Response)

      const result = await apiClient.post('/test', requestData)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData),
        }
      )
      expect(result).toEqual(responseData)
    })

    test('handles HTTP errors correctly', async () => {
      const errorResponse = { message: 'Not found', code: 'NOT_FOUND' }
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve(errorResponse),
      } as Response)

      await expect(apiClient.get('/nonexistent')).rejects.toThrow(ApiError)
      
      try {
        await apiClient.get('/nonexistent')
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError)
        expect((error as ApiError).status).toBe(404)
        expect((error as ApiError).code).toBe('NOT_FOUND')
        expect((error as ApiError).message).toBe('Not found')
      }
    })

    test('handles network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      await expect(apiClient.get('/test')).rejects.toThrow(ApiError)
      
      try {
        await apiClient.get('/test')
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError)
        expect((error as ApiError).code).toBe('NETWORK_ERROR')
      }
    })

    test('logs slow requests in development', async () => {
      const originalEnv = process.env.NODE_ENV
      process.env.NODE_ENV = 'development'
      
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation()
      
      // Mock a slow response
      mockFetch.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({}),
          } as Response), 1100)
        )
      )

      await apiClient.get('/slow-endpoint')

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Slow API request: /slow-endpoint took')
      )

      consoleSpy.mockRestore()
      process.env.NODE_ENV = originalEnv
    })
  })

  describe('Conversations API', () => {
    test('getAll fetches conversations list', async () => {
      const conversations = [{ id: '1', title: 'Test' }]
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(conversations),
      } as Response)

      const result = await conversationsApi.getAll()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/conversations',
        expect.any(Object)
      )
      expect(result).toEqual(conversations)
    })

    test('getById fetches specific conversation', async () => {
      const conversation = { id: '1', title: 'Test Conversation' }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(conversation),
      } as Response)

      const result = await conversationsApi.getById('1')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/conversations/1',
        expect.any(Object)
      )
      expect(result).toEqual(conversation)
    })

    test('create creates new conversation', async () => {
      const newConversation = { title: 'New Conversation' }
      const createdConversation = { id: '1', ...newConversation }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 201,
        json: () => Promise.resolve(createdConversation),
      } as Response)

      const result = await conversationsApi.create(newConversation)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/conversations',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(newConversation),
        })
      )
      expect(result).toEqual(createdConversation)
    })

    test('compact initiates conversation compacting', async () => {
      const compactResult = { success: true, reduction: 0.3 }
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(compactResult),
      } as Response)

      const result = await conversationsApi.compact('1', 'context_preservation')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/conversations/1/compact',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ strategy: 'context_preservation' }),
        })
      )
      expect(result).toEqual(compactResult)
    })

    test('getTokenUsage fetches token usage data', async () => {
      const tokenUsage = { 
        current_tokens: 1500, 
        threshold: 2000, 
        usage_percentage: 0.75 
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(tokenUsage),
      } as Response)

      const result = await conversationsApi.getTokenUsage('1')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/conversations/1/token-usage',
        expect.any(Object)
      )
      expect(result).toEqual(tokenUsage)
    })
  })

  describe('Workflows API', () => {
    test('execute starts workflow execution', async () => {
      const executionData = { 
        content: 'test command', 
        sessionId: 'session1' 
      }
      const workflowResult = { 
        workflow_id: 'workflow1', 
        status: 'completed' 
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(workflowResult),
      } as Response)

      const result = await workflowsApi.execute(executionData)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/workflow/execute',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(executionData),
        })
      )
      expect(result).toEqual(workflowResult)
    })

    test('getMetrics fetches workflow metrics', async () => {
      const metrics = { 
        totalExecutions: 100, 
        successRate: 0.95, 
        averageDuration: 2.5 
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(metrics),
      } as Response)

      const result = await workflowsApi.getMetrics()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/workflows/metrics',
        expect.any(Object)
      )
      expect(result).toEqual(metrics)
    })

    test('getHistory fetches paginated history', async () => {
      const historyData = {
        items: [{ id: '1', pattern: 'sequential' }],
        total: 50,
        page: 2,
        limit: 20,
        hasMore: true
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(historyData),
      } as Response)

      const result = await workflowsApi.getHistory(2, 20)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/workflows/history?page=2&limit=20',
        expect.any(Object)
      )
      expect(result).toEqual(historyData)
    })

    test('analyzePrompt analyzes prompt without execution', async () => {
      const analysis = { 
        complexity_score: 0.7, 
        recommended_pattern: 'parallel' 
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(analysis),
      } as Response)

      const result = await workflowsApi.analyzePrompt('test prompt')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/analyze',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ content: 'test prompt' }),
        })
      )
      expect(result).toEqual(analysis)
    })
  })

  describe('Error Handling', () => {
    test('handles 400 errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ message: 'Bad Request' }),
      } as Response)

      await expect(apiClient.get('/test')).rejects.toThrow('Bad Request')
    })

    test('handles 401 errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      } as Response)

      await expect(apiClient.get('/test')).rejects.toThrow('HTTP 401')
    })

    test('handles 500 errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ message: 'Internal Server Error' }),
      } as Response)

      await expect(apiClient.get('/test')).rejects.toThrow('Internal Server Error')
    })

    test('handles JSON parsing errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('Invalid JSON')),
      } as Response)

      await expect(apiClient.get('/test')).rejects.toThrow('HTTP 500')
    })
  })

  describe('Performance Monitoring', () => {
    test('tracks request timing', async () => {
      const performanceSpy = jest.spyOn(performance, 'now')
        .mockReturnValueOnce(1000)
        .mockReturnValueOnce(1150)

      await apiClient.get('/test')

      expect(performanceSpy).toHaveBeenCalledTimes(2)
      performanceSpy.mockRestore()
    })

    test('handles concurrent requests', async () => {
      const responses = [
        { data: 'response1' },
        { data: 'response2' },
        { data: 'response3' }
      ]

      responses.forEach((response, index) => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve(response),
        } as Response)
      })

      const promises = [
        apiClient.get('/test1'),
        apiClient.get('/test2'),
        apiClient.get('/test3')
      ]

      const results = await Promise.all(promises)

      expect(results).toEqual(responses)
      expect(mockFetch).toHaveBeenCalledTimes(3)
    })
  })
})