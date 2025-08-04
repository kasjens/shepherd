'use client'

import React, { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  Zap,
  BarChart3,
  Monitor,
  Server,
  Database,
  Network,
  Timer,
  Target
} from 'lucide-react'

interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    temperature?: number
    load: number[]
  }
  memory: {
    used: number
    total: number
    usage: number
    available: number
  }
  disk: {
    used: number
    total: number
    usage: number
    readSpeed: number
    writeSpeed: number
  }
  network: {
    bytesIn: number
    bytesOut: number
    packetsIn: number
    packetsOut: number
    latency: number
  }
}

interface WorkflowMetrics {
  totalExecutions: number
  successfulExecutions: number
  failedExecutions: number
  averageExecutionTime: number
  averageResponseTime: number
  executionsPerMinute: number
  successRate: number
  currentActiveWorkflows: number
  queuedWorkflows: number
  executionTimeByPattern: Record<string, number>
  errorsByType: Record<string, number>
}

interface AgentMetrics {
  totalAgents: number
  activeAgents: number
  idleAgents: number
  averageTasksPerAgent: number
  averageAgentResponseTime: number
  agentEfficiency: number
  toolUsageCount: number
  communicationEvents: number
  memoryOperations: number
  learningEvents: number
}

interface PerformanceAlert {
  id: string
  type: 'warning' | 'error' | 'info'
  component: 'system' | 'workflow' | 'agent' | 'memory' | 'learning'
  title: string
  description: string
  value?: number
  threshold?: number
  timestamp: number
  acknowledged: boolean
}

interface MetricsTrend {
  metric: string
  current: number
  previous: number
  change: number
  trend: 'up' | 'down' | 'stable'
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

function getTrendIcon(trend: 'up' | 'down' | 'stable', isGood: boolean = true) {
  if (trend === 'stable') return <Minus className="h-4 w-4 text-gray-500" />
  
  const color = (trend === 'up' && isGood) || (trend === 'down' && !isGood) 
    ? 'text-green-500' : 'text-red-500'
  
  return trend === 'up' 
    ? <TrendingUp className={`h-4 w-4 ${color}`} />
    : <TrendingDown className={`h-4 w-4 ${color}`} />
}

export function SystemMetricsPanel({ metrics }: { metrics: SystemMetrics }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Cpu className="h-4 w-4" />
            CPU Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{metrics.cpu.usage.toFixed(1)}%</span>
              <Badge variant={metrics.cpu.usage > 80 ? 'destructive' : 'outline'}>
                {metrics.cpu.cores} cores
              </Badge>
            </div>
            <Progress value={metrics.cpu.usage} className="h-2" />
            {metrics.cpu.temperature && (
              <div className="text-xs text-muted-foreground">
                Temp: {metrics.cpu.temperature}°C
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <HardDrive className="h-4 w-4" />
            Memory
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{metrics.memory.usage.toFixed(1)}%</span>
              <span className="text-xs text-muted-foreground">
                {formatBytes(metrics.memory.used)} / {formatBytes(metrics.memory.total)}
              </span>
            </div>
            <Progress value={metrics.memory.usage} className="h-2" />
            <div className="text-xs text-muted-foreground">
              Available: {formatBytes(metrics.memory.available)}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Database className="h-4 w-4" />
            Disk I/O
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{metrics.disk.usage.toFixed(1)}%</span>
              <span className="text-xs text-muted-foreground">
                {formatBytes(metrics.disk.used)} / {formatBytes(metrics.disk.total)}
              </span>
            </div>
            <Progress value={metrics.disk.usage} className="h-2" />
            <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
              <div>R: {formatBytes(metrics.disk.readSpeed)}/s</div>
              <div>W: {formatBytes(metrics.disk.writeSpeed)}/s</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Network className="h-4 w-4" />
            Network
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{metrics.network.latency}ms</span>
              <Badge variant={metrics.network.latency > 100 ? 'destructive' : 'outline'}>
                latency
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <div className="text-muted-foreground">In:</div>
                <div className="font-medium">{formatBytes(metrics.network.bytesIn)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Out:</div>
                <div className="font-medium">{formatBytes(metrics.network.bytesOut)}</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export function WorkflowMetricsPanel({ metrics }: { metrics: WorkflowMetrics }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Workflow Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold">{metrics.totalExecutions}</div>
            <div className="text-sm text-muted-foreground">Total Executions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{metrics.successfulExecutions}</div>
            <div className="text-sm text-muted-foreground">Successful</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{metrics.failedExecutions}</div>
            <div className="text-sm text-muted-foreground">Failed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{Math.round(metrics.successRate * 100)}%</div>
            <div className="text-sm text-muted-foreground">Success Rate</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium mb-3">Performance Metrics</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Avg Execution Time</span>
                <span className="font-medium">{formatDuration(metrics.averageExecutionTime)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Avg Response Time</span>
                <span className="font-medium">{formatDuration(metrics.averageResponseTime)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Executions/min</span>
                <span className="font-medium">{metrics.executionsPerMinute.toFixed(1)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Active Workflows</span>
                <span className="font-medium">{metrics.currentActiveWorkflows}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Queued Workflows</span>
                <span className="font-medium">{metrics.queuedWorkflows}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-3">Execution Times by Pattern</h4>
            <div className="space-y-2">
              {Object.entries(metrics.executionTimeByPattern).map(([pattern, time]) => (
                <div key={pattern} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{pattern.toLowerCase()}</span>
                  <span className="font-medium">{formatDuration(time)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {Object.keys(metrics.errorsByType).length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-medium mb-3">Common Errors</h4>
            <div className="space-y-2">
              {Object.entries(metrics.errorsByType).slice(0, 5).map(([error, count]) => (
                <div key={error} className="flex items-center justify-between">
                  <span className="text-sm line-clamp-1">{error}</span>
                  <Badge variant="outline">{count}</Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function AgentMetricsPanel({ metrics }: { metrics: AgentMetrics }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Agent Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold">{metrics.totalAgents}</div>
            <div className="text-sm text-muted-foreground">Total Agents</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{metrics.activeAgents}</div>
            <div className="text-sm text-muted-foreground">Active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{metrics.idleAgents}</div>
            <div className="text-sm text-muted-foreground">Idle</div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Agent Efficiency</span>
              <span className="text-sm font-bold">{Math.round(metrics.agentEfficiency * 100)}%</span>
            </div>
            <Progress value={metrics.agentEfficiency * 100} className="h-2" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">Avg Tasks/Agent</div>
              <div className="text-lg font-bold">{metrics.averageTasksPerAgent.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Avg Response Time</div>
              <div className="text-lg font-bold">{formatDuration(metrics.averageAgentResponseTime)}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-border">
            <div className="text-center">
              <div className="text-lg font-bold">{metrics.toolUsageCount}</div>
              <div className="text-xs text-muted-foreground">Tool Uses</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">{metrics.communicationEvents}</div>
              <div className="text-xs text-muted-foreground">Messages</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">{metrics.memoryOperations}</div>
              <div className="text-xs text-muted-foreground">Memory Ops</div>
            </div>
          </div>

          <div className="pt-4 border-t border-border">
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">{metrics.learningEvents}</div>
              <div className="text-xs text-muted-foreground">Learning Events</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function PerformanceAlertsPanel({ 
  alerts, 
  onAlertAcknowledge 
}: { 
  alerts: PerformanceAlert[]
  onAlertAcknowledge?: (alertId: string) => void 
}) {
  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged)
  const criticalAlerts = unacknowledgedAlerts.filter(alert => alert.type === 'error')
  const warningAlerts = unacknowledgedAlerts.filter(alert => alert.type === 'warning')

  function getAlertIcon(type: PerformanceAlert['type']) {
    switch (type) {
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'info':
        return <CheckCircle className="h-4 w-4 text-blue-600" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          Performance Alerts
          {unacknowledgedAlerts.length > 0 && (
            <Badge variant="destructive" className="ml-auto">
              {unacknowledgedAlerts.length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {unacknowledgedAlerts.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-600" />
            All systems operating normally
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {[...criticalAlerts, ...warningAlerts].map((alert) => (
              <div
                key={alert.id}
                className={`p-3 border rounded-lg ${
                  alert.type === 'error' ? 'border-red-200 bg-red-50' :
                  alert.type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                  'border-blue-200 bg-blue-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getAlertIcon(alert.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium">{alert.title}</h4>
                      <Badge variant="outline" className="text-xs">
                        {alert.component}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-2">
                      {alert.description}
                    </p>
                    
                    {alert.value !== undefined && alert.threshold !== undefined && (
                      <div className="text-xs text-muted-foreground mb-2">
                        Current: {alert.value} | Threshold: {alert.threshold}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onAlertAcknowledge?.(alert.id)}
                        className="text-xs h-6"
                      >
                        Acknowledge
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function MetricsTrendsPanel({ trends }: { trends: MetricsTrend[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Performance Trends
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {trends.map((trend, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div>
                <div className="text-sm font-medium">{trend.metric}</div>
                <div className="text-xs text-muted-foreground">
                  Previous: {trend.previous.toFixed(2)}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <div className="text-sm font-bold">{trend.current.toFixed(2)}</div>
                  <div className={`text-xs ${
                    trend.change > 0 ? 'text-green-600' : 
                    trend.change < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
                  </div>
                </div>
                {getTrendIcon(trend.trend, trend.metric.includes('Error') ? false : true)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function PerformanceMetricsDashboard() {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: { usage: 45.2, cores: 8, temperature: 65, load: [0.4, 0.5, 0.3] },
    memory: { used: 8.5 * 1024 * 1024 * 1024, total: 16 * 1024 * 1024 * 1024, usage: 53.1, available: 7.5 * 1024 * 1024 * 1024 },
    disk: { used: 120 * 1024 * 1024 * 1024, total: 500 * 1024 * 1024 * 1024, usage: 24.0, readSpeed: 150 * 1024 * 1024, writeSpeed: 80 * 1024 * 1024 },
    network: { bytesIn: 1.2 * 1024 * 1024, bytesOut: 800 * 1024, packetsIn: 1200, packetsOut: 850, latency: 12 }
  })

  const [workflowMetrics, setWorkflowMetrics] = useState<WorkflowMetrics>({
    totalExecutions: 1247,
    successfulExecutions: 1134,
    failedExecutions: 113,
    averageExecutionTime: 2340,
    averageResponseTime: 450,
    executionsPerMinute: 5.7,
    successRate: 0.91,
    currentActiveWorkflows: 8,
    queuedWorkflows: 3,
    executionTimeByPattern: {
      SEQUENTIAL: 1800,
      PARALLEL: 1200,
      CONDITIONAL: 2800,
      ITERATIVE: 3500,
      HIERARCHICAL: 4200
    },
    errorsByType: {
      'TimeoutError': 45,
      'ValidationError': 28,
      'ResourceError': 23,
      'NetworkError': 17
    }
  })

  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics>({
    totalAgents: 12,
    activeAgents: 7,
    idleAgents: 5,
    averageTasksPerAgent: 8.3,
    averageAgentResponseTime: 1200,
    agentEfficiency: 0.87,
    toolUsageCount: 234,
    communicationEvents: 456,
    memoryOperations: 1834,
    learningEvents: 67
  })

  const [alerts, setAlerts] = useState<PerformanceAlert[]>([
    {
      id: '1',
      type: 'warning',
      component: 'system',
      title: 'High Memory Usage',
      description: 'Memory usage has exceeded 80% for the past 10 minutes',
      value: 85.3,
      threshold: 80,
      timestamp: Date.now() - 300000,
      acknowledged: false
    },
    {
      id: '2',
      type: 'info',
      component: 'workflow',
      title: 'Performance Improvement',
      description: 'Average execution time has improved by 15% this hour',
      timestamp: Date.now() - 180000,
      acknowledged: false
    }
  ])

  const [trends, setTrends] = useState<MetricsTrend[]>([
    { metric: 'Workflow Success Rate', current: 91.2, previous: 88.7, change: 2.8, trend: 'up' },
    { metric: 'Average Response Time', current: 450, previous: 520, change: -13.5, trend: 'down' },
    { metric: 'Agent Efficiency', current: 87.3, previous: 85.1, change: 2.6, trend: 'up' },
    { metric: 'Memory Usage', current: 53.1, previous: 48.9, change: 8.6, trend: 'up' },
    { metric: 'Error Rate', current: 9.1, previous: 11.3, change: -19.5, trend: 'down' }
  ])

  const handleAlertAcknowledge = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Monitor className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Performance Dashboard</h2>
      </div>
      
      <SystemMetricsPanel metrics={systemMetrics} />
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <WorkflowMetricsPanel metrics={workflowMetrics} />
        <AgentMetricsPanel metrics={agentMetrics} />
      </div>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <PerformanceAlertsPanel 
          alerts={alerts} 
          onAlertAcknowledge={handleAlertAcknowledge} 
        />
        <MetricsTrendsPanel trends={trends} />
      </div>
    </div>
  )
}