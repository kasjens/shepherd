import { create } from 'zustand'
import { subscribeWithSelector, devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { shallow } from 'zustand/shallow'

export type WorkflowMode = 'simple' | 'advanced' | 'expert'
export type WorkflowStatus = 'idle' | 'analyzing' | 'executing' | 'completed' | 'error'
export type AgentStatus = 'idle' | 'active' | 'busy' | 'error' | 'offline'

export interface Agent {
  id: string
  name: string
  type: string
  status: AgentStatus
  currentTask?: string
  tasksCompleted: number
  efficiency: number
  lastActive: Date
  memoryUsage: number
  tools: string[]
}

export interface WorkflowExecution {
  id: string
  pattern: string
  status: WorkflowStatus
  startTime: Date
  endTime?: Date
  duration?: number
  steps: WorkflowStep[]
  agents: string[]
  complexity: number
  success: boolean
}

export interface WorkflowStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  agent?: string
  startTime?: Date
  endTime?: Date
  duration?: number
  output?: string
  error?: string
}

export interface WorkflowMetrics {
  totalExecutions: number
  successRate: number
  averageDuration: number
  activeAgents: number
  queuedTasks: number
  errorRate: number
  lastUpdated: Date
}

export interface WorkflowState {
  // Current workflow
  mode: WorkflowMode
  status: WorkflowStatus
  currentExecution?: WorkflowExecution
  
  // Agents
  agents: Agent[]
  activeAgents: string[]
  
  // History
  executionHistory: WorkflowExecution[]
  
  // Metrics
  metrics: WorkflowMetrics
  
  // Settings
  autoRetry: boolean
  maxRetries: number
  timeout: number
  
  // Real-time updates
  lastUpdate: Date
}

export interface WorkflowActions {
  // Mode actions
  setMode: (mode: WorkflowMode) => void
  
  // Execution actions
  startExecution: (pattern: string, complexity: number) => void
  updateExecutionStatus: (status: WorkflowStatus) => void
  completeExecution: (success: boolean) => void
  
  // Agent actions
  updateAgent: (agentId: string, update: Partial<Agent>) => void
  addAgent: (agent: Omit<Agent, 'id'>) => void
  removeAgent: (agentId: string) => void
  setAgentStatus: (agentId: string, status: AgentStatus) => void
  
  // Step actions
  updateStep: (stepId: string, update: Partial<WorkflowStep>) => void
  addStep: (step: Omit<WorkflowStep, 'id'>) => void
  
  // Settings actions
  setAutoRetry: (enabled: boolean) => void
  setMaxRetries: (retries: number) => void
  setTimeout: (timeout: number) => void
  
  // Metrics actions
  updateMetrics: (metrics: Partial<WorkflowMetrics>) => void
  
  // Utility actions
  clearHistory: () => void
  resetCurrentExecution: () => void
}

export type WorkflowStore = WorkflowState & WorkflowActions

const generateId = () => Math.random().toString(36).substr(2, 9)

export const useWorkflowStore = create<WorkflowStore>()(
  devtools(
    immer(
      subscribeWithSelector((set, get) => ({
        // Initial state
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
          },
          {
            id: 'agent-2',
            name: 'Task Agent',
            type: 'task',
            status: 'idle',
            tasksCompleted: 35,
            efficiency: 0.92,
            lastActive: new Date(),
            memoryUsage: 95,
            tools: ['research', 'analysis', 'creative']
          },
          {
            id: 'agent-3',
            name: 'Analysis Agent',
            type: 'analysis',
            status: 'active',
            currentTask: 'Processing workflow patterns',
            tasksCompleted: 28,
            efficiency: 0.95,
            lastActive: new Date(),
            memoryUsage: 156,
            tools: ['data', 'metrics', 'reporting']
          }
        ],
        activeAgents: ['agent-3'],
        executionHistory: [],
        metrics: {
          totalExecutions: 127,
          successRate: 0.94,
          averageDuration: 2.8,
          activeAgents: 1,
          queuedTasks: 3,
          errorRate: 0.06,
          lastUpdated: new Date()
        },
        autoRetry: true,
        maxRetries: 3,
        timeout: 300,
        lastUpdate: new Date(),

        // Mode actions
        setMode: (mode) =>
          set((state) => {
            state.mode = mode
          }),

        // Execution actions
        startExecution: (pattern, complexity) =>
          set((state) => {
            const execution: WorkflowExecution = {
              id: generateId(),
              pattern,
              status: 'analyzing',
              startTime: new Date(),
              steps: [],
              agents: [],
              complexity,
              success: false
            }
            
            state.currentExecution = execution
            state.status = 'analyzing'
            state.lastUpdate = new Date()
          }),

        updateExecutionStatus: (status) =>
          set((state) => {
            state.status = status
            if (state.currentExecution) {
              state.currentExecution.status = status
            }
            state.lastUpdate = new Date()
          }),

        completeExecution: (success) =>
          set((state) => {
            if (state.currentExecution) {
              state.currentExecution.status = success ? 'completed' : 'error'
              state.currentExecution.endTime = new Date()
              state.currentExecution.duration = 
                (state.currentExecution.endTime.getTime() - state.currentExecution.startTime.getTime()) / 1000
              state.currentExecution.success = success
              
              // Add to history
              state.executionHistory.unshift(state.currentExecution)
              
              // Keep only last 50 executions
              if (state.executionHistory.length > 50) {
                state.executionHistory = state.executionHistory.slice(0, 50)
              }
              
              // Update metrics
              state.metrics.totalExecutions += 1
              state.metrics.successRate = 
                state.executionHistory.filter(e => e.success).length / state.executionHistory.length
              state.metrics.averageDuration = 
                state.executionHistory.reduce((acc, e) => acc + (e.duration || 0), 0) / state.executionHistory.length
              state.metrics.lastUpdated = new Date()
            }
            
            state.status = 'idle'
            state.currentExecution = undefined
            state.lastUpdate = new Date()
          }),

        // Agent actions
        updateAgent: (agentId, update) =>
          set((state) => {
            const agentIndex = state.agents.findIndex(a => a.id === agentId)
            if (agentIndex !== -1) {
              Object.assign(state.agents[agentIndex], update)
              state.agents[agentIndex].lastActive = new Date()
            }
            state.lastUpdate = new Date()
          }),

        addAgent: (agent) =>
          set((state) => {
            const newAgent: Agent = {
              ...agent,
              id: generateId(),
            }
            state.agents.push(newAgent)
            state.lastUpdate = new Date()
          }),

        removeAgent: (agentId) =>
          set((state) => {
            state.agents = state.agents.filter(a => a.id !== agentId)
            state.activeAgents = state.activeAgents.filter(id => id !== agentId)
            state.lastUpdate = new Date()
          }),

        setAgentStatus: (agentId, status) =>
          set((state) => {
            get().updateAgent(agentId, { status })
            
            // Update active agents list
            if (status === 'active' || status === 'busy') {
              if (!state.activeAgents.includes(agentId)) {
                state.activeAgents.push(agentId)
              }
            } else {
              state.activeAgents = state.activeAgents.filter(id => id !== agentId)
            }
            
            // Update metrics
            state.metrics.activeAgents = state.activeAgents.length
            state.metrics.lastUpdated = new Date()
          }),

        // Step actions
        updateStep: (stepId, update) =>
          set((state) => {
            if (state.currentExecution) {
              const stepIndex = state.currentExecution.steps.findIndex(s => s.id === stepId)
              if (stepIndex !== -1) {
                Object.assign(state.currentExecution.steps[stepIndex], update)
              }
            }
            state.lastUpdate = new Date()
          }),

        addStep: (step) =>
          set((state) => {
            if (state.currentExecution) {
              const newStep: WorkflowStep = {
                ...step,
                id: generateId(),
              }
              state.currentExecution.steps.push(newStep)
            }
            state.lastUpdate = new Date()
          }),

        // Settings actions
        setAutoRetry: (enabled) =>
          set((state) => {
            state.autoRetry = enabled
          }),

        setMaxRetries: (retries) =>
          set((state) => {
            state.maxRetries = Math.max(0, Math.min(10, retries))
          }),

        setTimeout: (timeout) =>
          set((state) => {
            state.timeout = Math.max(30, Math.min(3600, timeout))
          }),

        // Metrics actions
        updateMetrics: (metrics) =>
          set((state) => {
            Object.assign(state.metrics, metrics)
            state.metrics.lastUpdated = new Date()
            state.lastUpdate = new Date()
          }),

        // Utility actions
        clearHistory: () =>
          set((state) => {
            state.executionHistory = []
            state.lastUpdate = new Date()
          }),

        resetCurrentExecution: () =>
          set((state) => {
            state.currentExecution = undefined
            state.status = 'idle'
            state.lastUpdate = new Date()
          }),
      }))
    ),
    {
      name: 'workflow-store',
    }
  )
)

// Performance-optimized selectors
export const workflowSelectors = {
  // Current execution
  execution: (state: WorkflowStore) => ({
    mode: state.mode,
    status: state.status,
    currentExecution: state.currentExecution,
  }),
  
  // Agents
  agents: (state: WorkflowStore) => ({
    agents: state.agents,
    activeAgents: state.activeAgents,
    agentCount: state.agents.length,
    activeCount: state.activeAgents.length,
  }),
  
  // Metrics
  metrics: (state: WorkflowStore) => state.metrics,
  
  // Settings
  settings: (state: WorkflowStore) => ({
    autoRetry: state.autoRetry,
    maxRetries: state.maxRetries,
    timeout: state.timeout,
  }),
  
  // History
  history: (state: WorkflowStore) => ({
    executions: state.executionHistory,
    totalExecutions: state.executionHistory.length,
    recentExecutions: state.executionHistory.slice(0, 10),
  }),
}

// Typed hooks
export const useWorkflowExecution = () => useWorkflowStore(workflowSelectors.execution, shallow)
export const useWorkflowAgents = () => useWorkflowStore(workflowSelectors.agents, shallow)
export const useWorkflowMetrics = () => useWorkflowStore(workflowSelectors.metrics, shallow)
export const useWorkflowSettings = () => useWorkflowStore(workflowSelectors.settings, shallow)
export const useWorkflowHistory = () => useWorkflowStore(workflowSelectors.history, shallow)

// Agent-specific selectors
export const useAgent = (agentId: string) => 
  useWorkflowStore((state) => state.agents.find(a => a.id === agentId), shallow)

export const useActiveAgents = () => 
  useWorkflowStore((state) => 
    state.agents.filter(a => state.activeAgents.includes(a.id)), 
    shallow
  )