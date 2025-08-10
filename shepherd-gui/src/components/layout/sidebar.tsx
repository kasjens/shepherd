'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Plus, 
  Settings, 
  HelpCircle, 
  Search, 
  PanelLeftClose, 
  PanelLeftOpen,
  Package,
  BarChart3,
  History,
  Download,
  TrendingUp,
  Activity,
  Brain
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ProjectFolderSelector } from '@/components/features/settings/project-folder-selector'
import { AnalyticsModal } from '@/components/features/modals/analytics-modal'
import { ArtifactsModal } from '@/components/features/modals/artifacts-modal'
import { SettingsModal } from '@/components/features/modals/settings-modal'

interface SidebarProps {
  className?: string
  width?: number
  isCollapsed?: boolean
  onCollapsedChange?: (collapsed: boolean) => void
}

export function Sidebar({ className, width = 320, isCollapsed = false, onCollapsedChange }: SidebarProps) {
  const [analyticsOpen, setAnalyticsOpen] = useState(false)
  const [artifactsOpen, setArtifactsOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)

  const handleToggleCollapse = () => {
    onCollapsedChange?.(!isCollapsed)
  }

  return (
    <>
      <div 
        className={cn(
          "terminal-panel border-r flex flex-col h-full transition-all duration-200 ease-out",
          className
        )}
        style={{ 
          width: isCollapsed ? '48px' : `${width}px`,
          minWidth: isCollapsed ? '48px' : '200px',
          maxWidth: isCollapsed ? '48px' : '600px'
        }}
      >
        {/* Header */}
        <div className={cn("terminal-header", isCollapsed ? "p-2" : "p-4")}>
          <div className={cn("flex items-center", isCollapsed ? "justify-center mb-2" : "justify-between mb-4")}>
            {!isCollapsed && (
              <div className="flex items-center gap-3">
                <img 
                  src="/Shepherd.png" 
                  alt="Shepherd Logo" 
                  className="w-6 h-6 object-contain"
                />
                <span className="font-semibold text-lg" style={{ color: 'var(--foreground)' }}>Shepherd</span>
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleToggleCollapse}
              className="h-8 w-8"
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? (
                <PanelLeftOpen className="h-4 w-4" />
              ) : (
                <PanelLeftClose className="h-4 w-4" />
              )}
            </Button>
          </div>
          {!isCollapsed && (
            <Button className="w-full shepherd-button-primary" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          )}
        </div>

        {/* Content - only show when not collapsed */}
        {!isCollapsed && (
          <>
            {/* Search */}
            <div className="p-4 terminal-header">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" style={{ color: 'var(--muted-gray)' }} />
                <Input
                  placeholder="Search conversations..."
                  className="pl-9 h-9 bg-transparent border"
                  style={{ borderColor: 'var(--border-color)', color: 'var(--foreground)' }}
                />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-4 space-y-2">
              <div className="text-xs font-medium text-muted-gray uppercase tracking-wide mb-3">
                ⚡ QUICK ACTIONS
              </div>
              
              <Button 
                variant="ghost" 
                className="w-full justify-start" 
                size="sm"
                onClick={() => setArtifactsOpen(true)}
              >
                <Package className="h-4 w-4 mr-2" />
                Artifacts
                <Badge variant="secondary" className="ml-auto text-xs">3</Badge>
              </Button>
              
              <Button 
                variant="ghost" 
                className="w-full justify-start" 
                size="sm"
                onClick={() => setAnalyticsOpen(true)}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Analytics
              </Button>
              
              <Button variant="ghost" className="w-full justify-start" size="sm">
                <History className="h-4 w-4 mr-2" />
                History
              </Button>
              
              <Button variant="ghost" className="w-full justify-start" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>

            {/* Conversations */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-4">
                <div className="text-xs font-medium text-muted-gray uppercase tracking-wide mb-3">
                  💬 CONVERSATIONS
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
            </div>

            {/* Resource Usage */}
            <div className="p-4 border-t border-gray-200">
              <div className="text-xs font-medium text-muted-gray uppercase tracking-wide mb-3">
                📊 RESOURCE USAGE
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-3 w-3 text-green-500" />
                    <span className="text-xs">CPU</span>
                  </div>
                  <span className="text-xs font-medium">45%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="h-3 w-3 text-blue-500" />
                    <span className="text-xs">Memory</span>
                  </div>
                  <span className="text-xs font-medium">6.2GB</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-3 w-3 text-purple-500" />
                    <span className="text-xs">Tokens</span>
                  </div>
                  <span className="text-xs font-medium">12.4K</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 space-y-4">
              {/* Project Folder Selector */}
              <ProjectFolderSelector />
              
              {/* Settings and Help */}
              <div className="space-y-2">
                <Button 
                  variant="ghost" 
                  className="w-full justify-start" 
                  size="sm"
                  onClick={() => setSettingsOpen(true)}
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
                <Button variant="ghost" className="w-full justify-start" size="sm">
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Help
                </Button>
              </div>
              
              {/* Status */}
              <div className="space-y-1">
                <div className="text-xs" style={{ color: 'var(--muted-gray)' }}>
                  <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Connected to Ollama
                </div>
                <div className="text-xs" style={{ color: 'var(--muted-gray)' }}>
                  <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  7 Active Agents
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Modals */}
      <AnalyticsModal 
        open={analyticsOpen} 
        onOpenChange={setAnalyticsOpen} 
      />
      <ArtifactsModal 
        open={artifactsOpen} 
        onOpenChange={setArtifactsOpen} 
      />
      <SettingsModal 
        open={settingsOpen} 
        onOpenChange={setSettingsOpen} 
      />
    </>
  )
}