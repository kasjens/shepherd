/**
 * Tests for Learning Progress components
 */

import { render, screen, fireEvent } from '../../../setup'
import { 
  LearningProgressOverview, 
  LearningInsightCard, 
  FeedbackSummaryPanel,
  PatternLearningPanel,
  AdaptationStatsPanel 
} from '@/components/features/learning/learning-progress'

// Mock data
const mockInsight = {
  id: 'insight-1',
  agentId: 'agent-1',
  agentName: 'TestAgent',
  type: 'pattern' as const,
  category: 'success' as const,
  title: 'Workflow optimization discovered',
  description: 'Found a pattern that reduces execution time by 15%',
  confidence: 0.85,
  timestamp: Date.now() - 300000,
  metrics: {
    before: 2.5,
    after: 2.1,
    improvement: 16.0
  },
  recommendations: [
    'Apply this pattern to similar workflows',
    'Monitor performance impact over time'
  ]
}

const mockFeedbackSummary = {
  totalFeedback: 47,
  feedbackByType: {
    correction: 15,
    guidance: 12,
    rating: 10,
    suggestion: 6,
    preference: 4
  },
  averageRating: 4.2,
  recentTrend: 'improving' as const,
  topIssues: [
    { issue: 'Response time too slow', count: 8, severity: 'medium' as const },
    { issue: 'Missing error handling', count: 5, severity: 'high' as const }
  ]
}

const mockPatternLearning = {
  totalPatternsLearned: 23,
  failurePatternsIdentified: 5,
  activePatternsCached: 12,
  averagePatternScore: 0.78,
  learningBufferSize: 50,
  recentPatterns: [
    {
      id: 'pattern-1',
      type: 'Sequential Processing',
      confidence: 0.92,
      usageCount: 8,
      performance: 1.8
    },
    {
      id: 'pattern-2', 
      type: 'Parallel Validation',
      confidence: 0.85,
      usageCount: 5,
      performance: 2.3
    }
  ]
}

const mockAdaptationStats = {
  enabledTypes: ['preference_based', 'performance_based', 'learning_based'],
  cacheSize: 128,
  performanceTracking: {
    'timeout_adjustment': {
      averageScore: 0.85,
      usageCount: 15,
      trend: 'improving' as const
    },
    'retry_strategy': {
      averageScore: 0.72,
      usageCount: 8,
      trend: 'stable' as const
    }
  },
  knowledgeBase: {
    preferences: 12,
    learnedPatterns: 23,
    failurePatterns: 5
  }
}

describe('LearningInsightCard', () => {
  test('renders insight information correctly', () => {
    render(<LearningInsightCard insight={mockInsight} />)
    
    expect(screen.getByText('Workflow optimization discovered')).toBeInTheDocument()
    expect(screen.getByText('Found a pattern that reduces execution time by 15%')).toBeInTheDocument()
    expect(screen.getByText('TestAgent')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument() // confidence
  })

  test('displays metrics when available', () => {
    render(<LearningInsightCard insight={mockInsight} />)
    
    expect(screen.getByText('Before')).toBeInTheDocument()
    expect(screen.getByText('2.50')).toBeInTheDocument()
    expect(screen.getByText('After')).toBeInTheDocument()
    expect(screen.getByText('2.10')).toBeInTheDocument()
    expect(screen.getByText('+16.0%')).toBeInTheDocument()
  })

  test('shows recommendations when available', () => {
    render(<LearningInsightCard insight={mockInsight} />)
    
    expect(screen.getByText('Recommendations:')).toBeInTheDocument()
    expect(screen.getByText('Apply this pattern to similar workflows')).toBeInTheDocument()
    expect(screen.getByText('Monitor performance impact over time')).toBeInTheDocument()
  })

  test('renders different insight categories with appropriate icons', () => {
    const concernInsight = { ...mockInsight, category: 'concern' as const }
    render(<LearningInsightCard insight={concernInsight} />)
    
    // Should render without error and show concern styling
    expect(screen.getByText('Workflow optimization discovered')).toBeInTheDocument()
  })

  test('formats timestamp correctly', () => {
    render(<LearningInsightCard insight={mockInsight} />)
    
    expect(screen.getByText(/ago/)).toBeInTheDocument()
  })
})

describe('FeedbackSummaryPanel', () => {
  test('displays feedback statistics', () => {
    render(<FeedbackSummaryPanel summary={mockFeedbackSummary} />)
    
    expect(screen.getByText('47')).toBeInTheDocument() // total feedback
    expect(screen.getByText('4.2')).toBeInTheDocument() // average rating
    expect(screen.getByText('improving')).toBeInTheDocument() // trend
  })

  test('shows feedback breakdown by type', () => {
    render(<FeedbackSummaryPanel summary={mockFeedbackSummary} />)
    
    expect(screen.getByText('Correction')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('Guidance')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  test('displays top issues', () => {
    render(<FeedbackSummaryPanel summary={mockFeedbackSummary} />)
    
    expect(screen.getByText('Top Issues')).toBeInTheDocument()
    expect(screen.getByText('Response time too slow')).toBeInTheDocument()
    expect(screen.getByText('Missing error handling')).toBeInTheDocument()
    expect(screen.getByText('×8')).toBeInTheDocument()
    expect(screen.getByText('×5')).toBeInTheDocument()
  })

  test('shows severity badges for issues', () => {
    render(<FeedbackSummaryPanel summary={mockFeedbackSummary} />)
    
    expect(screen.getByText('medium')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })
})

describe('PatternLearningPanel', () => {
  test('displays pattern learning metrics', () => {
    render(<PatternLearningPanel learning={mockPatternLearning} />)
    
    expect(screen.getByText('23')).toBeInTheDocument() // patterns learned
    expect(screen.getByText('5')).toBeInTheDocument() // failures identified
    expect(screen.getByText('78%')).toBeInTheDocument() // pattern score
    expect(screen.getByText('12')).toBeInTheDocument() // cached patterns
    expect(screen.getByText('50')).toBeInTheDocument() // buffer size
  })

  test('shows recent patterns', () => {
    render(<PatternLearningPanel learning={mockPatternLearning} />)
    
    expect(screen.getByText('Sequential Processing')).toBeInTheDocument()
    expect(screen.getByText('Parallel Validation')).toBeInTheDocument()
    expect(screen.getByText('92%')).toBeInTheDocument() // confidence
    expect(screen.getByText('Used 8 times')).toBeInTheDocument()
  })

  test('displays pattern performance metrics', () => {
    render(<PatternLearningPanel learning={mockPatternLearning} />)
    
    expect(screen.getByText('1.8s avg')).toBeInTheDocument()
    expect(screen.getByText('2.3s avg')).toBeInTheDocument()
  })
})

describe('AdaptationStatsPanel', () => {
  test('shows enabled adaptation types', () => {
    render(<AdaptationStatsPanel stats={mockAdaptationStats} />)
    
    expect(screen.getByText('preference based')).toBeInTheDocument()
    expect(screen.getByText('performance based')).toBeInTheDocument()
    expect(screen.getByText('learning based')).toBeInTheDocument()
  })

  test('displays knowledge base statistics', () => {
    render(<AdaptationStatsPanel stats={mockAdaptationStats} />)
    
    expect(screen.getByText('12')).toBeInTheDocument() // preferences
    expect(screen.getByText('23')).toBeInTheDocument() // learned patterns
    expect(screen.getByText('128')).toBeInTheDocument() // cache size
  })

  test('shows performance tracking details', () => {
    render(<AdaptationStatsPanel stats={mockAdaptationStats} />)
    
    expect(screen.getByText('timeout_adjustment')).toBeInTheDocument()
    expect(screen.getByText('retry_strategy')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument() // average score
    expect(screen.getByText('72%')).toBeInTheDocument() // average score
    expect(screen.getByText('Used 15 times')).toBeInTheDocument()
    expect(screen.getByText('Used 8 times')).toBeInTheDocument()
  })
})

describe('LearningProgressOverview', () => {
  const mockProps = {
    insights: [mockInsight],
    feedbackSummary: mockFeedbackSummary,
    patternLearning: mockPatternLearning,
    adaptationStats: mockAdaptationStats
  }

  test('renders all learning progress panels', () => {
    render(<LearningProgressOverview {...mockProps} />)
    
    expect(screen.getByText('Learning Progress')).toBeInTheDocument()
    expect(screen.getByText('Feedback Summary')).toBeInTheDocument()
    expect(screen.getByText('Pattern Learning')).toBeInTheDocument()
    expect(screen.getByText('Adaptive Behavior')).toBeInTheDocument()
    expect(screen.getByText('Learning Insights')).toBeInTheDocument()
  })

  test('filters insights by type', () => {
    render(<LearningProgressOverview {...mockProps} />)
    
    // Click on pattern filter
    const patternFilter = screen.getByRole('button', { name: 'pattern' })
    fireEvent.click(patternFilter)
    
    expect(screen.getByText('Workflow optimization discovered')).toBeInTheDocument()
  })

  test('shows empty state when no insights', () => {
    const emptyProps = { ...mockProps, insights: [] }
    render(<LearningProgressOverview {...emptyProps} />)
    
    expect(screen.getByText('No learning insights available')).toBeInTheDocument()
  })

  test('displays insight filter buttons', () => {
    render(<LearningProgressOverview {...mockProps} />)
    
    expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'feedback' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'pattern' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'adaptation' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'performance' })).toBeInTheDocument()
  })
})