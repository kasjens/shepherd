'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Send, Copy, RotateCw, Settings, Package, User, Bot, Folder } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useProjectStore } from '@/stores/project-store'

interface ConversationAreaProps {
  className?: string
}

interface Message {
  id: string
  sender: 'user' | 'ai'
  content: string
  timestamp: Date
  artifacts?: Array<{ id: string; name: string; type: string }>
}

export function ConversationArea({ className }: ConversationAreaProps) {
  const [message, setMessage] = useState('')
  const { projectFolder } = useProjectStore()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'user',
      content: 'Fix performance issues in my server and optimize running services',
      timestamp: new Date(Date.now() - 25 * 60 * 1000),
    },
    {
      id: '2',
      sender: 'ai',
      content: `I'll help you analyze and optimize your server performance. Let me start by examining your system metrics and running services.

🔄 Analyzing system performance...
┌─ CPU Usage: 45%
┌─ Memory: 78% (6.2GB/8GB used)
┌─ Disk: 62% used
└─ Services: 127 running

Based on the analysis, I've identified optimization opportunities. I've created a system analysis script and performance report for you.`,
      timestamp: new Date(Date.now() - 24 * 60 * 1000),
      artifacts: [
        { id: '1', name: 'system_analysis.py', type: 'python' },
        { id: '2', name: 'performance_report.md', type: 'markdown' }
      ]
    },
    {
      id: '3',
      sender: 'user',
      content: 'Can you also check what\'s using the most memory?',
      timestamp: new Date(Date.now() - 20 * 60 * 1000),
    },
    {
      id: '4',
      sender: 'ai',
      content: `Let me analyze the memory usage by process...

🔄 Memory analysis in progress...

Top memory consumers:
┌─ postgres: 1.2GB (15%)
┌─ chrome: 0.8GB (10%)
┌─ java: 0.6GB (7.5%)
└─ [View full analysis in artifact]`,
      timestamp: new Date(Date.now() - 19 * 60 * 1000),
      artifacts: [
        { id: '3', name: 'memory_analysis.json', type: 'json' }
      ]
    }
  ])

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!message.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: message,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, newMessage])
    setMessage('')

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: `I'll help you with that request. Let me analyze and process your requirements...

🔄 Processing your request...

I'm working on implementing your request. This may take a moment while I analyze the requirements and create the necessary components.`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  return (
    <div className={cn("flex-1 flex flex-col overflow-hidden h-full", className)} style={{ backgroundColor: 'var(--background)' }}>
      {/* Header */}
      <div className="p-4 terminal-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--foreground)' }}>Server Performance Analysis</h1>
            <div className="flex items-center gap-3 text-sm" style={{ color: 'var(--muted-gray)' }}>
              <span>Started 25 minutes ago • {messages.length} messages • 3 artifacts generated</span>
              {projectFolder && (
                <>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    <Folder className="h-3 w-3" />
                    <span title={projectFolder}>
                      {projectFolder.split(/[/\\]/).slice(-2).join('/')}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              {msg.sender === 'user' ? (
                <>
                  <User className="h-4 w-4" />
                  <span className="font-medium">You</span>
                </>
              ) : (
                <>
                  <Bot className="h-4 w-4" />
                  <span className="font-medium">Shepherd</span>
                </>
              )}
              <span className="text-muted-gray">• {formatTime(msg.timestamp)}</span>
            </div>
            
            <Card className={cn(
              "p-4 max-w-4xl",
              msg.sender === 'user' ? "message-user ml-6" : "message-ai ml-6"
            )}>
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                {msg.content}
              </pre>
              
              {msg.artifacts && msg.artifacts.length > 0 && (
                <div className="flex gap-2 mt-4">
                  {msg.artifacts.map((artifact) => (
                    <Button
                      key={artifact.id}
                      variant="outline"
                      size="sm"
                      className="h-8"
                    >
                      <Package className="h-3 w-3 mr-1" />
                      {artifact.name}
                    </Button>
                  ))}
                </div>
              )}
            </Card>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line, Enter to send)"
              className="min-h-[60px] max-h-32 resize-none"
            />
          </div>
          <Button
            onClick={handleSend}
            disabled={!message.trim()}
            size="lg"
            className="px-6 shepherd-button-primary"
          >
            <Send className="h-4 w-4 mr-2" />
            Send
          </Button>
        </div>
      </div>
    </div>
  )
}