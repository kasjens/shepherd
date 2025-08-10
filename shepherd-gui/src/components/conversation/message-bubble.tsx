'use client'

import React, { memo, useState, useCallback, useMemo } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { Copy, Check, User, Bot, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface MessageBubbleProps {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date
  isLoading?: boolean
  artifacts?: Array<{
    id: string
    type: 'code' | 'text' | 'image'
    title: string
    content: string
    language?: string
  }>
  onCopy?: (content: string) => void
  onArtifactClick?: (artifactId: string) => void
  className?: string
}

const MessageBubble = memo<MessageBubbleProps>(({
  id,
  content,
  role,
  timestamp,
  isLoading = false,
  artifacts = [],
  onCopy,
  onArtifactClick,
  className
}) => {
  const { theme, reducedMotion } = useUIStore(state => ({
    theme: state.theme,
    reducedMotion: state.reducedMotion
  }))

  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({})

  const handleCopy = useCallback(async (text: string, key: string = 'main') => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedStates(prev => ({ ...prev, [key]: true }))
      onCopy?.(text)
      
      // Reset copy state after 2 seconds
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [key]: false }))
      }, 2000)
    } catch (error) {
      console.error('Failed to copy text:', error)
    }
  }, [onCopy])

  const syntaxTheme = useMemo(() => 
    theme === 'dark' ? oneDark : oneLight
  , [theme])

  const parseContent = useMemo(() => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
    const inlineCodeRegex = /`([^`]+)`/g
    const parts: Array<{ type: 'text' | 'code' | 'inline-code', content: string, language?: string }> = []
    
    let lastIndex = 0
    let match

    // Find code blocks
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        const textContent = content.slice(lastIndex, match.index)
        if (textContent.trim()) {
          parts.push({ type: 'text', content: textContent })
        }
      }
      
      // Add code block
      parts.push({
        type: 'code',
        content: match[2].trim(),
        language: match[1] || 'text'
      })
      
      lastIndex = match.index + match[0].length
    }

    // Add remaining text
    if (lastIndex < content.length) {
      const remainingText = content.slice(lastIndex)
      if (remainingText.trim()) {
        parts.push({ type: 'text', content: remainingText })
      }
    }

    // If no code blocks found, treat as single text part
    if (parts.length === 0) {
      parts.push({ type: 'text', content })
    }

    return parts
  }, [content])

  const roleConfig = useMemo(() => ({
    user: {
      icon: User,
      label: 'You',
      bgColor: 'bg-blue-500',
      textColor: 'text-white',
      bubbleAlign: 'ml-auto',
      bubbleBg: 'bg-blue-50 dark:bg-blue-950',
      borderColor: 'border-blue-200 dark:border-blue-800'
    },
    assistant: {
      icon: Bot,
      label: 'Assistant',
      bgColor: 'bg-green-500',
      textColor: 'text-white',
      bubbleAlign: 'mr-auto',
      bubbleBg: 'bg-green-50 dark:bg-green-950',
      borderColor: 'border-green-200 dark:border-green-800'
    },
    system: {
      icon: Settings,
      label: 'System',
      bgColor: 'bg-gray-500',
      textColor: 'text-white',
      bubbleAlign: 'mx-auto',
      bubbleBg: 'bg-gray-50 dark:bg-gray-950',
      borderColor: 'border-gray-200 dark:border-gray-800'
    }
  }), [])

  const config = roleConfig[role]
  const IconComponent = config.icon

  return (
    <div className={cn(
      'group flex flex-col gap-2 max-w-4xl',
      config.bubbleAlign,
      className
    )}>
      {/* Message Header */}
      <div className="flex items-center gap-2">
        <div className={cn(
          'w-6 h-6 rounded-full flex items-center justify-center',
          config.bgColor
        )}>
          <IconComponent className={cn('w-3 h-3', config.textColor)} />
        </div>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {config.label}
        </span>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {timestamp.toLocaleTimeString()}
        </span>
      </div>

      {/* Message Content */}
      <div className={cn(
        'relative rounded-lg border p-4',
        config.bubbleBg,
        config.borderColor,
        !reducedMotion && 'transition-all duration-200',
        'group-hover:shadow-md'
      )}>
        {/* Copy Button */}
        <button
          onClick={() => handleCopy(content)}
          className={cn(
            'absolute top-2 right-2 p-1.5 rounded-md',
            'bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm',
            'border border-gray-200 dark:border-gray-700',
            'opacity-0 group-hover:opacity-100',
            !reducedMotion && 'transition-opacity duration-200',
            'hover:bg-white dark:hover:bg-gray-800'
          )}
        >
          {copiedStates.main ? (
            <Check className="w-3 h-3 text-green-500" />
          ) : (
            <Copy className="w-3 h-3 text-gray-500" />
          )}
        </button>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        {/* Content */}
        {!isLoading && (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {parseContent.map((part, index) => (
              <div key={index}>
                {part.type === 'text' && (
                  <div className="whitespace-pre-wrap break-words">
                    {part.content}
                  </div>
                )}
                
                {part.type === 'code' && (
                  <div className="relative group/code">
                    <button
                      onClick={() => handleCopy(part.content, `code-${index}`)}
                      className={cn(
                        'absolute top-2 right-2 p-1 rounded',
                        'bg-black/10 dark:bg-white/10 backdrop-blur-sm',
                        'opacity-0 group-hover/code:opacity-100',
                        !reducedMotion && 'transition-opacity duration-200'
                      )}
                    >
                      {copiedStates[`code-${index}`] ? (
                        <Check className="w-3 h-3 text-green-400" />
                      ) : (
                        <Copy className="w-3 h-3 text-gray-400" />
                      )}
                    </button>
                    
                    <SyntaxHighlighter
                      language={part.language}
                      style={syntaxTheme}
                      customStyle={{
                        margin: 0,
                        borderRadius: '0.375rem',
                        fontSize: '0.875rem'
                      }}
                      showLineNumbers={part.content.split('\n').length > 3}
                    >
                      {part.content}
                    </SyntaxHighlighter>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Artifacts */}
        {artifacts.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {artifacts.map((artifact) => (
              <button
                key={artifact.id}
                onClick={() => onArtifactClick?.(artifact.id)}
                className={cn(
                  'px-3 py-2 rounded-md text-sm',
                  'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
                  'border border-blue-200 dark:border-blue-700',
                  'hover:bg-blue-200 dark:hover:bg-blue-800',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                {artifact.title}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
})

MessageBubble.displayName = 'MessageBubble'

export default MessageBubble