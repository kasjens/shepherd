'use client'

import React, { useState, useEffect } from 'react'
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
  Eye,
  EyeOff
} from 'lucide-react'

interface AgentMessage {
  id: string
  fromAgent: string
  toAgent: string
  messageType: 'request' | 'response' | 'notification' | 'discovery' | 'review'
  content: string
  timestamp: number
  status: 'sent' | 'delivered' | 'processed' | 'failed'
  priority?: 'low' | 'medium' | 'high'
}

interface AgentCollaboration {
  agentId: string
  agentName: string
  connections: string[]
  messagesExchanged: number
  collaborationScore: number
  activeConversations: number
  lastActivity: number
}

interface AgentCollaborationViewProps {
  collaborations: AgentCollaboration[]
  messages: AgentMessage[]
  onMessageSelect?: (messageId: string) => void
}

function getMessageTypeIcon(type: AgentMessage['messageType']) {
  switch (type) {
    case 'request':
      return <MessageCircle className="h-3 w-3" />
    case 'response':
      return <ArrowRight className="h-3 w-3" />
    case 'notification':
      return <AlertCircle className="h-3 w-3" />
    case 'discovery':
      return <Eye className="h-3 w-3" />
    case 'review':
      return <CheckCircle className="h-3 w-3" />
    default:
      return <MessageCircle className="h-3 w-3" />
  }
}

function getMessageTypeColor(type: AgentMessage['messageType']): string {
  switch (type) {
    case 'request':
      return 'text-blue-600'
    case 'response':
      return 'text-green-600'
    case 'notification':
      return 'text-yellow-600'
    case 'discovery':
      return 'text-purple-600'
    case 'review':
      return 'text-indigo-600'
    default:
      return 'text-gray-600'
  }
}

function getStatusIcon(status: AgentMessage['status']) {
  switch (status) {
    case 'sent':
      return <Clock className="h-3 w-3" />
    case 'delivered':
      return <ArrowRight className="h-3 w-3" />
    case 'processed':
      return <CheckCircle className="h-3 w-3" />
    case 'failed':
      return <AlertCircle className="h-3 w-3" />
    default:
      return <Clock className="h-3 w-3" />
  }
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return `${seconds}s ago`
}

export function MessageItem({ message, onClick }: { 
  message: AgentMessage
  onClick?: () => void 
}) {
  return (
    <div 
      className="flex items-start gap-3 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <div className={`flex items-center gap-1 ${getMessageTypeColor(message.messageType)}`}>
        {getMessageTypeIcon(message.messageType)}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">{message.fromAgent}</span>
          <ArrowRight className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{message.toAgent}</span>
          <Badge variant="outline" className="text-xs ml-auto">
            {message.messageType}
          </Badge>
        </div>
        
        <p className="text-sm text-muted-foreground line-clamp-2 mb-1">
          {message.content}
        </p>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            {getStatusIcon(message.status)}
            <span>{message.status}</span>
          </div>
          <span>•</span>
          <span>{formatRelativeTime(message.timestamp)}</span>
          {message.priority && message.priority !== 'medium' && (
            <>
              <span>•</span>
              <Badge 
                variant={message.priority === 'high' ? 'destructive' : 'secondary'} 
                className="text-xs px-1 py-0"
              >
                {message.priority}
              </Badge>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export function CollaborationNetwork({ collaborations }: { collaborations: AgentCollaboration[] }) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Network className="h-4 w-4" />
          Collaboration Network
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {collaborations.map((collab) => (
            <div
              key={collab.agentId}
              className={`p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                selectedAgent === collab.agentId ? 'ring-2 ring-primary ring-offset-2' : ''
              }`}
              onClick={() => setSelectedAgent(collab.agentId)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{collab.agentName}</span>
                <Badge variant="outline" className="text-xs">
                  {collab.activeConversations} active
                </Badge>
              </div>
              
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Connections:</span>
                  <span>{collab.connections.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Messages:</span>
                  <span>{collab.messagesExchanged}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Score:</span>
                  <span className="font-medium">
                    {Math.round(collab.collaborationScore * 100)}%
                  </span>
                </div>
              </div>
              
              <div className="mt-2 text-xs text-muted-foreground">
                Last active: {formatRelativeTime(collab.lastActivity)}
              </div>
              
              {collab.connections.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground mb-1">Connected to:</div>
                  <div className="flex flex-wrap gap-1">
                    {collab.connections.slice(0, 3).map((connection, index) => (
                      <Badge key={index} variant="secondary" className="text-xs px-1 py-0">
                        {connection}
                      </Badge>
                    ))}
                    {collab.connections.length > 3 && (
                      <Badge variant="secondary" className="text-xs px-1 py-0">
                        +{collab.connections.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function MessageHistory({ 
  messages, 
  onMessageSelect, 
  maxMessages = 10 
}: { 
  messages: AgentMessage[]
  onMessageSelect?: (messageId: string) => void
  maxMessages?: number 
}) {
  const [showAll, setShowAll] = useState(false)
  const [filterType, setFilterType] = useState<AgentMessage['messageType'] | 'all'>('all')

  const filteredMessages = messages.filter(message => 
    filterType === 'all' || message.messageType === filterType
  )

  const displayMessages = showAll 
    ? filteredMessages 
    : filteredMessages.slice(0, maxMessages)

  const messageTypes: Array<AgentMessage['messageType'] | 'all'> = [
    'all', 'request', 'response', 'notification', 'discovery', 'review'
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="h-4 w-4" />
          Message History
        </CardTitle>
        <div className="flex items-center gap-2 mt-2">
          {messageTypes.map((type) => (
            <Button
              key={type}
              variant={filterType === type ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterType(type)}
              className="text-xs h-7"
            >
              {type === 'all' ? 'All' : type}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {displayMessages.length > 0 ? (
            displayMessages.map((message) => (
              <MessageItem
                key={message.id}
                message={message}
                onClick={() => onMessageSelect?.(message.id)}
              />
            ))
          ) : (
            <div className="text-center py-4 text-sm text-muted-foreground">
              No messages found
            </div>
          )}
          
          {filteredMessages.length > maxMessages && (
            <div className="text-center pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAll(!showAll)}
                className="text-xs"
              >
                {showAll ? (
                  <>
                    <EyeOff className="h-3 w-3 mr-1" />
                    Show Less
                  </>
                ) : (
                  <>
                    <Eye className="h-3 w-3 mr-1" />
                    Show All ({filteredMessages.length - maxMessages} more)
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function AgentCollaborationStats({ collaborations, messages }: {
  collaborations: AgentCollaboration[]
  messages: AgentMessage[]
}) {
  const totalMessages = messages.length
  const uniqueAgents = new Set([
    ...messages.map(m => m.fromAgent),
    ...messages.map(m => m.toAgent)
  ]).size
  
  const messageTypes = messages.reduce((acc, message) => {
    acc[message.messageType] = (acc[message.messageType] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const avgCollaborationScore = collaborations.length > 0
    ? collaborations.reduce((sum, c) => sum + c.collaborationScore, 0) / collaborations.length
    : 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{uniqueAgents}</div>
          <div className="text-sm text-muted-foreground">Active Agents</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{totalMessages}</div>
          <div className="text-sm text-muted-foreground">Total Messages</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">
            {collaborations.reduce((sum, c) => sum + c.activeConversations, 0)}
          </div>
          <div className="text-sm text-muted-foreground">Active Conversations</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-4 text-center">
          <div className="text-2xl font-bold">{Math.round(avgCollaborationScore * 100)}%</div>
          <div className="text-sm text-muted-foreground">Avg Collaboration</div>
        </CardContent>
      </Card>
    </div>
  )
}

export function AgentCollaborationView({ 
  collaborations, 
  messages, 
  onMessageSelect 
}: AgentCollaborationViewProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Users className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Agent Collaboration</h2>
      </div>
      
      <AgentCollaborationStats 
        collaborations={collaborations} 
        messages={messages} 
      />
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <CollaborationNetwork collaborations={collaborations} />
        <MessageHistory 
          messages={messages} 
          onMessageSelect={onMessageSelect}
          maxMessages={8}
        />
      </div>
    </div>
  )
}