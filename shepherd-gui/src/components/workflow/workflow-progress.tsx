'use client'

import React, { memo, useMemo, useCallback } from 'react'
import { 
  Play, 
  Pause, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  RotateCcw,
  ChevronRight,
  ChevronDown,
  Bot,
  Zap,
  Timer
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface WorkflowStep {
  id: string
  name: string
  description?: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  agent?: string
  startTime?: Date
  endTime?: Date
  duration?: number
  output?: string
  error?: string
  progress?: number // 0-1
  substeps?: WorkflowStep[]
}

export interface WorkflowExecution {
  id: string
  name: string
  pattern: 'sequential' | 'parallel' | 'conditional' | 'hierarchical' | 'iterative'
  status: 'analyzing' | 'executing' | 'completed' | 'failed' | 'paused'
  complexity: number
  startTime: Date
  endTime?: Date
  duration?: number
  steps: WorkflowStep[]
  progress: number // 0-1
  estimatedTimeRemaining?: number
}

export interface WorkflowProgressProps {
  execution: WorkflowExecution
  onPause?: (executionId: string) => void
  onResume?: (executionId: string) => void
  onCancel?: (executionId: string) => void
  onRetryStep?: (stepId: string) => void
  onViewStepDetails?: (stepId: string) => void
  className?: string
  showDetails?: boolean
}

const WorkflowProgress = memo<WorkflowProgressProps>(({
  execution,
  onPause,
  onResume,
  onCancel,
  onRetryStep,
  onViewStepDetails,
  className,
  showDetails = true
}) => {
  const { reducedMotion, theme } = useUIStore(state => ({
    reducedMotion: state.reducedMotion,
    theme: state.theme
  }))

  const statusConfig = useMemo(() => ({
    analyzing: {
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
      borderColor: 'border-blue-200 dark:border-blue-800',
      icon: Bot,
      label: 'Analyzing',
      pulseColor: 'bg-blue-500'
    },
    executing: {
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-950',
      borderColor: 'border-orange-200 dark:border-orange-800',
      icon: Play,
      label: 'Executing',
      pulseColor: 'bg-orange-500'
    },
    completed: {
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-950',
      borderColor: 'border-green-200 dark:border-green-800',
      icon: CheckCircle2,
      label: 'Completed',
      pulseColor: 'bg-green-500'
    },
    failed: {
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-950',
      borderColor: 'border-red-200 dark:border-red-800',
      icon: AlertCircle,
      label: 'Failed',
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

  const stepStatusConfig = useMemo(() => ({
    pending: {
      color: 'text-gray-400',
      bgColor: 'bg-gray-100',
      icon: Clock,
      borderColor: 'border-gray-200'
    },
    running: {
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      icon: Play,
      borderColor: 'border-blue-200'
    },
    completed: {
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      icon: CheckCircle2,
      borderColor: 'border-green-200'
    },
    failed: {
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      icon: AlertCircle,
      borderColor: 'border-red-200'
    },
    skipped: {
      color: 'text-gray-400',
      bgColor: 'bg-gray-50',
      icon: ChevronRight,
      borderColor: 'border-gray-100'
    }
  }), [])

  const patternLabels = {
    sequential: 'Sequential',
    parallel: 'Parallel',
    conditional: 'Conditional',
    hierarchical: 'Hierarchical',
    iterative: 'Iterative'
  }

  const config = statusConfig[execution.status]
  const StatusIcon = config.icon

  const formatDuration = useCallback((seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }, [])

  const formatTimeRemaining = useCallback((seconds: number): string => {
    if (seconds < 60) return `~${Math.round(seconds)}s remaining`
    if (seconds < 3600) return `~${Math.floor(seconds / 60)}m remaining`
    return `~${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m remaining`
  }, [])

  const handlePause = useCallback(() => {
    onPause?.(execution.id)
  }, [onPause, execution.id])

  const handleResume = useCallback(() => {
    onResume?.(execution.id)
  }, [onResume, execution.id])

  const handleCancel = useCallback(() => {
    onCancel?.(execution.id)
  }, [onCancel, execution.id])

  const completedSteps = useMemo(() => 
    execution.steps.filter(step => step.status === 'completed').length
  , [execution.steps])

  const failedSteps = useMemo(() => 
    execution.steps.filter(step => step.status === 'failed').length
  , [execution.steps])

  const runningSteps = useMemo(() => 
    execution.steps.filter(step => step.status === 'running').length
  , [execution.steps])

  return (
    <div className={cn(
      'bg-white dark:bg-gray-900 border rounded-lg overflow-hidden',
      config.borderColor,
      className
    )}>
      {/* Header */}
      <div className={cn(
        'p-4 border-b',
        config.bgColor,
        config.borderColor
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <StatusIcon className={cn('w-6 h-6', config.color)} />
              {execution.status === 'executing' && (
                <div className={cn(
                  'absolute -inset-1 rounded-full opacity-75',
                  config.pulseColor,
                  !reducedMotion && 'animate-ping'
                )} />
              )}
            </div>
            
            <div>
              <h3 className={cn('font-semibold', config.color)}>
                {execution.name}
              </h3>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span>{patternLabels[execution.pattern]}</span>
                <span>•</span>
                <span>Complexity: {Math.round(execution.complexity * 100)}%</span>
                <span>•</span>
                <span>{completedSteps}/{execution.steps.length} steps</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {execution.status === 'executing' && (
              <button
                onClick={handlePause}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-md border',
                  'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600',
                  'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </button>
            )}
            
            {execution.status === 'paused' && (
              <button
                onClick={handleResume}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-md border',
                  'bg-green-600 border-green-600 text-white',
                  'hover:bg-green-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <Play className="w-4 h-4 mr-1" />
                Resume
              </button>
            )}
            
            {(execution.status === 'executing' || execution.status === 'paused') && (
              <button
                onClick={handleCancel}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-md border',
                  'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600',
                  'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Progress: {Math.round(execution.progress * 100)}%
            </span>
            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              {execution.duration && (
                <div className="flex items-center gap-1">
                  <Timer className="w-4 h-4" />
                  <span>{formatDuration(execution.duration)}</span>
                </div>
              )}
              {execution.estimatedTimeRemaining && execution.status === 'executing' && (
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{formatTimeRemaining(execution.estimatedTimeRemaining)}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={cn(
                'h-2 rounded-full transition-all duration-300',
                config.pulseColor
              )}
              style={{ width: `${Math.round(execution.progress * 100)}%` }}
            />
          </div>
        </div>

        {/* Status Summary */}
        <div className="flex items-center gap-4 mt-3 text-sm">
          {runningSteps > 0 && (
            <div className="flex items-center gap-1 text-blue-600 dark:text-blue-400">
              <Zap className="w-4 h-4" />
              <span>{runningSteps} running</span>
            </div>
          )}
          
          <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>{completedSteps} completed</span>
          </div>
          
          {failedSteps > 0 && (
            <div className="flex items-center gap-1 text-red-600 dark:text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span>{failedSteps} failed</span>
            </div>
          )}
        </div>
      </div>

      {/* Steps */}
      {showDetails && (
        <div className="p-4">
          <div className="space-y-3">
            {execution.steps.map((step, index) => (
              <WorkflowStepItem
                key={step.id}
                step={step}
                index={index}
                isLast={index === execution.steps.length - 1}
                onRetry={() => onRetryStep?.(step.id)}
                onViewDetails={() => onViewStepDetails?.(step.id)}
                reducedMotion={reducedMotion}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
})

const WorkflowStepItem = memo<{
  step: WorkflowStep
  index: number
  isLast: boolean
  onRetry: () => void
  onViewDetails: () => void
  reducedMotion: boolean
}>(({ step, index, isLast, onRetry, onViewDetails, reducedMotion }) => {
  const [isExpanded, setIsExpanded] = React.useState(false)

  const stepStatusConfig = {
    pending: { color: 'text-gray-400', bgColor: 'bg-gray-100', icon: Clock, borderColor: 'border-gray-200' },
    running: { color: 'text-blue-600', bgColor: 'bg-blue-100', icon: Play, borderColor: 'border-blue-200' },
    completed: { color: 'text-green-600', bgColor: 'bg-green-100', icon: CheckCircle2, borderColor: 'border-green-200' },
    failed: { color: 'text-red-600', bgColor: 'bg-red-100', icon: AlertCircle, borderColor: 'border-red-200' },
    skipped: { color: 'text-gray-400', bgColor: 'bg-gray-50', icon: ChevronRight, borderColor: 'border-gray-100' }
  }

  const config = stepStatusConfig[step.status]
  const StepIcon = config.icon

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
  }

  return (
    <div className="relative">
      {/* Connection Line */}
      {!isLast && (
        <div className={cn(
          'absolute left-6 top-12 w-0.5 h-8 bg-gray-200 dark:bg-gray-700',
          step.status === 'completed' && 'bg-green-200 dark:bg-green-800'
        )} />
      )}

      {/* Step */}
      <div className={cn(
        'flex items-start gap-3 p-3 rounded-lg border',
        'bg-white dark:bg-gray-800',
        config.borderColor,
        !reducedMotion && 'transition-all duration-200',
        'hover:shadow-sm'
      )}>
        {/* Step Number & Icon */}
        <div className="relative">
          <div className={cn(
            'w-12 h-12 rounded-full border-2 flex items-center justify-center',
            config.bgColor,
            config.borderColor
          )}>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-bold text-gray-500">
                {index + 1}
              </span>
            </div>
            <StepIcon className={cn('w-4 h-4 absolute top-0 right-0', config.color)} />
          </div>
          
          {step.status === 'running' && (
            <div className={cn(
              'absolute -inset-0.5 rounded-full border-2 border-blue-400',
              !reducedMotion && 'animate-pulse'
            )} />
          )}
        </div>

        {/* Step Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-medium text-gray-900 dark:text-gray-100">
              {step.name}
            </h4>
            
            <div className="flex items-center gap-2">
              {step.duration && (
                <span className="text-xs text-gray-500">
                  {formatDuration(step.duration)}
                </span>
              )}
              
              {step.agent && (
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs',
                  'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                )}>
                  {step.agent}
                </span>
              )}
            </div>
          </div>

          {step.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {step.description}
            </p>
          )}

          {/* Progress Bar for Running Steps */}
          {step.status === 'running' && step.progress !== undefined && (
            <div className="mb-2">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                <div
                  className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${Math.round(step.progress * 100)}%` }}
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            {(step.output || step.error || step.substeps) && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={cn(
                  'flex items-center gap-1 px-2 py-1 text-xs rounded',
                  'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                Details
              </button>
            )}
            
            {step.status === 'failed' && (
              <button
                onClick={onRetry}
                className={cn(
                  'flex items-center gap-1 px-2 py-1 text-xs rounded',
                  'text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-950',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <RotateCcw className="w-3 h-3" />
                Retry
              </button>
            )}
          </div>

          {/* Expanded Details */}
          {isExpanded && (
            <div className="mt-3 space-y-2">
              {step.error && (
                <div className="p-2 bg-red-50 dark:bg-red-950 rounded text-sm">
                  <div className="font-medium text-red-700 dark:text-red-400 mb-1">Error:</div>
                  <div className="text-red-600 dark:text-red-300 text-xs">{step.error}</div>
                </div>
              )}
              
              {step.output && (
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                  <div className="font-medium text-gray-700 dark:text-gray-400 mb-1">Output:</div>
                  <div className="text-gray-600 dark:text-gray-300 text-xs whitespace-pre-wrap">
                    {step.output}
                  </div>
                </div>
              )}
              
              {step.substeps && step.substeps.length > 0 && (
                <div className="pl-4 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
                  {step.substeps.map((substep, subIndex) => (
                    <WorkflowStepItem
                      key={substep.id}
                      step={substep}
                      index={subIndex}
                      isLast={subIndex === step.substeps!.length - 1}
                      onRetry={() => {}}
                      onViewDetails={() => {}}
                      reducedMotion={reducedMotion}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

WorkflowProgress.displayName = 'WorkflowProgress'

export default WorkflowProgress