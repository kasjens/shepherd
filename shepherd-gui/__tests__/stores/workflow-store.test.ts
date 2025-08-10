import { act, renderHook } from '@testing-library/react'
import { useWorkflowStore, workflowSelectors, type WorkflowStore } from '@/stores/workflow-store'

describe('Workflow Store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useWorkflowStore.setState({
      mode: 'simple',
      status: 'idle',
      currentExecution: undefined,
      agents: [
        {
          id: 'agent-1',
          name: 'System Agent',
          type: 'system',
          status: 'idle',
          tasksCompleted: 42,
          efficiency: 0.87,
          lastActive: new Date(),
          memoryUsage: 128,
          tools: ['filesystem', 'process', 'network']
        }
      ],
      activeAgents: [],
      executionHistory: [],
      metrics: {
        totalExecutions: 0,
        successRate: 0,
        averageDuration: 0,
        activeAgents: 0,
        queuedTasks: 0,
        errorRate: 0,
        lastUpdated: new Date()
      },
      autoRetry: true,
      maxRetries: 3,
      timeout: 300,
      lastUpdate: new Date(),
    })
  })

  describe('Mode Management', () => {
    test('sets workflow mode', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      expect(result.current.mode).toBe('simple')
      
      act(() => {
        result.current.setMode('advanced')
      })
      
      expect(result.current.mode).toBe('advanced')
      
      act(() => {
        result.current.setMode('expert')
      })
      
      expect(result.current.mode).toBe('expert')
    })
  })

  describe('Execution Management', () => {
    test('starts workflow execution', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      expect(result.current.status).toBe('idle')
      expect(result.current.currentExecution).toBeUndefined()
      
      act(() => {
        result.current.startExecution('sequential', 0.6)
      })
      
      expect(result.current.status).toBe('analyzing')
      expect(result.current.currentExecution).toBeDefined()
      expect(result.current.currentExecution?.pattern).toBe('sequential')
      expect(result.current.currentExecution?.complexity).toBe(0.6)
      expect(result.current.currentExecution?.status).toBe('analyzing')
    })

    test('updates execution status', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('parallel', 0.8)
      })
      
      act(() => {
        result.current.updateExecutionStatus('executing')
      })
      
      expect(result.current.status).toBe('executing')
      expect(result.current.currentExecution?.status).toBe('executing')
    })

    test('completes execution successfully', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('conditional', 0.7)
      })
      
      act(() => {
        result.current.completeExecution(true)
      })
      
      expect(result.current.status).toBe('idle')
      expect(result.current.currentExecution).toBeUndefined()
      expect(result.current.executionHistory).toHaveLength(1)
      expect(result.current.executionHistory[0].success).toBe(true)
      expect(result.current.executionHistory[0].endTime).toBeDefined()
      expect(result.current.executionHistory[0].duration).toBeGreaterThan(0)
    })

    test('completes execution with failure', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('hierarchical', 0.9)
      })
      
      act(() => {
        result.current.completeExecution(false)
      })
      
      expect(result.current.status).toBe('idle')
      expect(result.current.executionHistory[0].success).toBe(false)
      expect(result.current.executionHistory[0].status).toBe('error')
    })

    test('updates metrics after execution', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      const initialTotalExecutions = result.current.metrics.totalExecutions
      
      act(() => {
        result.current.startExecution('sequential', 0.5)
      })
      
      act(() => {
        result.current.completeExecution(true)
      })
      
      expect(result.current.metrics.totalExecutions).toBe(initialTotalExecutions + 1)
      expect(result.current.metrics.successRate).toBe(1.0)
    })

    test('maintains execution history limit', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      // Add 60 executions (more than the 50 limit)
      for (let i = 0; i < 60; i++) {
        act(() => {
          result.current.startExecution(`execution-${i}`, 0.5)
          result.current.completeExecution(true)
        })
      }
      
      expect(result.current.executionHistory).toHaveLength(50)
      expect(result.current.executionHistory[0].pattern).toBe('execution-59') // Most recent first
    })
  })

  describe('Agent Management', () => {
    test('adds new agent', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      const initialAgentCount = result.current.agents.length
      
      act(() => {
        result.current.addAgent({
          name: 'Test Agent',
          type: 'test',
          status: 'idle',
          tasksCompleted: 0,
          efficiency: 0.95,
          lastActive: new Date(),
          memoryUsage: 64,
          tools: ['test']
        })
      })
      
      expect(result.current.agents).toHaveLength(initialAgentCount + 1)
      expect(result.current.agents[result.current.agents.length - 1].name).toBe('Test Agent')
      expect(result.current.agents[result.current.agents.length - 1].id).toBeDefined()
    })

    test('updates agent status', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      const agentId = result.current.agents[0].id
      
      act(() => {
        result.current.setAgentStatus(agentId, 'active')
      })
      
      expect(result.current.agents[0].status).toBe('active')
      expect(result.current.activeAgents).toContain(agentId)
      expect(result.current.metrics.activeAgents).toBe(1)
      
      act(() => {
        result.current.setAgentStatus(agentId, 'idle')
      })
      
      expect(result.current.agents[0].status).toBe('idle')
      expect(result.current.activeAgents).not.toContain(agentId)
      expect(result.current.metrics.activeAgents).toBe(0)
    })

    test('updates agent properties', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      const agentId = result.current.agents[0].id
      const originalLastActive = result.current.agents[0].lastActive
      
      act(() => {
        result.current.updateAgent(agentId, {
          tasksCompleted: 50,
          efficiency: 0.95,
          currentTask: 'Processing data'
        })
      })
      
      const updatedAgent = result.current.agents[0]
      expect(updatedAgent.tasksCompleted).toBe(50)
      expect(updatedAgent.efficiency).toBe(0.95)
      expect(updatedAgent.currentTask).toBe('Processing data')
      expect(updatedAgent.lastActive.getTime()).toBeGreaterThan(originalLastActive.getTime())
    })

    test('removes agent', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      const agentId = result.current.agents[0].id
      const initialAgentCount = result.current.agents.length
      
      // Make agent active first
      act(() => {
        result.current.setAgentStatus(agentId, 'active')
      })
      
      expect(result.current.activeAgents).toContain(agentId)
      
      act(() => {
        result.current.removeAgent(agentId)
      })
      
      expect(result.current.agents).toHaveLength(initialAgentCount - 1)
      expect(result.current.activeAgents).not.toContain(agentId)
      expect(result.current.agents.find(a => a.id === agentId)).toBeUndefined()
    })
  })

  describe('Step Management', () => {
    test('adds workflow steps', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('sequential', 0.5)
      })
      
      act(() => {
        result.current.addStep({
          name: 'Test Step',
          status: 'pending',
          agent: 'agent-1',
        })
      })
      
      expect(result.current.currentExecution?.steps).toHaveLength(1)
      expect(result.current.currentExecution?.steps[0].name).toBe('Test Step')
      expect(result.current.currentExecution?.steps[0].id).toBeDefined()
    })

    test('updates workflow steps', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('parallel', 0.6)
      })
      
      act(() => {
        result.current.addStep({
          name: 'Update Step',
          status: 'pending',
        })
      })
      
      const stepId = result.current.currentExecution!.steps[0].id
      
      act(() => {
        result.current.updateStep(stepId, {
          status: 'running',
          startTime: new Date(),
          output: 'Step started'
        })
      })
      
      const updatedStep = result.current.currentExecution!.steps[0]
      expect(updatedStep.status).toBe('running')
      expect(updatedStep.startTime).toBeDefined()
      expect(updatedStep.output).toBe('Step started')
    })
  })

  describe('Settings Management', () => {
    test('manages retry settings', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      expect(result.current.autoRetry).toBe(true)
      expect(result.current.maxRetries).toBe(3)
      
      act(() => {
        result.current.setAutoRetry(false)
      })
      expect(result.current.autoRetry).toBe(false)
      
      act(() => {
        result.current.setMaxRetries(5)
      })
      expect(result.current.maxRetries).toBe(5)
      
      // Test constraints
      act(() => {
        result.current.setMaxRetries(-1)
      })
      expect(result.current.maxRetries).toBe(0)
      
      act(() => {
        result.current.setMaxRetries(15)
      })
      expect(result.current.maxRetries).toBe(10)
    })

    test('manages timeout settings', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      expect(result.current.timeout).toBe(300)
      
      act(() => {
        result.current.setTimeout(600)
      })
      expect(result.current.timeout).toBe(600)
      
      // Test constraints
      act(() => {
        result.current.setTimeout(10)
      })
      expect(result.current.timeout).toBe(30)
      
      act(() => {
        result.current.setTimeout(5000)
      })
      expect(result.current.timeout).toBe(3600)
    })
  })

  describe('Utility Actions', () => {
    test('clears execution history', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      // Add some history
      act(() => {
        result.current.startExecution('test', 0.5)
        result.current.completeExecution(true)
      })
      
      expect(result.current.executionHistory).toHaveLength(1)
      
      act(() => {
        result.current.clearHistory()
      })
      
      expect(result.current.executionHistory).toHaveLength(0)
    })

    test('resets current execution', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.startExecution('test', 0.5)
      })
      
      expect(result.current.currentExecution).toBeDefined()
      expect(result.current.status).toBe('analyzing')
      
      act(() => {
        result.current.resetCurrentExecution()
      })
      
      expect(result.current.currentExecution).toBeUndefined()
      expect(result.current.status).toBe('idle')
    })
  })

  describe('Selectors', () => {
    test('execution selector provides computed values', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      let execution = workflowSelectors.execution(result.current)
      expect(execution.isExecuting).toBe(false)
      expect(execution.canExecute).toBe(true)
      
      act(() => {
        result.current.startExecution('test', 0.5)
      })
      
      execution = workflowSelectors.execution(result.current)
      expect(execution.isExecuting).toBe(true)
      expect(execution.canExecute).toBe(false)
    })

    test('agents selector provides statistics', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.addAgent({
          name: 'Agent 2',
          type: 'task',
          status: 'busy',
          tasksCompleted: 10,
          efficiency: 0.9,
          lastActive: new Date(),
          memoryUsage: 80,
          tools: ['analysis']
        })
        result.current.addAgent({
          name: 'Agent 3',
          type: 'system',
          status: 'error',
          tasksCompleted: 5,
          efficiency: 0.7,
          lastActive: new Date(),
          memoryUsage: 120,
          tools: ['system']
        })
        result.current.setAgentStatus(result.current.agents[0].id, 'active')
        result.current.setAgentStatus(result.current.agents[1].id, 'busy')
      })
      
      const agents = workflowSelectors.agents(result.current)
      
      expect(agents.totalCount).toBe(3)
      expect(agents.activeCount).toBe(2) // active + busy
      expect(agents.busyCount).toBe(1)
      expect(agents.errorCount).toBe(1)
      expect(agents.hasErrors).toBe(true)
      expect(agents.utilizationRate).toBeCloseTo(0.67, 2) // 2/3
    })

    test('history selector provides analysis', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      // Add mixed success/failure history
      act(() => {
        result.current.startExecution('test1', 0.5)
        result.current.completeExecution(true)
        
        result.current.startExecution('test2', 0.7)
        result.current.completeExecution(false)
        
        result.current.startExecution('test3', 0.3)
        result.current.completeExecution(true)
      })
      
      const history = workflowSelectors.history(result.current)
      
      expect(history.totalCount).toBe(3)
      expect(history.successfulCount).toBe(2)
      expect(history.failedCount).toBe(1)
      expect(history.recentSuccessRate).toBeCloseTo(0.67, 2)
      expect(history.recent).toHaveLength(3)
    })

    test('metrics selector provides computed efficiency', () => {
      const { result } = renderHook(() => useWorkflowStore())
      
      act(() => {
        result.current.updateMetrics({
          successRate: 0.9,
          errorRate: 0.1,
          totalExecutions: 100,
        })
      })
      
      const metrics = workflowSelectors.metrics(result.current)
      
      expect(metrics.efficiencyScore).toBeCloseTo(0.81, 2) // 0.9 * (1 - 0.1)
      expect(metrics.totalExecutions).toBe(100)
      expect(metrics.successRate).toBe(0.9)
      expect(metrics.errorRate).toBe(0.1)
    })
  })
})