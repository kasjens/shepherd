'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  MessageCircle, 
  ArrowRight, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Users,
  Network,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Eye,
  EyeOff
} from 'lucide-react'

interface CommunicationEvent {
  id: string
  timestamp: number
  type: 'message_sent' | 'message_received' | 'request' | 'response' | 'broadcast' | 'peer_review'
  fromAgent: string
  toAgent?: string
  messageType: 'request' | 'response' | 'notification' | 'discovery' | 'review' | 'status_update'
  content: string
  status: 'pending' | 'delivered' | 'processed' | 'failed'
  priority: 'low' | 'medium' | 'high'
  conversationId?: string
  responseTime?: number
}

interface AgentConnection {
  fromAgent: string
  toAgent: string
  messageCount: number
  lastActivity: number
  connectionStrength: number
  status: 'active' | 'idle' | 'blocked'
}

interface CommunicationStats {
  totalMessages: number
  averageResponseTime: number
  activeConversations: number
  successRate: number
  messagesByType: Record<string, number>
  agentActivity: Record<string, {
    sent: number
    received: number
    responseTime: number
  }>
}

interface CommunicationFlowProps {
  onEventSelect?: (eventId: string) => void
  maxEvents?: number
}

function getEventTypeIcon(type: CommunicationEvent['type']) {
  switch (type) {
    case 'message_sent':
    case 'message_received':
      return <MessageCircle className="h-3 w-3" />
    case 'request':
      return <ArrowRight className="h-3 w-3" />
    case 'response':
      return <CheckCircle className="h-3 w-3" />
    case 'broadcast':
      return <Zap className="h-3 w-3" />
    case 'peer_review':
      return <Eye className="h-3 w-3" />
    default:
      return <MessageCircle className="h-3 w-3" />
  }
}

function getEventTypeColor(type: CommunicationEvent['type']): string {
  switch (type) {
    case 'message_sent':
      return 'text-blue-600 bg-blue-50'
    case 'message_received':
      return 'text-green-600 bg-green-50'
    case 'request':
      return 'text-orange-600 bg-orange-50'
    case 'response':
      return 'text-purple-600 bg-purple-50'
    case 'broadcast':
      return 'text-yellow-600 bg-yellow-50'
    case 'peer_review':
      return 'text-indigo-600 bg-indigo-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

function getStatusIcon(status: CommunicationEvent['status']) {
  switch (status) {
    case 'pending':
      return <Clock className="h-3 w-3 text-yellow-600" />
    case 'delivered':
      return <ArrowRight className="h-3 w-3 text-blue-600" />
    case 'processed':
      return <CheckCircle className="h-3 w-3 text-green-600" />
    case 'failed':
      return <AlertCircle className="h-3 w-3 text-red-600" />
    default:
      return <Clock className="h-3 w-3" />
  }
}

function formatResponseTime(responseTime?: number): string {
  if (!responseTime) return 'N/A'
  if (responseTime < 1000) return `${responseTime}ms`
  return `${(responseTime / 1000).toFixed(1)}s`
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  
  if (minutes > 0) return `${minutes}m ago`
  return `${seconds}s ago`
}

export function CommunicationEventItem({ 
  event, 
  onClick 
}: { 
  event: CommunicationEvent
  onClick?: () => void 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="flex items-start gap-3 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <div className={`p-1 rounded-full ${getEventTypeColor(event.type)}`}>
        {getEventTypeIcon(event.type)}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">{event.fromAgent}</span>
          {event.toAgent ? (
            <>
              <ArrowRight className="h-3 w-3 text-muted-foreground" />
              <span className="text-sm font-medium">{event.toAgent}</span>
            </>
          ) : (
            <Badge variant="outline" className="text-xs">
              broadcast
            </Badge>
          )}
          <div className="flex items-center gap-1 ml-auto">
            {getStatusIcon(event.status)}
            <Badge 
              variant={event.priority === 'high' ? 'destructive' : 
                      event.priority === 'medium' ? 'default' : 'secondary'} 
              className="text-xs"
            >
              {event.priority}
            </Badge>
          </div>
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-2 mb-1">
          {event.content}
        </p>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Badge variant="outline" className="text-xs px-1 py-0">
            {event.messageType}
          </Badge>
          <span>•</span>
          <span>{formatRelativeTime(event.timestamp)}</span>
          {event.responseTime && (
            <>
              <span>•</span>
              <span>{formatResponseTime(event.responseTime)}</span>
            </>
          )}
          {event.conversationId && (
            <>
              <span>•</span>
              <span className="font-mono">#{event.conversationId.slice(-6)}</span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export function CommunicationNetwork({ connections }: { connections: AgentConnection[] }) {
  const [selectedConnection, setSelectedConnection] = useState<string | null>(null)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Network className="h-4 w-4" />
          Communication Network
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {connections.map((connection, index) => {
            const connectionKey = `${connection.fromAgent}-${connection.toAgent}`
            return (
              <div
                key={connectionKey}
                className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedConnection === connectionKey ? 'ring-2 ring-primary ring-offset-2' : ''
                }`}
                onClick={() => setSelectedConnection(
                  selectedConnection === connectionKey ? null : connectionKey
                )}
              >
                <div className="flex items-center gap-3 flex-1">
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium">{connection.fromAgent}</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                    <span className="text-sm font-medium">{connection.toAgent}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-auto">
                    <Badge 
                      variant={connection.status === 'active' ? 'default' : 
                              connection.status === 'idle' ? 'secondary' : 'destructive'}
                      className="text-xs"
                    >
                      {connection.status}
                    </Badge>
                    
                    <div className="text-right">
                      <div className="text-xs font-medium">{connection.messageCount} msgs</div>
                      <div className="text-xs text-muted-foreground">
                        {formatRelativeTime(connection.lastActivity)}
                      </div>
                    </div>
                  </div>
                </div>
                
                {selectedConnection === connectionKey && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="w-full mt-3 pt-3 border-t border-border"
                  >
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div>
                        <div className="text-muted-foreground">Messages</div>
                        <div className="font-medium">{connection.messageCount}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Strength</div>
                        <div className="font-medium">{Math.round(connection.connectionStrength * 100)}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Status</div>
                        <div className="font-medium capitalize">{connection.status}</div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export function CommunicationStatsPanel({ stats }: { stats: CommunicationStats }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{stats.totalMessages}</div>
          <div className="text-sm text-muted-foreground">Total Messages</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{formatResponseTime(stats.averageResponseTime)}</div>
          <div className="text-sm text-muted-foreground">Avg Response</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{stats.activeConversations}</div>
          <div className="text-sm text-muted-foreground">Active Convos</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{Math.round(stats.successRate * 100)}%</div>
          <div className="text-sm text-muted-foreground">Success Rate</div>
        </CardContent>
      </Card>
    </div>
  )
}

export function CommunicationFlow({ 
  onEventSelect, 
  maxEvents = 20 
}: CommunicationFlowProps) {
  const [events, setEvents] = useState<CommunicationEvent[]>([])
  const [connections, setConnections] = useState<AgentConnection[]>([])
  const [stats, setStats] = useState<CommunicationStats>({
    totalMessages: 0,
    averageResponseTime: 0,
    activeConversations: 0,
    successRate: 0,
    messagesByType: {},
    agentActivity: {}
  })
  const [isConnected, setIsConnected] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [filterType, setFilterType] = useState<CommunicationEvent['type'] | 'all'>('all')

  useEffect(() => {
    if (isPaused) return

    // Subscribe to communication events via WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/communication')
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('Connected to communication WebSocket')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'communication_event') {
          setEvents(prev => [data.event, ...prev].slice(0, maxEvents))
        } else if (data.type === 'communication_stats') {
          setStats(data.stats)
        } else if (data.type === 'connection_update') {
          setConnections(prev => {
            const updated = [...prev]
            const index = updated.findIndex(c => 
              c.fromAgent === data.connection.fromAgent && 
              c.toAgent === data.connection.toAgent
            )
            if (index >= 0) {
              updated[index] = data.connection
            } else {
              updated.push(data.connection)
            }
            return updated
          })
        }
      } catch (error) {
        console.error('Error parsing communication WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('Disconnected from communication WebSocket')
    }
    
    ws.onerror = (error) => {
      console.error('Communication WebSocket error:', error)
      setIsConnected(false)
    }
    
    return () => {
      ws.close()
    }
  }, [isPaused, maxEvents])

  // Mock data for development/demo
  useEffect(() => {
    if (events.length === 0) {
      const mockEvents: CommunicationEvent[] = [
        {
          id: '1',
          timestamp: Date.now() - 10000,
          type: 'request',
          fromAgent: 'TaskAgent-001',
          toAgent: 'LearningAgent-002',
          messageType: 'request',
          content: 'Request peer review for task completion analysis',
          status: 'processed',
          priority: 'medium',
          conversationId: 'conv-123',
          responseTime: 1200
        },
        {
          id: '2',
          timestamp: Date.now() - 25000,
          type: 'broadcast',
          fromAgent: 'SystemAgent-000',
          messageType: 'notification',
          content: 'System maintenance scheduled for tonight',
          status: 'delivered',
          priority: 'high',
          conversationId: 'broadcast-456'
        },
        {
          id: '3',
          timestamp: Date.now() - 40000,
          type: 'response',
          fromAgent: 'AnalysisAgent-003',
          toAgent: 'TaskAgent-001',
          messageType: 'response',
          content: 'Data analysis complete. Found 3 optimization opportunities.',
          status: 'processed',
          priority: 'medium',
          conversationId: 'conv-789',
          responseTime: 800
        }
      ]
      setEvents(mockEvents)

      const mockConnections: AgentConnection[] = [
        {
          fromAgent: 'TaskAgent-001',
          toAgent: 'LearningAgent-002',
          messageCount: 15,
          lastActivity: Date.now() - 10000,
          connectionStrength: 0.85,
          status: 'active'
        },
        {
          fromAgent: 'AnalysisAgent-003',
          toAgent: 'TaskAgent-001',
          messageCount: 8,
          lastActivity: Date.now() - 40000,
          connectionStrength: 0.72,
          status: 'idle'
        }
      ]
      setConnections(mockConnections)

      setStats({
        totalMessages: 23,
        averageResponseTime: 950,
        activeConversations: 3,
        successRate: 0.91,
        messagesByType: {
          request: 8,
          response: 7,
          notification: 5,
          discovery: 3
        },
        agentActivity: {
          'TaskAgent-001': { sent: 5, received: 8, responseTime: 1100 },
          'LearningAgent-002': { sent: 8, received: 5, responseTime: 800 },
          'AnalysisAgent-003': { sent: 3, received: 2, responseTime: 650 }
        }
      })
    }
  }, [events.length])

  const filteredEvents = events.filter(event => 
    filterType === 'all' || event.type === filterType
  )

  const eventTypes: Array<CommunicationEvent['type'] | 'all'> = [
    'all', 'message_sent', 'message_received', 'request', 'response', 'broadcast', 'peer_review'
  ]

  const clearEvents = () => {
    setEvents([])
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Communication Flow</h2>
          <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
            className="text-xs h-7"
          >
            {isPaused ? (
              <>
                <Play className="h-3 w-3 mr-1" />
                Resume
              </>
            ) : (
              <>
                <Pause className="h-3 w-3 mr-1" />
                Pause
              </>
            )}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={clearEvents}
            className="text-xs h-7"
          >
            <RotateCcw className="h-3 w-3 mr-1" />
            Clear
          </Button>
        </div>
      </div>
      
      <CommunicationStatsPanel stats={stats} />
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Recent Events
            </CardTitle>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {eventTypes.map((type) => (
                <Button
                  key={type}
                  variant={filterType === type ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterType(type)}
                  className="text-xs h-7"
                >
                  {type === 'all' ? 'All' : type.replace('_', ' ')}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent className="max-h-96 overflow-y-auto">
            <div className="space-y-2">
              <AnimatePresence>
                {filteredEvents.length > 0 ? (
                  filteredEvents.map((event) => (
                    <CommunicationEventItem
                      key={event.id}
                      event={event}
                      onClick={() => onEventSelect?.(event.id)}
                    />
                  ))
                ) : (
                  <div className="text-center py-8 text-sm text-muted-foreground">
                    {isPaused ? 'Communication flow paused' : 'No communication events yet'}
                  </div>
                )}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
        
        <CommunicationNetwork connections={connections} />
      </div>
    </div>
  )
}