'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Settings, HelpCircle, Search, MessageSquare, Package } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className={cn("sidebar-panel", className)}>
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-shepherd-blue rounded-sm flex items-center justify-center text-white text-sm font-bold">
              🐑
            </div>
            {!isCollapsed && <span className="font-semibold text-lg">Shepherd</span>}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-8 w-8"
          >
            <MessageSquare className="h-4 w-4" />
          </Button>
        </div>
        {!isCollapsed && (
          <Button className="w-full" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        )}
      </div>

      {/* Search */}
      {!isCollapsed && (
        <div className="p-4 border-b border-border">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-gray" />
            <Input
              placeholder="Search conversations..."
              className="pl-9 h-9"
            />
          </div>
        </div>
      )}

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="text-xs font-medium text-muted-gray uppercase tracking-wide mb-3">
            📋 CONVERSATIONS
          </div>
          
          {/* Sample conversations */}
          <div className="space-y-2">
            <div className="p-3 rounded-lg hover:bg-accent cursor-pointer border-l-2 border-shepherd-blue bg-primary/5">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-shepherd-blue rounded-full" />
                <span className="font-medium text-sm">Server Performance Analysis</span>
              </div>
              <div className="text-xs text-muted-gray">2 artifacts • 15m ago</div>
            </div>
            
            <div className="p-3 rounded-lg hover:bg-accent cursor-pointer">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-muted-gray rounded-full" />
                <span className="font-medium text-sm">React Authentication Setup</span>
              </div>
              <div className="text-xs text-muted-gray">1 artifact • 1h ago</div>
            </div>
            
            <div className="p-3 rounded-lg hover:bg-accent cursor-pointer">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-muted-gray rounded-full" />
                <span className="font-medium text-sm">Database Optimization</span>
              </div>
              <div className="text-xs text-muted-gray">3 artifacts • 2h ago</div>
            </div>
          </div>
        </div>

        {/* Artifacts */}
        <div className="p-4 border-t border-border">
          <div className="text-xs font-medium text-muted-gray uppercase tracking-wide mb-3">
            📦 ARTIFACTS
          </div>
          
          <div className="space-y-2">
            <div className="p-2 rounded hover:bg-accent cursor-pointer">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-muted-gray" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">system_analysis.py</div>
                  <div className="text-xs text-muted-gray">Python Script • 12m ago</div>
                </div>
              </div>
            </div>
            
            <div className="p-2 rounded hover:bg-accent cursor-pointer">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-muted-gray" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">performance_report.md</div>
                  <div className="text-xs text-muted-gray">Report • 15m ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border space-y-2">
        <Button variant="ghost" className="w-full justify-start" size="sm">
          <Settings className="h-4 w-4 mr-2" />
          {!isCollapsed && "Settings"}
        </Button>
        <Button variant="ghost" className="w-full justify-start" size="sm">
          <HelpCircle className="h-4 w-4 mr-2" />
          {!isCollapsed && "Help"}
        </Button>
        {!isCollapsed && (
          <div className="text-xs text-muted-gray mt-2">
            Status: ● Connected to Ollama
          </div>
        )}
      </div>
    </div>
  )
}