'use client'

import React, { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Brain, MessageCircle, Pause, Play } from 'lucide-react'

interface AgentStatus {
  id: string
  name: string
  type: string
  status: 'idle' | 'working' | 'communicating' | 'learning'
  currentTask?: string
  progress?: number
  lastActivity?: string
  taskStartTime?: number
  performance?: {
    tasksCompleted: number
    averageExecutionTime: number
    successRate: number
  }
  capabilities?: string[]
  memoryUsage?: {
    local: number
    shared: number
    knowledge: number
  }
}

interface AgentStatusPanelProps {
  agents: AgentStatus[]
  onAgentSelect?: (agentId: string) => void
  selectedAgentId?: string
}

function getStatusVariant(status: AgentStatus['status']): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'working':
      return 'default'
    case 'learning':
      return 'secondary'
    case 'communicating':
      return 'outline'
    case 'idle':
    default:
      return 'outline'
  }
}

function getStatusIcon(status: AgentStatus['status']) {
  switch (status) {
    case 'working':
      return <Play className="h-3 w-3" />
    case 'learning':
      return <Brain className="h-3 w-3" />
    case 'communicating':
      return <MessageCircle className="h-3 w-3" />
    case 'idle':
    default:
      return <Pause className="h-3 w-3" />
  }
}

function formatDuration(startTime?: number): string {
  if (!startTime) return ''
  const duration = Date.now() - startTime
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  }
  return `${seconds}s`
}

export function AgentStatusCard({ agent, isSelected, onClick }: { 
  agent: AgentStatus
  isSelected?: boolean
  onClick?: () => void 
}) {
  const [taskDuration, setTaskDuration] = useState('')

  useEffect(() => {
    if (agent.taskStartTime && agent.status === 'working') {
      const interval = setInterval(() => {
        setTaskDuration(formatDuration(agent.taskStartTime))
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [agent.taskStartTime, agent.status])

  return (
    <Card 
      className={`transition-all cursor-pointer hover:shadow-md ${
        isSelected ? 'ring-2 ring-primary ring-offset-2' : ''
      }`}
      onClick={onClick}
    >
      <CardContent className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              {getStatusIcon(agent.status)}
              <span className="text-sm font-medium">{agent.name}</span>
            </div>
            <Badge variant="outline" className="text-xs">
              {agent.type}
            </Badge>
          </div>
          <Badge variant={getStatusVariant(agent.status)} className="text-xs">
            {agent.status}
          </Badge>
        </div>
        
        {agent.currentTask && (
          <div className="mb-2">
            <p className="text-xs text-muted-foreground line-clamp-2">
              {agent.currentTask}
            </p>
            {taskDuration && (
              <p className="text-xs text-muted-foreground mt-1">
                Duration: {taskDuration}
              </p>
            )}
          </div>
        )}
        
        {agent.progress !== undefined && (
          <div className="mb-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-muted-foreground">Progress</span>
              <span className="text-xs font-medium">{Math.round(agent.progress)}%</span>
            </div>
            <Progress value={agent.progress} className="h-2" />
          </div>
        )}

        {agent.performance && (
          <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-border">
            <div className="text-center">
              <p className="text-xs font-medium">{agent.performance.tasksCompleted}</p>
              <p className="text-xs text-muted-foreground">Tasks</p>
            </div>
            <div className="text-center">
              <p className="text-xs font-medium">{agent.performance.averageExecutionTime.toFixed(1)}s</p>
              <p className="text-xs text-muted-foreground">Avg Time</p>
            </div>
            <div className="text-center">
              <p className="text-xs font-medium">{Math.round(agent.performance.successRate * 100)}%</p>
              <p className="text-xs text-muted-foreground">Success</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function AgentStatusPanel({ agents, onAgentSelect, selectedAgentId }: AgentStatusPanelProps) {
  const activeAgents = agents.filter(agent => agent.status !== 'idle')
  const idleAgents = agents.filter(agent => agent.status === 'idle')

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Activity className="h-4 w-4" />
          <h3 className="text-sm font-medium">Active Agents ({activeAgents.length})</h3>
        </div>
        <div className="space-y-2">
          {activeAgents.length > 0 ? (
            activeAgents.map(agent => (
              <AgentStatusCard
                key={agent.id}
                agent={agent}
                isSelected={selectedAgentId === agent.id}
                onClick={() => onAgentSelect?.(agent.id)}
              />
            ))
          ) : (
            <div className="text-center py-4 text-sm text-muted-foreground">
              No active agents
            </div>
          )}
        </div>
      </div>

      {idleAgents.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Pause className="h-4 w-4" />
            <h3 className="text-sm font-medium">Idle Agents ({idleAgents.length})</h3>
          </div>
          <div className="space-y-2">
            {idleAgents.map(agent => (
              <AgentStatusCard
                key={agent.id}
                agent={agent}
                isSelected={selectedAgentId === agent.id}
                onClick={() => onAgentSelect?.(agent.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export function AgentDetailView({ agent }: { agent: AgentStatus }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon(agent.status)}
          {agent.name}
          <Badge variant={getStatusVariant(agent.status)} className="ml-auto">
            {agent.status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Agent Info</h4>
            <div className="space-y-1 text-sm">
              <div>
                <span className="text-muted-foreground">ID:</span> {agent.id}
              </div>
              <div>
                <span className="text-muted-foreground">Type:</span> {agent.type}
              </div>
              {agent.lastActivity && (
                <div>
                  <span className="text-muted-foreground">Last Activity:</span> {agent.lastActivity}
                </div>
              )}
            </div>
          </div>

          {agent.memoryUsage && (
            <div>
              <h4 className="text-sm font-medium mb-2">Memory Usage</h4>
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-sm">
                    <span>Local</span>
                    <span>{agent.memoryUsage.local} KB</span>
                  </div>
                  <Progress value={(agent.memoryUsage.local / 1024) * 100} className="h-1" />
                </div>
                <div>
                  <div className="flex justify-between text-sm">
                    <span>Shared</span>
                    <span>{agent.memoryUsage.shared} KB</span>
                  </div>
                  <Progress value={(agent.memoryUsage.shared / 1024) * 100} className="h-1" />
                </div>
                <div>
                  <div className="flex justify-between text-sm">
                    <span>Knowledge</span>
                    <span>{agent.memoryUsage.knowledge} KB</span>
                  </div>
                  <Progress value={(agent.memoryUsage.knowledge / 1024) * 100} className="h-1" />
                </div>
              </div>
            </div>
          )}
        </div>

        {agent.capabilities && agent.capabilities.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Capabilities</h4>
            <div className="flex flex-wrap gap-1">
              {agent.capabilities.map((capability, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {capability}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {agent.currentTask && (
          <div>
            <h4 className="text-sm font-medium mb-2">Current Task</h4>
            <p className="text-sm text-muted-foreground">{agent.currentTask}</p>
            {agent.progress !== undefined && (
              <div className="mt-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm">Progress</span>
                  <span className="text-sm font-medium">{Math.round(agent.progress)}%</span>
                </div>
                <Progress value={agent.progress} className="h-2" />
              </div>
            )}
          </div>
        )}

        {agent.performance && (
          <div>
            <h4 className="text-sm font-medium mb-2">Performance Metrics</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-lg font-bold">{agent.performance.tasksCompleted}</p>
                <p className="text-sm text-muted-foreground">Tasks Completed</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-lg font-bold">{agent.performance.averageExecutionTime.toFixed(1)}s</p>
                <p className="text-sm text-muted-foreground">Average Time</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-lg font-bold">{Math.round(agent.performance.successRate * 100)}%</p>
                <p className="text-sm text-muted-foreground">Success Rate</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}