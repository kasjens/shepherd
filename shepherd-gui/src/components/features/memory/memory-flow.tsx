'use client'

import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Database, 
  Share2, 
  Brain, 
  Clock, 
  ArrowRight, 
  Eye, 
  EyeOff,
  Layers,
  Search,
  BookOpen,
  Zap
} from 'lucide-react'

interface MemoryTransfer {
  id: string
  from: string
  to: string
  type: 'discovery' | 'context' | 'learning' | 'knowledge' | 'pattern' | 'preference'
  content: string
  timestamp: number
  size: number
  memoryTier: 'local' | 'shared' | 'persistent' | 'vector'
}

interface MemoryUsage {
  agentId: string
  agentName: string
  local: {
    used: number
    total: number
    operations: number
  }
  shared: {
    reads: number
    writes: number
    subscriptions: string[]
  }
  persistent: {
    patterns: number
    preferences: number
    failures: number
  }
  vector: {
    searches: number
    similarities: number
    embeddings: number
  }
}

interface MemoryFlowVisualizerProps {
  onTransferSelect?: (transferId: string) => void
}

function getTransferTypeIcon(type: MemoryTransfer['type']) {
  switch (type) {
    case 'discovery':
      return <Eye className="h-3 w-3" />
    case 'context':
      return <Share2 className="h-3 w-3" />
    case 'learning':
      return <Brain className="h-3 w-3" />
    case 'knowledge':
      return <BookOpen className="h-3 w-3" />
    case 'pattern':
      return <Zap className="h-3 w-3" />
    case 'preference':
      return <Database className="h-3 w-3" />
    default:
      return <Database className="h-3 w-3" />
  }
}

function getTransferTypeColor(type: MemoryTransfer['type']): string {
  switch (type) {
    case 'discovery':
      return 'text-blue-600 bg-blue-50'
    case 'context':
      return 'text-green-600 bg-green-50'
    case 'learning':
      return 'text-purple-600 bg-purple-50'
    case 'knowledge':
      return 'text-orange-600 bg-orange-50'
    case 'pattern':
      return 'text-yellow-600 bg-yellow-50'
    case 'preference':
      return 'text-pink-600 bg-pink-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

function getMemoryTierIcon(tier: MemoryTransfer['memoryTier']) {
  switch (tier) {
    case 'local':
      return <Database className="h-3 w-3" />
    case 'shared':
      return <Share2 className="h-3 w-3" />
    case 'persistent':
      return <BookOpen className="h-3 w-3" />
    case 'vector':
      return <Search className="h-3 w-3" />
    default:
      return <Database className="h-3 w-3" />
  }
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  
  if (minutes > 0) return `${minutes}m ago`
  return `${seconds}s ago`
}

export function MemoryTransferItem({ 
  transfer, 
  onClick 
}: { 
  transfer: MemoryTransfer
  onClick?: () => void 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex items-start gap-3 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <div className={`p-1 rounded ${getTransferTypeColor(transfer.type)}`}>
        {getTransferTypeIcon(transfer.type)}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">{transfer.from}</span>
          <ArrowRight className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{transfer.to}</span>
          <div className="flex items-center gap-1 ml-auto">
            {getMemoryTierIcon(transfer.memoryTier)}
            <Badge variant="outline" className="text-xs">
              {transfer.memoryTier}
            </Badge>
          </div>
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-2 mb-1">
          {transfer.content}
        </p>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Badge variant="secondary" className="text-xs px-1 py-0">
            {transfer.type}
          </Badge>
          <span>•</span>
          <span>{formatBytes(transfer.size)}</span>
          <span>•</span>
          <span>{formatRelativeTime(transfer.timestamp)}</span>
        </div>
      </div>
    </motion.div>
  )
}

export function MemoryFlowVisualizer({ onTransferSelect }: MemoryFlowVisualizerProps) {
  const [transfers, setTransfers] = useState<MemoryTransfer[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (isPaused) return

    // Subscribe to memory transfer events via WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws')
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('Connected to memory flow WebSocket')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'memory_transfer') {
          setTransfers(prev => [data.transfer, ...prev].slice(0, 20)) // Keep last 20
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('Disconnected from memory flow WebSocket')
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }
    
    return () => {
      ws.close()
    }
  }, [isPaused])

  // Mock data for development/demo
  useEffect(() => {
    if (transfers.length === 0) {
      const mockTransfers: MemoryTransfer[] = [
        {
          id: '1',
          from: 'TaskAgent-001',
          to: 'SharedContext',
          type: 'discovery',
          content: 'Found optimization pattern for data processing',
          timestamp: Date.now() - 30000,
          size: 1024,
          memoryTier: 'shared'
        },
        {
          id: '2',
          from: 'LearningAgent-002',
          to: 'VectorStore',
          type: 'pattern',
          content: 'Successful workflow pattern: sequential processing with parallel validation',
          timestamp: Date.now() - 45000,
          size: 2048,
          memoryTier: 'vector'
        },
        {
          id: '3',
          from: 'UserInterface',
          to: 'PersistentKnowledge',
          type: 'preference',
          content: 'User prefers detailed progress reporting',
          timestamp: Date.now() - 60000,
          size: 512,
          memoryTier: 'persistent'
        }
      ]
      setTransfers(mockTransfers)
    }
  }, [transfers.length])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Memory Flow
          <div className="flex items-center gap-2 ml-auto">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPaused(!isPaused)}
              className="text-xs h-7"
            >
              {isPaused ? (
                <>
                  <Eye className="h-3 w-3 mr-1" />
                  Resume
                </>
              ) : (
                <>
                  <EyeOff className="h-3 w-3 mr-1" />
                  Pause
                </>
              )}
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="max-h-96 overflow-y-auto">
        <div className="space-y-2">
          <AnimatePresence>
            {transfers.length > 0 ? (
              transfers.map((transfer) => (
                <MemoryTransferItem
                  key={transfer.id}
                  transfer={transfer}
                  onClick={() => onTransferSelect?.(transfer.id)}
                />
              ))
            ) : (
              <div className="text-center py-8 text-sm text-muted-foreground">
                {isPaused ? 'Memory flow paused' : 'No memory transfers yet'}
              </div>
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  )
}

export function MemoryUsagePanel({ usages }: { usages: MemoryUsage[] }) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-4 w-4" />
          Memory Usage by Agent
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {usages.map((usage) => (
            <div
              key={usage.agentId}
              className={`border rounded-lg p-3 cursor-pointer transition-all hover:shadow-md ${
                selectedAgent === usage.agentId ? 'ring-2 ring-primary ring-offset-2' : ''
              }`}
              onClick={() => setSelectedAgent(
                selectedAgent === usage.agentId ? null : usage.agentId
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{usage.agentName}</span>
                <Badge variant="outline" className="text-xs">
                  {Math.round((usage.local.used / usage.local.total) * 100)}% local
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <div className="text-muted-foreground mb-1">Local</div>
                  <div className="font-medium">
                    {formatBytes(usage.local.used)} / {formatBytes(usage.local.total)}
                  </div>
                  <div className="text-muted-foreground">
                    {usage.local.operations} ops
                  </div>
                </div>
                
                <div>
                  <div className="text-muted-foreground mb-1">Shared</div>
                  <div className="font-medium">
                    {usage.shared.reads}R / {usage.shared.writes}W
                  </div>
                  <div className="text-muted-foreground">
                    {usage.shared.subscriptions.length} subs
                  </div>
                </div>
                
                <div>
                  <div className="text-muted-foreground mb-1">Persistent</div>
                  <div className="font-medium">
                    {usage.persistent.patterns} patterns
                  </div>
                  <div className="text-muted-foreground">
                    {usage.persistent.preferences} prefs
                  </div>
                </div>
                
                <div>
                  <div className="text-muted-foreground mb-1">Vector</div>
                  <div className="font-medium">
                    {usage.vector.searches} searches
                  </div>
                  <div className="text-muted-foreground">
                    {usage.vector.embeddings} embeddings
                  </div>
                </div>
              </div>
              
              {selectedAgent === usage.agentId && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-3 pt-3 border-t border-border"
                >
                  <div className="space-y-2">
                    <div>
                      <div className="text-xs font-medium mb-1">Shared Context Subscriptions</div>
                      <div className="flex flex-wrap gap-1">
                        {usage.shared.subscriptions.length > 0 ? (
                          usage.shared.subscriptions.map((sub, index) => (
                            <Badge key={index} variant="secondary" className="text-xs px-1 py-0">
                              {sub}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-xs text-muted-foreground">No subscriptions</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div>
                        <div className="font-medium">{usage.persistent.patterns}</div>
                        <div className="text-muted-foreground">Learned Patterns</div>
                      </div>
                      <div>
                        <div className="font-medium">{usage.persistent.preferences}</div>
                        <div className="text-muted-foreground">User Preferences</div>
                      </div>
                      <div>
                        <div className="font-medium">{usage.persistent.failures}</div>
                        <div className="text-muted-foreground">Failure Patterns</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function MemoryStats({ transfers, usages }: {
  transfers: MemoryTransfer[]
  usages: MemoryUsage[]
}) {
  const totalTransfers = transfers.length
  const transfersByType = transfers.reduce((acc, transfer) => {
    acc[transfer.type] = (acc[transfer.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const totalMemoryUsed = usages.reduce((sum, usage) => sum + usage.local.used, 0)
  const totalOperations = usages.reduce((sum, usage) => sum + usage.local.operations, 0)

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{totalTransfers}</div>
          <div className="text-sm text-muted-foreground">Memory Transfers</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{formatBytes(totalMemoryUsed)}</div>
          <div className="text-sm text-muted-foreground">Memory Used</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{totalOperations}</div>
          <div className="text-sm text-muted-foreground">Total Operations</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{usages.length}</div>
          <div className="text-sm text-muted-foreground">Active Agents</div>
        </CardContent>
      </Card>
    </div>
  )
}