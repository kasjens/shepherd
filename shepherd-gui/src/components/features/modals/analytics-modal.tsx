'use client'

import React from 'react'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { PerformanceMetricsDashboard } from '@/components/features/performance/metrics-dashboard'
import { AgentCollaboration } from '@/components/features/agents/agent-collaboration'
import { CommunicationFlow } from '@/components/features/agents/communication-flow'
import { MemoryFlow } from '@/components/features/memory/memory-flow'
import { LearningProgress } from '@/components/features/learning/learning-progress'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BarChart3, Activity, MessageSquare, Brain, GraduationCap } from 'lucide-react'

interface AnalyticsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AnalyticsModal({ open, onOpenChange }: AnalyticsModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Analytics & Performance
          </DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="performance" className="flex-1 overflow-hidden">
          <TabsList className="grid w-full grid-cols-5">
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
          
          <div className="overflow-y-auto flex-1 mt-4">
            <TabsContent value="performance" className="space-y-4">
              <PerformanceMetricsDashboard />
            </TabsContent>
            
            <TabsContent value="agents" className="space-y-4">
              <AgentCollaboration />
            </TabsContent>
            
            <TabsContent value="communication" className="space-y-4">
              <CommunicationFlow />
            </TabsContent>
            
            <TabsContent value="memory" className="space-y-4">
              <MemoryFlow />
            </TabsContent>
            
            <TabsContent value="learning" className="space-y-4">
              <LearningProgress />
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}