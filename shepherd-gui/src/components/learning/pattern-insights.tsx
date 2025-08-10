'use client'

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  TrendingUp, 
  Brain, 
  Zap, 
  Target, 
  Clock, 
  Users,
  BarChart3,
  Filter,
  Search,
  ChevronRight,
  ChevronDown,
  Star,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useWebSocket } from '@/hooks/use-websocket'

// Helper functions for pattern icons
const getPatternIcon = (type: string) => {
  switch (type) {
    case 'workflow':
      return Target
    case 'user_behavior':
      return Users
    case 'performance':
      return BarChart3
    case 'error':
      return AlertTriangle
    case 'usage':
      return TrendingUp
    case 'optimization':
      return Zap
    default:
      return Brain
  }
}

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'improving':
      return ArrowUp
    case 'declining':
      return ArrowDown
    case 'stable':
      return Minus
    default:
      return Minus
  }
}

const getImpactColor = (impact: string) => {
  switch (impact) {
    case 'high':
      return 'text-red-600 dark:text-red-400'
    case 'medium':
      return 'text-yellow-600 dark:text-yellow-400'
    case 'low':
      return 'text-green-600 dark:text-green-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
}

export interface Pattern {
  id: string
  type: 'workflow' | 'user_behavior' | 'performance' | 'error' | 'usage' | 'optimization'
  title: string
  description: string
  confidence: number // 0-100
  frequency: number
  impact: 'low' | 'medium' | 'high'
  trend: 'increasing' | 'decreasing' | 'stable'
  detectedAt: Date
  lastSeen: Date
  examples: PatternExample[]
  metrics: PatternMetrics
  recommendations: Recommendation[]
  tags: string[]
  status: 'active' | 'resolved' | 'investigating' | 'archived'
}

export interface PatternExample {
  id: string
  timestamp: Date
  context: string
  data: Record<string, any>
  similarity: number // 0-100
}

export interface PatternMetrics {
  occurrences: number
  avgDuration?: number
  successRate?: number
  errorRate?: number
  usersSatisfied?: number
  performanceImpact?: number
  trendsData: Array<{
    date: Date
    value: number
    metric: string
  }>
}

export interface Recommendation {
  id: string
  type: 'improvement' | 'optimization' | 'fix' | 'investigation'
  title: string
  description: string
  priority: 'low' | 'medium' | 'high'
  effort: 'low' | 'medium' | 'high'
  expectedImpact: string
  implemented?: boolean
  implementedAt?: Date
}

interface PatternInsightsProps {
  patterns?: Pattern[]
  onPatternAction?: (patternId: string, action: 'investigate' | 'resolve' | 'archive') => void
  onRecommendationImplement?: (recommendationId: string) => void
  className?: string
}

export function PatternInsights({ 
  patterns: propPatterns, 
  onPatternAction, 
  onRecommendationImplement, 
  className 
}: PatternInsightsProps) {
  const [patterns, setPatterns] = useState<Pattern[]>(propPatterns || [])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<Pattern['type'] | 'all'>('all')
  const [filterStatus, setFilterStatus] = useState<Pattern['status'] | 'all'>('all')
  const [sortBy, setSortBy] = useState<'confidence' | 'frequency' | 'impact' | 'detected'>('confidence')
  const [expandedPattern, setExpandedPattern] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const patternsPerPage = 10

  const ws = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      if (message.type === 'pattern_update') {
        setPatterns(prev => {
          const updated = prev.map(p => 
            p.id === message.data.id ? { ...p, ...message.data } : p
          )
          if (!prev.find(p => p.id === message.data.id)) {
            updated.push(message.data)
          }
          return updated
        })
      }
    }
  })

  // Load patterns from server
  useEffect(() => {
    if (!propPatterns) {
      loadPatterns()
    }
  }, [propPatterns])

  const loadPatterns = useCallback(async () => {
    setLoading(true)
    try {
      const response = await ws.send('learning:get_patterns', {}, true)
      if (response?.patterns) {
        setPatterns(response.patterns)
      }
    } catch (error) {
      console.error('Failed to load patterns:', error)
    } finally {
      setLoading(false)
    }
  }, [ws])

  // Filter and sort patterns
  const filteredPatterns = useMemo(() => {
    return patterns
      .filter(pattern => {
        // Search filter
        if (searchQuery) {
          const query = searchQuery.toLowerCase()
          if (!pattern.title.toLowerCase().includes(query) &&
              !pattern.description.toLowerCase().includes(query) &&
              !pattern.tags.some(tag => tag.toLowerCase().includes(query))) {
            return false
          }
        }
        
        // Type filter
        if (filterType !== 'all' && pattern.type !== filterType) {
          return false
        }
        
        // Status filter
        if (filterStatus !== 'all' && pattern.status !== filterStatus) {
          return false
        }
        
        return true
      })
      .sort((a, b) => {
        switch (sortBy) {
          case 'confidence':
            return b.confidence - a.confidence
          case 'frequency':
            return b.frequency - a.frequency
          case 'impact':
            const impactOrder = { high: 3, medium: 2, low: 1 }
            return impactOrder[b.impact] - impactOrder[a.impact]
          case 'detected':
            return new Date(b.detectedAt).getTime() - new Date(a.detectedAt).getTime()
          default:
            return 0
        }
      })
  }, [patterns, searchQuery, filterType, filterStatus, sortBy])

  // Pagination
  const totalPages = Math.ceil(filteredPatterns.length / patternsPerPage)
  const paginatedPatterns = filteredPatterns.slice(
    (currentPage - 1) * patternsPerPage,
    currentPage * patternsPerPage
  )

  const handlePatternAction = useCallback((patternId: string, action: 'investigate' | 'resolve' | 'archive') => {
    setPatterns(prev => prev.map(p => 
      p.id === patternId 
        ? { ...p, status: action === 'investigate' ? 'investigating' : action === 'resolve' ? 'resolved' : 'archived' }
        : p
    ))
    onPatternAction?.(patternId, action)
  }, [onPatternAction])

  const handleRecommendationImplement = useCallback((recommendationId: string) => {
    setPatterns(prev => prev.map(pattern => ({
      ...pattern,
      recommendations: pattern.recommendations.map(rec =>
        rec.id === recommendationId
          ? { ...rec, implemented: true, implementedAt: new Date() }
          : rec
      )
    })))
    onRecommendationImplement?.(recommendationId)
  }, [onRecommendationImplement])

  const getPatternIcon = (type: Pattern['type']) => {
    switch (type) {
      case 'workflow': return Zap
      case 'user_behavior': return Users
      case 'performance': return TrendingUp
      case 'error': return AlertTriangle
      case 'usage': return BarChart3
      case 'optimization': return Target
      default: return Brain
    }
  }

  const getImpactColor = (impact: Pattern['impact']) => {
    switch (impact) {
      case 'high': return 'text-red-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-green-500'
    }
  }

  const getTrendIcon = (trend: Pattern['trend']) => {
    switch (trend) {
      case 'increasing': return ArrowUp
      case 'decreasing': return ArrowDown
      case 'stable': return Minus
    }
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-purple-500" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Pattern Insights
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              AI-discovered patterns and optimization opportunities
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="text-sm text-gray-500">
            {filteredPatterns.length} patterns found
          </div>
          <button
            onClick={loadPatterns}
            disabled={loading}
            className={cn(
              'px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md',
              'hover:bg-gray-50 dark:hover:bg-gray-700',
              loading && 'opacity-50 cursor-not-allowed'
            )}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-64">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search patterns..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>
        </div>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as Pattern['type'] | 'all')}
          className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
        >
          <option value="all">All Types</option>
          <option value="workflow">Workflow</option>
          <option value="user_behavior">User Behavior</option>
          <option value="performance">Performance</option>
          <option value="error">Errors</option>
          <option value="usage">Usage</option>
          <option value="optimization">Optimization</option>
        </select>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as Pattern['status'] | 'all')}
          className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="archived">Archived</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
        >
          <option value="confidence">Confidence</option>
          <option value="frequency">Frequency</option>
          <option value="impact">Impact</option>
          <option value="detected">Date Detected</option>
        </select>
      </div>

      {/* Pattern List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
          </div>
        ) : paginatedPatterns.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <div className="text-lg font-medium mb-2">No Patterns Found</div>
            <div className="text-sm">
              {patterns.length === 0 
                ? "No patterns have been discovered yet. Keep using the system to generate insights."
                : "Try adjusting your filters to see more patterns."
              }
            </div>
          </div>
        ) : (
          paginatedPatterns.map((pattern) => (
            <PatternCard
              key={pattern.id}
              pattern={pattern}
              isExpanded={expandedPattern === pattern.id}
              onToggleExpand={() => setExpandedPattern(
                expandedPattern === pattern.id ? null : pattern.id
              )}
              onAction={handlePatternAction}
              onRecommendationImplement={handleRecommendationImplement}
            />
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Showing {(currentPage - 1) * patternsPerPage + 1} to{' '}
            {Math.min(currentPage * patternsPerPage, filteredPatterns.length)} of{' '}
            {filteredPatterns.length} patterns
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50"
            >
              Previous
            </button>
            
            <span className="px-3 py-1 text-sm">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Individual Pattern Card Component
interface PatternCardProps {
  pattern: Pattern
  isExpanded: boolean
  onToggleExpand: () => void
  onAction: (patternId: string, action: 'investigate' | 'resolve' | 'archive') => void
  onRecommendationImplement: (recommendationId: string) => void
}

function PatternCard({
  pattern,
  isExpanded,
  onToggleExpand,
  onAction,
  onRecommendationImplement
}: PatternCardProps) {
  const PatternIcon = getPatternIcon(pattern.type)
  const TrendIcon = getTrendIcon(pattern.trend)
  
  return (
    <div className="border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 shadow-sm">
      {/* Header */}
      <div 
        onClick={onToggleExpand}
        className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <PatternIcon className="w-5 h-5 mt-1 text-purple-500" />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium text-gray-900 dark:text-gray-100">
                  {pattern.title}
                </h3>
                <div className="flex items-center gap-1">
                  <TrendIcon className={cn('w-4 h-4', {
                    'text-red-500': pattern.trend === 'increasing' && pattern.impact === 'high',
                    'text-green-500': pattern.trend === 'decreasing' && pattern.impact === 'high',
                    'text-gray-500': pattern.trend === 'stable'
                  })} />
                  <span className={cn('text-xs px-2 py-1 rounded-full', {
                    'bg-green-100 text-green-700': pattern.status === 'resolved',
                    'bg-yellow-100 text-yellow-700': pattern.status === 'investigating',
                    'bg-red-100 text-red-700': pattern.status === 'active',
                    'bg-gray-100 text-gray-700': pattern.status === 'archived'
                  })}>
                    {pattern.status}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {pattern.description}
              </p>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Confidence: {pattern.confidence}%</span>
                <span>Frequency: {pattern.frequency}</span>
                <span className={getImpactColor(pattern.impact)}>
                  Impact: {pattern.impact}
                </span>
                <span>Detected: {new Date(pattern.detectedAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex">
              {pattern.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full mr-1"
                >
                  {tag}
                </span>
              ))}
              {pattern.tags.length > 3 && (
                <span className="text-xs text-gray-400">+{pattern.tags.length - 3}</span>
              )}
            </div>
            <ChevronRight className={cn('w-4 h-4 text-gray-400 transition-transform', {
              'rotate-90': isExpanded
            })} />
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-600">
          <div className="p-4 space-y-4">
            {/* Metrics */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                Metrics
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <div className="text-2xl font-bold text-purple-600">
                    {pattern.metrics.occurrences}
                  </div>
                  <div className="text-xs text-gray-500">Occurrences</div>
                </div>
                {pattern.metrics.successRate !== undefined && (
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <div className="text-2xl font-bold text-green-600">
                      {pattern.metrics.successRate}%
                    </div>
                    <div className="text-xs text-gray-500">Success Rate</div>
                  </div>
                )}
                {pattern.metrics.avgDuration !== undefined && (
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <div className="text-2xl font-bold text-blue-600">
                      {pattern.metrics.avgDuration}ms
                    </div>
                    <div className="text-xs text-gray-500">Avg Duration</div>
                  </div>
                )}
                {pattern.metrics.errorRate !== undefined && (
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <div className="text-2xl font-bold text-red-600">
                      {pattern.metrics.errorRate}%
                    </div>
                    <div className="text-xs text-gray-500">Error Rate</div>
                  </div>
                )}
              </div>
            </div>

            {/* Examples */}
            {pattern.examples.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Recent Examples
                </h4>
                <div className="space-y-2">
                  {pattern.examples.slice(0, 3).map((example) => (
                    <div key={example.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{example.context}</span>
                        <span className="text-gray-500">
                          {example.similarity}% similarity
                        </span>
                      </div>
                      <div className="text-gray-600 dark:text-gray-400 text-xs">
                        {new Date(example.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {pattern.recommendations.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Recommendations
                </h4>
                <div className="space-y-3">
                  {pattern.recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      className={cn(
                        'p-3 border rounded-lg',
                        rec.implemented
                          ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900'
                          : 'border-gray-200 dark:border-gray-600'
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-sm">{rec.title}</span>
                            {rec.implemented && (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            )}
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {rec.description}
                          </p>
                          <div className="flex items-center gap-4 text-xs">
                            <span className={cn('px-2 py-1 rounded', {
                              'bg-red-100 text-red-700': rec.priority === 'high',
                              'bg-yellow-100 text-yellow-700': rec.priority === 'medium',
                              'bg-green-100 text-green-700': rec.priority === 'low'
                            })}>
                              {rec.priority} priority
                            </span>
                            <span className="text-gray-500">
                              {rec.effort} effort
                            </span>
                            <span className="text-gray-500">
                              Impact: {rec.expectedImpact}
                            </span>
                          </div>
                        </div>
                        
                        {!rec.implemented && (
                          <button
                            onClick={() => onRecommendationImplement(rec.id)}
                            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                          >
                            Implement
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-2 border-t border-gray-200 dark:border-gray-600">
              {pattern.status === 'active' && (
                <>
                  <button
                    onClick={() => onAction(pattern.id, 'investigate')}
                    className="px-3 py-1 text-sm border border-yellow-300 text-yellow-700 rounded hover:bg-yellow-50"
                  >
                    Investigate
                  </button>
                  <button
                    onClick={() => onAction(pattern.id, 'resolve')}
                    className="px-3 py-1 text-sm border border-green-300 text-green-700 rounded hover:bg-green-50"
                  >
                    Mark Resolved
                  </button>
                </>
              )}
              {pattern.status === 'investigating' && (
                <button
                  onClick={() => onAction(pattern.id, 'resolve')}
                  className="px-3 py-1 text-sm border border-green-300 text-green-700 rounded hover:bg-green-50"
                >
                  Mark Resolved
                </button>
              )}
              <button
                onClick={() => onAction(pattern.id, 'archive')}
                className="px-3 py-1 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
              >
                Archive
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}