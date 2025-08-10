'use client'

import React, { memo, useMemo, useCallback } from 'react'
import { Bot, Cpu, HardDrive, Clock, Activity, AlertCircle, CheckCircle2, Pause, Play } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface AgentStatus {
  id: string
  name: string
  type: 'system' | 'task' | 'research' | 'creative' | 'analytical' | 'communication'
  status: 'idle' | 'active' | 'busy' | 'error' | 'paused'
  currentTask?: string
  tasksCompleted: number
  efficiency: number
  memoryUsage: number // in MB
  cpuUsage?: number // percentage
  lastActive: Date
  uptime: number // in seconds
  tools: string[]
  errorCount?: number
  successRate?: number
}

export interface AgentStatusCardProps {
  agent: AgentStatus
  onPause?: (agentId: string) => void
  onResume?: (agentId: string) => void
  onRestart?: (agentId: string) => void
  onViewDetails?: (agentId: string) => void
  className?: string
  compact?: boolean
}

const AgentStatusCard = memo<AgentStatusCardProps>(({
  agent,
  onPause,
  onResume,
  onRestart,
  onViewDetails,
  className,
  compact = false
}) => {
  const { reducedMotion, theme } = useUIStore(state => ({
    reducedMotion: state.reducedMotion,
    theme: state.theme
  }))

  const statusConfig = useMemo(() => ({
    idle: {
      color: 'text-gray-500',
      bgColor: 'bg-gray-100 dark:bg-gray-800',
      borderColor: 'border-gray-200 dark:border-gray-700',
      icon: Pause,
      label: 'Idle',
      pulseColor: 'bg-gray-400'
    },
    active: {
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-950',
      borderColor: 'border-green-200 dark:border-green-800',
      icon: Activity,
      label: 'Active',
      pulseColor: 'bg-green-500'
    },
    busy: {
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-950',
      borderColor: 'border-orange-200 dark:border-orange-800',
      icon: Cpu,
      label: 'Busy',
      pulseColor: 'bg-orange-500'
    },
    error: {
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-950',
      borderColor: 'border-red-200 dark:border-red-800',
      icon: AlertCircle,
      label: 'Error',
      pulseColor: 'bg-red-500'
    },
    paused: {
      color: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-50 dark:bg-yellow-950',
      borderColor: 'border-yellow-200 dark:border-yellow-800',
      icon: Pause,
      label: 'Paused',
      pulseColor: 'bg-yellow-500'
    }
  }), [])

  const typeConfig = useMemo(() => ({
    system: { label: 'System', color: 'bg-blue-500' },
    task: { label: 'Task', color: 'bg-green-500' },
    research: { label: 'Research', color: 'bg-purple-500' },
    creative: { label: 'Creative', color: 'bg-pink-500' },
    analytical: { label: 'Analytical', color: 'bg-indigo-500' },
    communication: { label: 'Communication', color: 'bg-teal-500' }
  }), [])

  const config = statusConfig[agent.status]
  const typeInfo = typeConfig[agent.type]
  const StatusIcon = config.icon

  const formatUptime = useCallback((seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`
    return `${Math.floor(seconds / 86400)}d`
  }, [])

  const formatMemory = useCallback((mb: number): string => {
    if (mb < 1024) return `${mb}MB`
    return `${(mb / 1024).toFixed(1)}GB`
  }, [])

  const handlePause = useCallback(() => {
    onPause?.(agent.id)
  }, [onPause, agent.id])

  const handleResume = useCallback(() => {
    onResume?.(agent.id)
  }, [onResume, agent.id])

  const handleRestart = useCallback(() => {
    onRestart?.(agent.id)
  }, [onRestart, agent.id])

  const handleViewDetails = useCallback(() => {
    onViewDetails?.(agent.id)
  }, [onViewDetails, agent.id])

  if (compact) {
    return (
      <div className={cn(
        'flex items-center gap-3 p-3 rounded-lg border',
        config.bgColor,
        config.borderColor,
        !reducedMotion && 'transition-all duration-200',
        'hover:shadow-md cursor-pointer',
        className
      )} onClick={handleViewDetails}>
        {/* Status Indicator */}
        <div className="relative">
          <div className={cn(
            'w-3 h-3 rounded-full',
            config.pulseColor,
            !reducedMotion && agent.status === 'active' && 'animate-pulse'
          )} />
          {agent.status === 'error' && agent.errorCount && agent.errorCount > 0 && (
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />
          )}
        </div>

        {/* Agent Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-sm truncate">{agent.name}</span>
            <span className={cn(
              'px-2 py-0.5 rounded text-xs font-medium text-white',
              typeInfo.color
            )}>
              {typeInfo.label}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span>{agent.tasksCompleted} tasks</span>
            <span>{Math.round(agent.efficiency * 100)}%</span>
            <span>{formatMemory(agent.memoryUsage)}</span>
          </div>
        </div>

        <StatusIcon className={cn('w-4 h-4', config.color)} />
      </div>
    )
  }

  return (
    <div className={cn(
      'p-4 rounded-lg border',
      config.bgColor,
      config.borderColor,
      !reducedMotion && 'transition-all duration-200',
      'hover:shadow-lg group',
      className
    )}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className={cn(
              'w-10 h-10 rounded-full flex items-center justify-center',
              typeInfo.color
            )}>
              <Bot className="w-5 h-5 text-white" />
            </div>
            
            {/* Status Indicator */}
            <div className={cn(
              'absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white dark:border-gray-900 flex items-center justify-center',
              config.pulseColor,
              !reducedMotion && agent.status === 'active' && 'animate-pulse'
            )}>
              <StatusIcon className="w-2 h-2 text-white" />
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {agent.name}
            </h3>
            <div className="flex items-center gap-2">
              <span className={cn(
                'px-2 py-1 rounded text-xs font-medium text-white',
                typeInfo.color
              )}>
                {typeInfo.label}
              </span>
              <span className={cn('text-sm font-medium', config.color)}>
                {config.label}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className={cn(
          'flex items-center gap-1 opacity-0 group-hover:opacity-100',
          !reducedMotion && 'transition-opacity duration-200'
        )}>
          {agent.status === 'active' || agent.status === 'busy' ? (
            <button
              onClick={handlePause}
              className={cn(
                'p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300',
                'hover:bg-gray-100 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
              title="Pause Agent"
            >
              <Pause className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleResume}
              className={cn(
                'p-2 rounded-md text-gray-400 hover:text-green-600',
                'hover:bg-green-50 dark:hover:bg-green-950',
                !reducedMotion && 'transition-colors duration-200'
              )}
              title="Resume Agent"
            >
              <Play className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Current Task */}
      {agent.currentTask && (
        <div className="mb-3 p-2 bg-white/50 dark:bg-black/20 rounded-md">
          <div className="text-xs text-gray-500 mb-1">Current Task:</div>
          <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
            {agent.currentTask}
          </div>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {agent.tasksCompleted}
          </div>
          <div className="text-xs text-gray-500">Tasks Completed</div>
        </div>
        
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {Math.round(agent.efficiency * 100)}%
          </div>
          <div className="text-xs text-gray-500">Efficiency</div>
        </div>
      </div>

      {/* Resource Usage */}
      <div className="space-y-2 mb-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">Memory</span>
          </div>
          <span className="font-medium">{formatMemory(agent.memoryUsage)}</span>
        </div>
        
        {agent.cpuUsage !== undefined && (
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600 dark:text-gray-400">CPU</span>
            </div>
            <span className="font-medium">{agent.cpuUsage}%</span>
          </div>
        )}
        
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">Uptime</span>
          </div>
          <span className="font-medium">{formatUptime(agent.uptime)}</span>
        </div>
      </div>

      {/* Success Rate & Errors */}
      {(agent.successRate !== undefined || (agent.errorCount && agent.errorCount > 0)) && (
        <div className="flex items-center justify-between text-sm mb-3">
          {agent.successRate !== undefined && (
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span className="text-gray-600 dark:text-gray-400">
                {Math.round(agent.successRate * 100)}% success
              </span>
            </div>
          )}
          
          {agent.errorCount && agent.errorCount > 0 && (
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <span className="text-red-600 dark:text-red-400">
                {agent.errorCount} error{agent.errorCount !== 1 ? 's' : ''}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Tools */}
      <div className="mb-3">
        <div className="text-xs text-gray-500 mb-2">Available Tools:</div>
        <div className="flex flex-wrap gap-1">
          {agent.tools.slice(0, 3).map((tool) => (
            <span
              key={tool}
              className={cn(
                'px-2 py-1 rounded text-xs',
                'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
              )}
            >
              {tool}
            </span>
          ))}
          {agent.tools.length > 3 && (
            <span className="px-2 py-1 text-xs text-gray-500">
              +{agent.tools.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Last active: {agent.lastActive.toLocaleTimeString()}</span>
        <button
          onClick={handleViewDetails}
          className={cn(
            'text-blue-500 hover:text-blue-600 font-medium',
            !reducedMotion && 'transition-colors duration-200'
          )}
        >
          View Details →
        </button>
      </div>
    </div>
  )
})

AgentStatusCard.displayName = 'AgentStatusCard'

export default AgentStatusCard