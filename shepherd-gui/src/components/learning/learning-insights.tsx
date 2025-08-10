'use client'

import React, { memo, useState, useCallback, useMemo } from 'react'
import {
  Brain,
  TrendingUp,
  Target,
  Users,
  Lightbulb,
  BarChart3,
  Activity,
  Zap,
  Clock,
  CheckCircle,
  AlertTriangle,
  Info,
  ArrowUp,
  ArrowDown,
  Minus,
  Eye,
  Filter,
  Calendar,
  Download
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts'
import { format, subDays } from 'date-fns'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface PatternData {
  id: string
  name: string
  type: 'workflow' | 'user_behavior' | 'performance' | 'error'
  description: string
  confidence: number
  frequency: number
  impact: 'high' | 'medium' | 'low'
  trend: 'increasing' | 'stable' | 'decreasing'
  discoveredAt: Date
  lastSeen: Date
  examples: {
    id: string
    description: string
    timestamp: Date
    context: any
  }[]
}

export interface LearningMetrics {
  totalPatterns: number
  newPatternsThisWeek: number
  accuracyScore: number
  predictionSuccess: number
  adaptationRate: number
  knowledgeGrowth: number
}

export interface Recommendation {
  id: string
  type: 'optimization' | 'warning' | 'enhancement' | 'maintenance'
  priority: 'critical' | 'high' | 'medium' | 'low'
  title: string
  description: string
  expectedImpact: string
  effort: 'low' | 'medium' | 'high'
  category: string
  actionItems: string[]
  createdAt: Date
}

export interface LearningInsightsProps {
  patterns: PatternData[]
  metrics: LearningMetrics
  recommendations: Recommendation[]
  performanceData: Array<{
    date: string
    accuracy: number
    predictions: number
    adaptations: number
    knowledge: number
  }>
  onPatternDetails: (patternId: string) => void
  onRecommendationAction: (recommendationId: string, action: string) => void
  onExportInsights: (format: 'pdf' | 'json' | 'csv') => void
  className?: string
}

const CHART_COLORS = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4']

const MOCK_PERFORMANCE_DATA = [
  { date: '2024-01-01', accuracy: 85, predictions: 120, adaptations: 8, knowledge: 450 },
  { date: '2024-01-02', accuracy: 87, predictions: 135, adaptations: 12, knowledge: 465 },
  { date: '2024-01-03', accuracy: 89, predictions: 142, adaptations: 15, knowledge: 480 },
  { date: '2024-01-04', accuracy: 91, predictions: 158, adaptations: 18, knowledge: 495 },
  { date: '2024-01-05', accuracy: 88, predictions: 144, adaptations: 14, knowledge: 510 },
  { date: '2024-01-06', accuracy: 92, predictions: 167, adaptations: 22, knowledge: 525 },
  { date: '2024-01-07', accuracy: 94, predictions: 175, adaptations: 25, knowledge: 540 }
]

const PATTERN_DISTRIBUTION = [
  { name: 'Workflow', value: 35, color: '#3B82F6' },
  { name: 'User Behavior', value: 28, color: '#10B981' },
  { name: 'Performance', value: 22, color: '#8B5CF6' },
  { name: 'Error Patterns', value: 15, color: '#F59E0B' }
]

const KNOWLEDGE_AREAS = [
  { area: 'Task Optimization', current: 85, target: 95 },
  { area: 'Error Prediction', current: 78, target: 90 },
  { area: 'User Preferences', current: 92, target: 95 },
  { area: 'System Performance', current: 88, target: 93 },
  { area: 'Workflow Efficiency', current: 75, target: 88 },
  { area: 'Resource Usage', current: 82, target: 90 }
]

const LearningInsights = memo<LearningInsightsProps>(({
  patterns,
  metrics,
  recommendations,
  performanceData = MOCK_PERFORMANCE_DATA,
  onPatternDetails,
  onRecommendationAction,
  onExportInsights,
  className
}) => {
  const { theme, reducedMotion } = useUIStore(state => ({
    theme: state.theme,
    reducedMotion: state.reducedMotion
  }))

  const [activeTab, setActiveTab] = useState<'overview' | 'patterns' | 'recommendations' | 'performance'>('overview')
  const [selectedPatternType, setSelectedPatternType] = useState<string>('all')
  const [selectedTimeframe, setSelectedTimeframe] = useState<'7d' | '30d' | '90d'>('30d')

  // Filter patterns based on type and timeframe
  const filteredPatterns = useMemo(() => {
    let filtered = patterns

    if (selectedPatternType !== 'all') {
      filtered = filtered.filter(pattern => pattern.type === selectedPatternType)
    }

    const timeframeDate = subDays(new Date(), selectedTimeframe === '7d' ? 7 : selectedTimeframe === '30d' ? 30 : 90)
    filtered = filtered.filter(pattern => pattern.lastSeen >= timeframeDate)

    return filtered.sort((a, b) => b.confidence - a.confidence)
  }, [patterns, selectedPatternType, selectedTimeframe])

  const getTrendIcon = useCallback((trend: PatternData['trend']) => {
    switch (trend) {
      case 'increasing':
        return <ArrowUp className="w-4 h-4 text-green-500" />
      case 'decreasing':
        return <ArrowDown className="w-4 h-4 text-red-500" />
      case 'stable':
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }, [])

  const getImpactColor = useCallback((impact: PatternData['impact']) => {
    switch (impact) {
      case 'high':
        return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300'
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300'
      case 'low':
        return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300'
    }
  }, [])

  const getRecommendationIcon = useCallback((type: Recommendation['type']) => {
    switch (type) {
      case 'optimization':
        return <Zap className="w-4 h-4 text-blue-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'enhancement':
        return <Lightbulb className="w-4 h-4 text-purple-500" />
      case 'maintenance':
        return <Activity className="w-4 h-4 text-gray-500" />
    }
  }, [])

  const getPriorityColor = useCallback((priority: Recommendation['priority']) => {
    switch (priority) {
      case 'critical':
        return 'border-red-500 bg-red-50 dark:bg-red-950'
      case 'high':
        return 'border-orange-500 bg-orange-50 dark:bg-orange-950'
      case 'medium':
        return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950'
      case 'low':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-950'
    }
  }, [])

  const renderOverview = () => (
    <div className="p-6 space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Brain className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metrics.totalPatterns}
              </div>
              <div className="text-sm text-gray-500">Total Patterns</div>
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm text-green-600">
            <ArrowUp className="w-3 h-3 mr-1" />
            +{metrics.newPatternsThisWeek} this week
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Target className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metrics.accuracyScore}%
              </div>
              <div className="text-sm text-gray-500">Accuracy Score</div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metrics.predictionSuccess}%
              </div>
              <div className="text-sm text-gray-500">Prediction Success</div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <Activity className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metrics.adaptationRate}%
              </div>
              <div className="text-sm text-gray-500">Adaptation Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Trends */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Learning Performance
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(date) => format(new Date(date), 'MMM dd')} />
              <YAxis />
              <Tooltip
                labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                formatter={(value: number, name: string) => [
                  name === 'accuracy' ? `${value}%` : value.toLocaleString(),
                  name.charAt(0).toUpperCase() + name.slice(1)
                ]}
              />
              <Line type="monotone" dataKey="accuracy" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="predictions" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Pattern Distribution */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Pattern Distribution
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={PATTERN_DISTRIBUTION}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ name, value }) => `${name}: ${value}`}
              >
                {PATTERN_DISTRIBUTION.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Knowledge Areas Radar */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Knowledge Areas Progress
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={KNOWLEDGE_AREAS}>
            <PolarGrid />
            <PolarAngleAxis dataKey="area" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar name="Current" dataKey="current" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
            <Radar name="Target" dataKey="target" stroke="#10B981" fill="#10B981" fillOpacity={0.1} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )

  const renderPatterns = () => (
    <div className="p-6">
      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <select
          value={selectedPatternType}
          onChange={(e) => setSelectedPatternType(e.target.value)}
          className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
        >
          <option value="all">All Types</option>
          <option value="workflow">Workflow</option>
          <option value="user_behavior">User Behavior</option>
          <option value="performance">Performance</option>
          <option value="error">Error Patterns</option>
        </select>

        <select
          value={selectedTimeframe}
          onChange={(e) => setSelectedTimeframe(e.target.value as any)}
          className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      {/* Pattern List */}
      <div className="space-y-4">
        {filteredPatterns.map((pattern) => (
          <div
            key={pattern.id}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {pattern.name}
                  </h3>
                  <span className={cn(
                    'px-2 py-1 text-xs rounded-full',
                    getImpactColor(pattern.impact)
                  )}>
                    {pattern.impact} impact
                  </span>
                  <div className="flex items-center gap-1">
                    {getTrendIcon(pattern.trend)}
                    <span className="text-sm text-gray-500">{pattern.trend}</span>
                  </div>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  {pattern.description}
                </p>

                <div className="flex items-center gap-6 text-sm text-gray-500">
                  <div>Confidence: <span className="font-medium">{pattern.confidence}%</span></div>
                  <div>Frequency: <span className="font-medium">{pattern.frequency}x</span></div>
                  <div>Last seen: <span className="font-medium">{format(pattern.lastSeen, 'MMM dd, yyyy')}</span></div>
                </div>
              </div>

              <button
                onClick={() => onPatternDetails(pattern.id)}
                className={cn(
                  'px-3 py-1.5 text-sm border border-blue-300 dark:border-blue-700 text-blue-600 rounded hover:bg-blue-50 dark:hover:bg-blue-950',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <Eye className="w-4 h-4 mr-1" />
                Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderRecommendations = () => (
    <div className="p-6 space-y-4">
      {recommendations.map((recommendation) => (
        <div
          key={recommendation.id}
          className={cn(
            'p-6 rounded-lg border-l-4',
            getPriorityColor(recommendation.priority)
          )}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              {getRecommendationIcon(recommendation.type)}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {recommendation.title}
                  </h3>
                  <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded">
                    {recommendation.priority}
                  </span>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  {recommendation.description}
                </p>

                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <span className="text-gray-500">Expected Impact:</span>
                    <div className="font-medium">{recommendation.expectedImpact}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Effort Level:</span>
                    <div className="font-medium capitalize">{recommendation.effort}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="text-gray-500 text-sm">Action Items:</span>
                  <ul className="mt-1 space-y-1">
                    {recommendation.actionItems.map((item, index) => (
                      <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                        <span className="w-4 h-4 mr-2 mt-0.5 text-xs">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex gap-2 ml-4">
              <button
                onClick={() => onRecommendationAction(recommendation.id, 'implement')}
                className={cn(
                  'px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                Implement
              </button>
              <button
                onClick={() => onRecommendationAction(recommendation.id, 'dismiss')}
                className={cn(
                  'px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 text-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  const renderPerformance = () => (
    <div className="p-6 space-y-6">
      {/* Performance Metrics */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Detailed Performance Metrics
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={(date) => format(new Date(date), 'MMM dd')} />
            <YAxis />
            <Tooltip
              labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
              formatter={(value: number, name: string) => [
                value.toLocaleString(),
                name.charAt(0).toUpperCase() + name.slice(1)
              ]}
            />
            <Area type="monotone" dataKey="knowledge" stackId="1" stroke="#8B5CF6" fill="#8B5CF6" />
            <Area type="monotone" dataKey="predictions" stackId="1" stroke="#10B981" fill="#10B981" />
            <Area type="monotone" dataKey="adaptations" stackId="1" stroke="#F59E0B" fill="#F59E0B" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Knowledge Growth Timeline */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Knowledge Growth Timeline
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={(date) => format(new Date(date), 'MMM dd')} />
            <YAxis />
            <Tooltip
              labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
              formatter={(value: number) => [value.toLocaleString(), 'Knowledge Items']}
            />
            <Bar dataKey="knowledge" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )

  return (
    <div className={cn('flex flex-col h-full bg-gray-50 dark:bg-gray-950', className)}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-blue-500" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Learning Insights
              </h1>
              <p className="text-sm text-gray-500">
                AI-powered patterns and recommendations
              </p>
            </div>
          </div>

          <button
            onClick={() => onExportInsights('pdf')}
            className={cn(
              'px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700',
              !reducedMotion && 'transition-colors duration-200'
            )}
          >
            <Download className="w-4 h-4 mr-1" />
            Export Report
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-1 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'patterns', label: 'Patterns', icon: Target },
            { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
            { id: 'performance', label: 'Performance', icon: TrendingUp }
          ].map((tab) => {
            const IconComponent = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 text-sm rounded-md',
                  activeTab === tab.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <IconComponent className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'patterns' && renderPatterns()}
        {activeTab === 'recommendations' && renderRecommendations()}
        {activeTab === 'performance' && renderPerformance()}
      </div>
    </div>
  )
})

LearningInsights.displayName = 'LearningInsights'

export default LearningInsights