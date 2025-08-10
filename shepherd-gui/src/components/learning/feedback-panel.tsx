'use client'

import React, { useState, useCallback, useRef } from 'react'
import { 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Star, 
  Send, 
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Target,
  TrendingUp,
  Clock
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useWebSocket } from '@/hooks/use-websocket'

export type FeedbackType = 'positive' | 'negative' | 'suggestion' | 'bug' | 'feature' | 'question'
export type FeedbackPriority = 'low' | 'medium' | 'high'

export interface FeedbackData {
  id?: string
  type: FeedbackType
  priority: FeedbackPriority
  title: string
  description: string
  context?: {
    page?: string
    feature?: string
    workflowId?: string
    agentId?: string
    timestamp?: Date
  }
  rating?: number // 1-5 stars
  tags?: string[]
  attachments?: File[]
  userId?: string
  userEmail?: string
  status?: 'submitted' | 'processing' | 'acknowledged' | 'resolved'
  createdAt?: Date
}

interface FeedbackPanelProps {
  isOpen: boolean
  onClose: () => void
  initialContext?: Partial<FeedbackData['context']>
  onSubmit?: (feedback: FeedbackData) => Promise<void>
  className?: string
}

export function FeedbackPanel({ 
  isOpen, 
  onClose, 
  initialContext,
  onSubmit,
  className 
}: FeedbackPanelProps) {
  const [feedbackData, setFeedbackData] = useState<Partial<FeedbackData>>({
    type: 'suggestion',
    priority: 'medium',
    title: '',
    description: '',
    context: initialContext,
    rating: 0,
    tags: []
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [files, setFiles] = useState<File[]>([])
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const descriptionRef = useRef<HTMLTextAreaElement>(null)
  
  const ws = useWebSocket({
    autoConnect: true
  })

  // Debounced auto-save
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const handleAutoSave = useCallback(() => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current)
    }
    
    autoSaveTimeoutRef.current = setTimeout(() => {
      // Save to localStorage as draft
      localStorage.setItem('feedback-draft', JSON.stringify(feedbackData))
    }, 1000)
  }, [feedbackData])

  // Load draft on mount
  React.useEffect(() => {
    const draft = localStorage.getItem('feedback-draft')
    if (draft && isOpen) {
      try {
        const parsedDraft = JSON.parse(draft)
        if (parsedDraft.title || parsedDraft.description) {
          setFeedbackData(prev => ({ ...prev, ...parsedDraft }))
        }
      } catch (error) {
        console.warn('Failed to load feedback draft:', error)
      }
    }
  }, [isOpen])

  React.useEffect(() => {
    if (feedbackData.title || feedbackData.description) {
      handleAutoSave()
    }
  }, [feedbackData, handleAutoSave])

  const updateFeedback = useCallback((updates: Partial<FeedbackData>) => {
    setFeedbackData(prev => ({ ...prev, ...updates }))
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!feedbackData.title?.trim() || !feedbackData.description?.trim()) {
      return
    }

    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      const finalFeedback: FeedbackData = {
        ...feedbackData,
        id: `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        attachments: files,
        createdAt: new Date(),
        status: 'submitted'
      } as FeedbackData

      if (onSubmit) {
        await onSubmit(finalFeedback)
      } else {
        // Send via WebSocket
        await ws.send('learning:feedback', finalFeedback)
      }

      setSubmitStatus('success')
      localStorage.removeItem('feedback-draft')
      
      // Reset form after success
      setTimeout(() => {
        setFeedbackData({
          type: 'suggestion',
          priority: 'medium',
          title: '',
          description: '',
          context: initialContext,
          rating: 0,
          tags: []
        })
        setFiles([])
        onClose()
      }, 2000)

    } catch (error) {
      console.error('Failed to submit feedback:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }, [feedbackData, files, onSubmit, ws, onClose, initialContext])

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = Array.from(e.target.files || [])
    const maxSize = 5 * 1024 * 1024 // 5MB
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'text/plain', 'application/pdf']
    
    const validFiles = uploadedFiles.filter(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 5MB.`)
        return false
      }
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} has unsupported type.`)
        return false
      }
      return true
    })
    
    setFiles(prev => [...prev, ...validFiles].slice(0, 3)) // Max 3 files
  }, [])

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const addTag = useCallback((tag: string) => {
    if (tag && !feedbackData.tags?.includes(tag)) {
      updateFeedback({
        tags: [...(feedbackData.tags || []), tag]
      })
    }
  }, [feedbackData.tags, updateFeedback])

  const removeTag = useCallback((tag: string) => {
    updateFeedback({
      tags: feedbackData.tags?.filter(t => t !== tag) || []
    })
  }, [feedbackData.tags, updateFeedback])

  const feedbackTypes = [
    { value: 'positive', label: 'Positive', icon: ThumbsUp, color: 'text-green-600' },
    { value: 'negative', label: 'Negative', icon: ThumbsDown, color: 'text-red-600' },
    { value: 'suggestion', label: 'Suggestion', icon: Lightbulb, color: 'text-yellow-600' },
    { value: 'bug', label: 'Bug Report', icon: AlertCircle, color: 'text-red-600' },
    { value: 'feature', label: 'Feature Request', icon: Target, color: 'text-blue-600' },
    { value: 'question', label: 'Question', icon: MessageSquare, color: 'text-gray-600' }
  ]

  const suggestedTags = [
    'UI/UX', 'Performance', 'Analytics', 'Workflow', 'Agent', 'Export', 'Collaboration', 
    'Real-time', 'Dashboard', 'Charts', 'Mobile', 'Accessibility'
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className={cn(
        'bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden',
        className
      )}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Share Your Feedback
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Help us improve Shepherd with your insights
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            disabled={isSubmitting}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Feedback Type */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Feedback Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              {feedbackTypes.map(({ value, label, icon: Icon, color }) => (
                <button
                  key={value}
                  onClick={() => updateFeedback({ type: value as FeedbackType })}
                  className={cn(
                    'flex items-center gap-2 p-3 border rounded-lg text-left',
                    feedbackData.type === value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                      : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  )}
                >
                  <Icon className={cn('w-4 h-4', color)} />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Priority */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Priority
            </label>
            <select
              value={feedbackData.priority}
              onChange={(e) => updateFeedback({ priority: e.target.value as FeedbackPriority })}
              className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
            >
              <option value="low">Low - Nice to have</option>
              <option value="medium">Medium - Should be addressed</option>
              <option value="high">High - Needs immediate attention</option>
            </select>
          </div>

          {/* Rating (for positive/negative feedback) */}
          {(feedbackData.type === 'positive' || feedbackData.type === 'negative') && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rating
              </label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    onClick={() => updateFeedback({ rating })}
                    className="p-1"
                  >
                    <Star
                      className={cn(
                        'w-6 h-6',
                        rating <= (feedbackData.rating || 0)
                          ? 'text-yellow-500 fill-current'
                          : 'text-gray-300'
                      )}
                    />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Title */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Title *
            </label>
            <input
              type="text"
              value={feedbackData.title || ''}
              onChange={(e) => updateFeedback({ title: e.target.value })}
              placeholder="Brief summary of your feedback"
              className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isSubmitting}
            />
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description *
            </label>
            <textarea
              ref={descriptionRef}
              value={feedbackData.description || ''}
              onChange={(e) => updateFeedback({ description: e.target.value })}
              placeholder="Please provide detailed feedback. Include steps to reproduce for bugs, specific use cases for features, etc."
              rows={6}
              className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 resize-none"
              disabled={isSubmitting}
            />
            <div className="text-xs text-gray-500 mt-1">
              {feedbackData.description?.length || 0} characters
            </div>
          </div>

          {/* Tags */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {feedbackData.tags?.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded-full"
                >
                  {tag}
                  <button
                    onClick={() => removeTag(tag)}
                    className="ml-1 hover:text-blue-900 dark:hover:text-blue-100"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex flex-wrap gap-1">
              {suggestedTags
                .filter(tag => !feedbackData.tags?.includes(tag))
                .map((tag) => (
                  <button
                    key={tag}
                    onClick={() => addTag(tag)}
                    className="px-2 py-1 text-xs border border-gray-200 dark:border-gray-600 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    +{tag}
                  </button>
                ))}
            </div>
          </div>

          {/* File Attachments */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Attachments (Optional)
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500"
            >
              <div className="text-sm text-gray-500">
                Click to upload images or documents (max 3 files, 5MB each)
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.gif,.txt,.pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {files.length > 0 && (
              <div className="mt-2 space-y-1">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className="text-sm truncate">{file.name}</span>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Context Info */}
          {initialContext && (
            <div className="mb-6 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Context Information
              </div>
              <div className="text-xs text-gray-500 space-y-1">
                {initialContext.page && <div>Page: {initialContext.page}</div>}
                {initialContext.feature && <div>Feature: {initialContext.feature}</div>}
                {initialContext.workflowId && <div>Workflow: {initialContext.workflowId}</div>}
                {initialContext.agentId && <div>Agent: {initialContext.agentId}</div>}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {submitStatus === 'success' && (
              <>
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Feedback submitted successfully!</span>
              </>
            )}
            {submitStatus === 'error' && (
              <>
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span>Failed to submit feedback. Please try again.</span>
              </>
            )}
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || !feedbackData.title?.trim() || !feedbackData.description?.trim()}
              className={cn(
                'flex items-center gap-2 px-6 py-2 rounded-lg font-medium',
                isSubmitting || !feedbackData.title?.trim() || !feedbackData.description?.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              )}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Submit Feedback
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Quick Feedback Component for contextual feedback
interface QuickFeedbackProps {
  context?: Partial<FeedbackData['context']>
  onSubmit?: (feedback: FeedbackData) => Promise<void>
  className?: string
}

export function QuickFeedback({ context, onSubmit, className }: QuickFeedbackProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [rating, setRating] = useState(0)
  const [submitted, setSubmitted] = useState(false)

  const submitQuickRating = useCallback(async (selectedRating: number) => {
    try {
      const feedback: FeedbackData = {
        id: `quick_${Date.now()}`,
        type: selectedRating >= 4 ? 'positive' : 'negative',
        priority: 'low',
        title: `Quick Rating: ${selectedRating}/5`,
        description: `User provided a ${selectedRating}-star rating`,
        context,
        rating: selectedRating,
        createdAt: new Date(),
        status: 'submitted'
      }

      if (onSubmit) {
        await onSubmit(feedback)
      }

      setRating(selectedRating)
      setSubmitted(true)
    } catch (error) {
      console.error('Failed to submit quick feedback:', error)
    }
  }, [context, onSubmit])

  if (submitted) {
    return (
      <div className={cn('flex items-center gap-2 text-sm text-green-600', className)}>
        <CheckCircle className="w-4 h-4" />
        <span>Thanks for your feedback!</span>
      </div>
    )
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="text-sm text-gray-600 dark:text-gray-400">Rate this:</span>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => submitQuickRating(star)}
            className="p-1 hover:scale-110 transition-transform"
          >
            <Star
              className={cn(
                'w-4 h-4',
                star <= rating
                  ? 'text-yellow-500 fill-current'
                  : 'text-gray-300 hover:text-yellow-400'
              )}
            />
          </button>
        ))}
      </div>
      <button
        onClick={() => setIsOpen(true)}
        className="text-sm text-blue-500 hover:text-blue-700 ml-2"
      >
        More feedback
      </button>
      
      <FeedbackPanel
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialContext={context}
        onSubmit={onSubmit}
      />
    </div>
  )
}