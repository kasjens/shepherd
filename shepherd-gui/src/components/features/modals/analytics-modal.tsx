'use client'

import React, { useState } from 'react'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { PerformanceMetricsDashboard } from '@/components/features/performance/metrics-dashboard'
import { AgentCollaborationView } from '@/components/features/agents/agent-collaboration'
import { CommunicationFlow } from '@/components/features/agents/communication-flow'
import { MemoryFlowVisualizer } from '@/components/features/memory/memory-flow'
import { LearningProgressOverview } from '@/components/features/learning/learning-progress'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AnalyticsDashboard, { DashboardConfig } from '@/components/analytics/analytics-dashboard'
import { BarChart3, Activity, MessageSquare, Brain, GraduationCap, LineChart, Settings } from 'lucide-react'

interface AnalyticsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const SAMPLE_DASHBOARD: DashboardConfig = {
  id: 'overview',
  name: 'System Overview',
  layout: [
    { i: 'agents_metric', x: 0, y: 0, w: 3, h: 2 },
    { i: 'conversations_metric', x: 3, y: 0, w: 3, h: 2 },
    { i: 'success_rate_gauge', x: 6, y: 0, w: 3, h: 3 },
    { i: 'system_status', x: 9, y: 0, w: 3, h: 3 },
    { i: 'performance_chart', x: 0, y: 2, w: 6, h: 4 },
    { i: 'resource_progress', x: 0, y: 6, w: 4, h: 3 }
  ],
  widgets: [
    {
      id: 'agents_metric',
      title: 'Active Agents',
      type: 'metric',
      data: {
        value: 8,
        previousValue: 6,
        label: 'Currently Running',
        color: 'blue',
        icon: 'Users'
      }
    },
    {
      id: 'conversations_metric',
      title: 'Conversations Today',
      type: 'metric',
      data: {
        value: 142,
        previousValue: 128,
        label: 'Total Messages',
        color: 'green',
        icon: 'MessageCircle'
      }
    },
    {
      id: 'success_rate_gauge',
      title: 'Success Rate',
      type: 'gauge',
      data: {
        value: 94.5,
        min: 0,
        max: 100,
        label: 'Overall Performance',
        color: 'green',
        thresholds: { warning: 80, critical: 60 }
      }
    },
    {
      id: 'system_status',
      title: 'System Status',
      type: 'status',
      data: {
        services: [
          { name: 'API Server', status: 'healthy', uptime: '99.9%' },
          { name: 'Ollama', status: 'healthy', uptime: '99.8%' },
          { name: 'Database', status: 'healthy', uptime: '99.5%' },
          { name: 'WebSocket', status: 'warning', uptime: '97.2%' }
        ]
      }
    },
    {
      id: 'performance_chart',
      title: 'Performance Over Time',
      type: 'chart',
      data: {
        chartType: 'area',
        data: [
          { time: '00:00', cpu: 45, memory: 62, tokens: 1200 },
          { time: '04:00', cpu: 52, memory: 68, tokens: 1450 },
          { time: '08:00', cpu: 38, memory: 55, tokens: 980 },
          { time: '12:00', cpu: 65, memory: 72, tokens: 1680 },
          { time: '16:00', cpu: 48, memory: 58, tokens: 1320 },
          { time: '20:00', cpu: 42, memory: 61, tokens: 1150 }
        ],
        xKey: 'time',
        yKey: 'cpu',
        colors: ['#3B82F6', '#10B981', '#8B5CF6']
      }
    },
    {
      id: 'resource_progress',
      title: 'Resource Usage',
      type: 'progress',
      data: {
        items: [
          { label: 'CPU Usage', value: 45, color: 'blue' },
          { label: 'Memory', value: 68, color: 'green' },
          { label: 'Disk Space', value: 32, color: 'yellow' },
          { label: 'Token Usage', value: 78, color: 'red' }
        ]
      }
    }
  ],
  settings: {
    autoRefresh: true,
    refreshInterval: 30,
    compactMode: false,
    showGrid: true
  }
}

export function AnalyticsModal({ open, onOpenChange }: AnalyticsModalProps) {
  const [dashboard, setDashboard] = useState<DashboardConfig>(SAMPLE_DASHBOARD)
  const [isEditing, setIsEditing] = useState(false)

  const handleDashboardChange = (config: DashboardConfig) => {
    setDashboard(config)
  }

  const handleSave = (config: DashboardConfig) => {
    setDashboard(config)
    setIsEditing(false)
  }

  const handleExport = (format: 'pdf' | 'png' | 'csv') => {
    console.log(`Exporting dashboard as ${format}`)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-full max-h-full w-screen h-screen m-0 p-0 overflow-hidden">
        <DialogHeader className="sr-only">
          <DialogTitle>Analytics & Performance Dashboard</DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="dashboard" className="flex-1 h-full flex flex-col overflow-hidden">
          <div className="border-b border-gray-200 dark:border-gray-700 px-4 py-2">
            <TabsList className="grid w-full max-w-2xl grid-cols-6">
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <LineChart className="h-4 w-4" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="performance" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Performance
              </TabsTrigger>
              <TabsTrigger value="agents" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Agents
              </TabsTrigger>
              <TabsTrigger value="communication" className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Communication
              </TabsTrigger>
              <TabsTrigger value="memory" className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Memory
              </TabsTrigger>
              <TabsTrigger value="learning" className="flex items-center gap-2">
                <GraduationCap className="h-4 w-4" />
                Learning
              </TabsTrigger>
            </TabsList>
          </div>
          
          <div className="flex-1 overflow-hidden">
            <TabsContent value="dashboard" className="h-full m-0">
              <AnalyticsDashboard
                config={dashboard}
                onConfigChange={handleDashboardChange}
                onSave={handleSave}
                onExport={handleExport}
                isEditing={isEditing}
                onEditToggle={setIsEditing}
              />
            </TabsContent>
            
            <TabsContent value="performance" className="space-y-4 overflow-y-auto h-full p-4">
              <PerformanceMetricsDashboard />
            </TabsContent>
            
            <TabsContent value="agents" className="space-y-4 overflow-y-auto h-full p-4">
              <AgentCollaborationView collaborations={[]} messages={[]} />
            </TabsContent>
            
            <TabsContent value="communication" className="space-y-4 overflow-y-auto h-full p-4">
              <CommunicationFlow onEventSelect={() => {}} />
            </TabsContent>
            
            <TabsContent value="memory" className="space-y-4 overflow-y-auto h-full p-4">
              <MemoryFlowVisualizer onTransferSelect={() => {}} />
            </TabsContent>
            
            <TabsContent value="learning" className="space-y-4 overflow-y-auto h-full p-4">
              <LearningProgressOverview 
                insights={[]} 
                feedbackSummary={{totalFeedback: 0, feedbackByType: {}, averageRating: 0, recentTrend: 'stable', topIssues: []}}
                patternLearning={{totalPatternsLearned: 0, failurePatternsIdentified: 0, activePatternsCached: 0, averagePatternScore: 0, learningBufferSize: 0, recentPatterns: []}}
                adaptationStats={{enabledTypes: [], cacheSize: 0, performanceTracking: {}, knowledgeBase: {preferences: 0, learnedPatterns: 0, failurePatterns: 0}}}
              />
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}