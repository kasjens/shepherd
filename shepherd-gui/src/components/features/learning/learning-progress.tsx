'use client'

import React, { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  BarChart3,
  Lightbulb,
  Zap,
  Book,
  Users,
  Settings
} from 'lucide-react'

interface LearningInsight {
  id: string
  agentId: string
  agentName: string
  type: 'feedback' | 'pattern' | 'adaptation' | 'performance'
  category: 'success' | 'improvement' | 'concern' | 'neutral'
  title: string
  description: string
  confidence: number
  timestamp: number
  metrics?: {
    before: number
    after: number
    improvement: number
  }
  recommendations?: string[]
}

interface FeedbackSummary {
  totalFeedback: number
  feedbackByType: Record<string, number>
  averageRating: number
  recentTrend: 'improving' | 'declining' | 'stable'
  topIssues: Array<{
    issue: string
    count: number
    severity: 'low' | 'medium' | 'high'
  }>
}

interface PatternLearning {
  totalPatternsLearned: number
  failurePatternsIdentified: number
  activePatternsCached: number
  averagePatternScore: number
  learningBufferSize: number
  recentPatterns: Array<{
    id: string
    type: string
    confidence: number
    usageCount: number
    performance: number
  }>
}

interface AdaptationStats {
  enabledTypes: string[]
  cacheSize: number
  performanceTracking: Record<string, {
    averageScore: number
    usageCount: number
    trend: 'improving' | 'declining' | 'stable'
  }>
  knowledgeBase: {
    preferences: number
    learnedPatterns: number
    failurePatterns: number
  }
}

interface LearningProgressProps {
  agentId?: string
  insights: LearningInsight[]
  feedbackSummary: FeedbackSummary
  patternLearning: PatternLearning
  adaptationStats: AdaptationStats
}

function getInsightIcon(type: LearningInsight['type'], category: LearningInsight['category']) {
  if (category === 'success') return <CheckCircle className="h-4 w-4 text-green-600" />
  if (category === 'concern') return <AlertTriangle className="h-4 w-4 text-red-600" />
  if (category === 'improvement') return <TrendingUp className="h-4 w-4 text-blue-600" />
  
  switch (type) {
    case 'feedback':
      return <Star className="h-4 w-4" />
    case 'pattern':
      return <Brain className="h-4 w-4" />
    case 'adaptation':
      return <Zap className="h-4 w-4" />
    case 'performance':
      return <BarChart3 className="h-4 w-4" />
    default:
      return <Lightbulb className="h-4 w-4" />
  }
}

function getTrendIcon(trend: 'improving' | 'declining' | 'stable') {
  switch (trend) {
    case 'improving':
      return <TrendingUp className="h-4 w-4 text-green-600" />
    case 'declining':
      return <TrendingDown className="h-4 w-4 text-red-600" />
    case 'stable':
    default:
      return <Minus className="h-4 w-4 text-gray-600" />
  }
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return 'Just now'
}

export function LearningInsightCard({ insight }: { insight: LearningInsight }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            {getInsightIcon(insight.type, insight.category)}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-medium line-clamp-1">{insight.title}</h4>
              <Badge variant="outline" className="text-xs ml-auto">
                {Math.round(insight.confidence * 100)}%
              </Badge>
            </div>
            
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
              {insight.description}
            </p>
            
            {insight.metrics && (
              <div className="bg-muted rounded p-2 mb-2">
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <div className="text-muted-foreground">Before</div>
                    <div className="font-medium">{insight.metrics.before.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">After</div>
                    <div className="font-medium">{insight.metrics.after.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Change</div>
                    <div className={`font-medium ${
                      insight.metrics.improvement > 0 ? 'text-green-600' : 
                      insight.metrics.improvement < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {insight.metrics.improvement > 0 ? '+' : ''}{insight.metrics.improvement.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{insight.agentName}</span>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatRelativeTime(insight.timestamp)}</span>
              </div>
            </div>
            
            {insight.recommendations && insight.recommendations.length > 0 && (
              <div className="mt-2 pt-2 border-t border-border">
                <div className="text-xs font-medium text-muted-foreground mb-1">Recommendations:</div>
                <ul className="text-xs space-y-1">
                  {insight.recommendations.slice(0, 2).map((rec, index) => (
                    <li key={index} className="flex items-start gap-1">
                      <span className="text-muted-foreground">•</span>
                      <span className="line-clamp-1">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function FeedbackSummaryPanel({ summary }: { summary: FeedbackSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-4 w-4" />
          Feedback Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-2xl font-bold">{summary.totalFeedback}</div>
            <div className="text-sm text-muted-foreground">Total Feedback</div>
          </div>
          <div>
            <div className="flex items-center gap-1">
              <div className="text-2xl font-bold">{summary.averageRating.toFixed(1)}</div>
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            </div>
            <div className="text-sm text-muted-foreground">Average Rating</div>
          </div>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium">Recent Trend</span>
            {getTrendIcon(summary.recentTrend)}
            <Badge variant={
              summary.recentTrend === 'improving' ? 'default' :
              summary.recentTrend === 'declining' ? 'destructive' : 'secondary'
            } className="text-xs">
              {summary.recentTrend}
            </Badge>
          </div>
        </div>
        
        <div>
          <div className="text-sm font-medium mb-2">Feedback by Type</div>
          <div className="space-y-2">
            {Object.entries(summary.feedbackByType).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary rounded-full h-2 transition-all"
                      style={{ width: `${(count / summary.totalFeedback) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-6 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {summary.topIssues.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Top Issues</div>
            <div className="space-y-1">
              {summary.topIssues.slice(0, 3).map((issue, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="line-clamp-1">{issue.issue}</span>
                  <div className="flex items-center gap-1">
                    <Badge 
                      variant={
                        issue.severity === 'high' ? 'destructive' :
                        issue.severity === 'medium' ? 'default' : 'secondary'
                      }
                      className="text-xs"
                    >
                      {issue.severity}
                    </Badge>
                    <span className="text-xs text-muted-foreground">×{issue.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function PatternLearningPanel({ learning }: { learning: PatternLearning }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Pattern Learning
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-2xl font-bold">{learning.totalPatternsLearned}</div>
            <div className="text-sm text-muted-foreground">Patterns Learned</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{learning.failurePatternsIdentified}</div>
            <div className="text-sm text-muted-foreground">Failures Identified</div>
          </div>
        </div>
        
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Pattern Score</span>
            <span className="text-sm font-bold">
              {Math.round(learning.averagePatternScore * 100)}%
            </span>
          </div>
          <Progress value={learning.averagePatternScore * 100} className="h-2" />
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Cached Patterns</div>
            <div className="font-medium">{learning.activePatternsCached}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Learning Buffer</div>
            <div className="font-medium">{learning.learningBufferSize}</div>
          </div>
        </div>
        
        {learning.recentPatterns.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Recent Patterns</div>
            <div className="space-y-2">
              {learning.recentPatterns.slice(0, 3).map((pattern, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                  <div>
                    <div className="text-sm font-medium">{pattern.type}</div>
                    <div className="text-xs text-muted-foreground">
                      Used {pattern.usageCount} times
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {Math.round(pattern.confidence * 100)}%
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {pattern.performance.toFixed(1)}s avg
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function AdaptationStatsPanel({ stats }: { stats: AdaptationStats }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Adaptive Behavior
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="text-sm font-medium mb-2">Enabled Adaptation Types</div>
          <div className="flex flex-wrap gap-1">
            {stats.enabledTypes.map((type, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {type.replace('_', ' ')}
              </Badge>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-lg font-bold">{stats.knowledgeBase.preferences}</div>
            <div className="text-xs text-muted-foreground">Preferences</div>
          </div>
          <div>
            <div className="text-lg font-bold">{stats.knowledgeBase.learnedPatterns}</div>
            <div className="text-xs text-muted-foreground">Patterns</div>
          </div>
          <div>
            <div className="text-lg font-bold">{stats.cacheSize}</div>
            <div className="text-xs text-muted-foreground">Cache Size</div>
          </div>
        </div>
        
        {Object.keys(stats.performanceTracking).length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Performance Tracking</div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {Object.entries(stats.performanceTracking).slice(0, 5).map(([name, perf]) => (
                <div key={name} className="flex items-center justify-between p-2 bg-muted rounded">
                  <div>
                    <div className="text-sm font-medium line-clamp-1">{name}</div>
                    <div className="text-xs text-muted-foreground">
                      Used {perf.usageCount} times
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getTrendIcon(perf.trend)}
                    <span className="text-sm font-medium">
                      {Math.round(perf.averageScore * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function LearningProgressOverview({ 
  insights, 
  feedbackSummary, 
  patternLearning, 
  adaptationStats 
}: LearningProgressProps) {
  const [selectedInsightType, setSelectedInsightType] = useState<LearningInsight['type'] | 'all'>('all')
  
  const filteredInsights = insights.filter(insight => 
    selectedInsightType === 'all' || insight.type === selectedInsightType
  )

  const insightTypes: Array<LearningInsight['type'] | 'all'> = [
    'all', 'feedback', 'pattern', 'adaptation', 'performance'
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Brain className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Learning Progress</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <FeedbackSummaryPanel summary={feedbackSummary} />
        <PatternLearningPanel learning={patternLearning} />
        <AdaptationStatsPanel stats={adaptationStats} />
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Learning Insights
          </CardTitle>
          <div className="flex items-center gap-2 mt-2">
            {insightTypes.map((type) => (
              <Button
                key={type}
                variant={selectedInsightType === type ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedInsightType(type)}
                className="text-xs h-7"
              >
                {type === 'all' ? 'All' : type}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredInsights.length > 0 ? (
              filteredInsights.slice(0, 6).map((insight) => (
                <LearningInsightCard key={insight.id} insight={insight} />
              ))
            ) : (
              <div className="col-span-full text-center py-8 text-sm text-muted-foreground">
                No learning insights available
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}