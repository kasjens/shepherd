# GUI Components Documentation

This document provides a comprehensive list of all GUI components in the Shepherd application, their purposes, and expected actions.

## Layout Components

### Sidebar (`/components/layout/sidebar.tsx`)
**Purpose**: Primary navigation and conversation management panel
**Actions**:
- Create new chat conversations
- Switch between existing conversations
- Search through conversation history
- Access settings and help
- Select project folder for context
- View system status (Ollama connection)
- Collapse/expand sidebar for more workspace

### ConversationArea (`/components/layout/conversation-area.tsx`)
**Purpose**: Main chat interface for user-AI interaction
**Actions**:
- Display message history with sender identification
- Show real-time typing indicators
- Support markdown rendering in messages
- Display inline progress indicators for long tasks
- Auto-scroll to latest messages
- Support message copying and selection

### ArtifactsPanel (`/components/layout/artifacts-panel.tsx`)
**Purpose**: Display and manage generated code, reports, and outputs
**Actions**:
- View generated artifacts with syntax highlighting
- Switch between multiple artifacts via tabs
- Copy artifact content to clipboard
- Download/export artifacts
- Execute code artifacts (when applicable)
- Dismiss/close individual artifacts
- Resize panel for optimal viewing

## Feature Components

### ProjectFolderSelector (`/components/features/settings/project-folder-selector.tsx`)
**Purpose**: Select and display current working directory for file operations
**Actions**:
- Open native folder selection dialog
- Display selected folder path
- Clear/reset folder selection
- Persist selection across sessions
- Show truncated path for long directories

### MessageInput (`/components/features/chat/message-input.tsx`)
**Purpose**: Input interface for user messages and commands
**Actions**:
- Multi-line text input with auto-resize
- Send messages via Enter or button click
- Command autocomplete and suggestions
- Emoji picker integration
- File attachment support
- Voice input recognition

## Phase 9: Frontend Collaboration UI Components

### Agent Status Components (`/components/features/agents/agent-status.tsx`)
**Purpose**: Real-time visualization of agent states and performance metrics
**Components**:
- `AgentStatusCard`: Individual agent status display with progress indicators
- `AgentStatusPanel`: Grid view of all active agents with filtering
- `AgentDetailView`: Expanded view showing detailed agent information
**Actions**:
- Display agent status (idle, working, error, completed)
- Show current task progress with visual indicators
- Filter agents by status, type, or performance metrics
- View detailed agent performance statistics
- Show agent resource usage (CPU, memory)
- Display agent connections and communication patterns
- View agent tool usage and capabilities

### Agent Collaboration Components (`/components/features/agents/agent-collaboration.tsx`)
**Purpose**: Visualization of agent-to-agent interactions and teamwork
**Actions**:
- Display agent communication network topology
- Show message flow between agents in real-time
- Visualize collaborative task distribution
- Monitor peer review processes and consensus building
- Track shared context and knowledge exchange

### Communication Flow Components (`/components/features/agents/communication-flow.tsx`)
**Purpose**: Real-time visualization of agent communication events
**Components**:
- `CommunicationEventItem`: Individual message/event display
- `CommunicationNetwork`: Network topology of agent connections
- `CommunicationStatsPanel`: Communication statistics overview
**Actions**:
- Stream real-time communication events via WebSocket
- Filter events by type (request, response, broadcast, peer_review)
- Show message priorities and response times
- Display conversation threads and context IDs
- Pause/resume event streaming
- View connection strength and activity metrics

### Memory Flow Components (`/components/features/memory/memory-flow.tsx`)
**Purpose**: Visualization of memory operations across the three-tier architecture
**Components**:
- `MemoryFlowVisualizer`: Main memory transfer visualization
- `MemoryTransferItem`: Individual memory operation display
- `MemoryUsagePanel`: Per-agent memory usage statistics
**Actions**:
- Show memory transfers between agents and storage tiers
- Display memory usage across local, shared, persistent, and vector tiers
- Filter transfers by type (discovery, context, learning, knowledge, pattern)
- Monitor agent subscription patterns to shared contexts
- View memory operation statistics and trends
- Pause/resume memory flow monitoring

### Learning Progress Components (`/components/features/learning/learning-progress.tsx`)
**Purpose**: Visualization of Phase 8 learning system progress and insights
**Components**:
- `LearningProgressOverview`: Main dashboard for learning metrics
- `LearningInsightCard`: Individual learning insight display
- `FeedbackSummaryPanel`: User feedback statistics and trends
- `PatternLearningPanel`: Pattern discovery and optimization metrics
- `AdaptationStatsPanel`: Adaptive behavior statistics
**Actions**:
- Display learning insights with confidence scores and recommendations
- Show feedback processing statistics and trends
- Visualize pattern learning progress and success rates
- Monitor adaptive behavior performance tracking
- Filter insights by type (feedback, pattern, adaptation, performance)
- Show learning score calculations and trend analysis

### Performance Metrics Components (`/components/features/performance/metrics-dashboard.tsx`)
**Purpose**: Comprehensive system performance monitoring dashboard
**Components**:
- `SystemMetricsPanel`: System resource utilization (CPU, memory, disk, network)
- `WorkflowMetricsPanel`: Workflow execution statistics and performance
- `AgentMetricsPanel`: Agent performance and efficiency metrics
- `PerformanceAlertsPanel`: System alerts and performance warnings
- `MetricsTrendsPanel`: Performance trends and change indicators
**Actions**:
- Monitor real-time system resource usage with visual indicators
- Track workflow execution success rates and timing
- Display agent efficiency and task completion metrics
- Show performance alerts with acknowledgment system
- Visualize performance trends with improvement/decline indicators
- Display error rates and common failure patterns

## Phase 10: Advanced Analytics Components

### Analytics Dashboard Components (`/components/features/analytics/analytics-dashboard.tsx`)
**Purpose**: Advanced analytics visualization and management interface
**Components**:
- `AnalyticsDashboard`: Main analytics dashboard container with customizable widgets
- `WidgetContainer`: Individual widget wrapper with resize and configuration controls
- `DashboardGrid`: Responsive grid layout system for widget arrangement
- `DashboardToolbar`: Dashboard management toolbar with save, share, and export options
**Actions**:
- Create and manage custom analytics dashboards
- Drag and drop widget positioning with grid snapping
- Configure widget data sources and refresh intervals
- Save dashboard configurations with persistence
- Share dashboards with team members
- Export dashboard layouts as templates

### Collaboration Analytics Components (`/components/features/analytics/collaboration-analytics.tsx`)
**Purpose**: Agent collaboration pattern analysis and visualization
**Components**:
- `CollaborationNetworkGraph`: Interactive network topology visualization of agent interactions
- `CollaborationMetricsPanel`: Key collaboration metrics and KPIs display
- `InteractionTimelineView`: Chronological view of agent interactions and communications
- `TeamEfficiencyPanel`: Team performance analysis with collaboration effectiveness scores
**Actions**:
- Visualize agent communication networks with interactive graph controls
- Display collaboration metrics including communication frequency and effectiveness
- Show interaction patterns over time with timeline scrubbing
- Analyze team performance with filtering by agent type and time period
- Export collaboration reports in multiple formats
- Configure collaboration metric thresholds and alerts

### Predictive Analytics Components (`/components/features/analytics/predictive-analytics.tsx`)
**Purpose**: Machine learning predictions and insights visualization
**Components**:
- `PredictionPanel`: Main predictions display with confidence indicators
- `WorkflowSuccessPrediction`: Workflow success probability visualization
- `PerformanceForecast`: Performance predictions with trend analysis
- `ResourceUsagePrediction`: Resource requirement predictions with capacity planning
- `RecommendationEngine`: AI-driven recommendations display
**Actions**:
- Display workflow success predictions with confidence scores
- Show performance forecasts with interactive trend lines
- Visualize resource usage predictions for capacity planning
- Present AI recommendations with reasoning explanations
- Configure prediction parameters and model selection
- Track prediction accuracy over time with validation metrics

### Metrics Aggregator Components (`/components/features/analytics/metrics-aggregator.tsx`)
**Purpose**: Real-time metrics collection and trend analysis interface
**Components**:
- `MetricsOverviewPanel`: High-level metrics summary with key performance indicators
- `TrendAnalysisChart`: Interactive trend visualization with multiple metrics
- `AnomalyDetectionPanel`: Anomaly alerts and pattern deviation indicators
- `HistoricalDataExplorer`: Time-series data exploration with drill-down capabilities
**Actions**:
- Monitor real-time system metrics with live updating displays
- Analyze performance trends with interactive time range selection
- Display anomaly alerts with automatic pattern deviation detection
- Explore historical data with zoom and filter capabilities
- Configure metric collection intervals and retention policies
- Set up automated alerts for metric threshold breaches

### Export Manager Components (`/components/features/analytics/export-manager.tsx`)
**Purpose**: Multi-format data export and report generation interface
**Components**:
- `ExportWizard`: Step-by-step export configuration interface
- `ReportTemplateSelector`: Pre-built report template selection with preview
- `ExportFormatSelector`: Multi-format export options (PDF, CSV, JSON, Excel, HTML, Markdown)
- `ScheduledExportsPanel`: Automated export scheduling and management
- `ExportHistoryView`: Export job history with status tracking and download links
**Actions**:
- Configure data exports with flexible filtering and date range selection
- Select from professional report templates with customization options
- Choose export formats based on intended use (analysis, sharing, archival)
- Schedule automated exports with configurable frequency and distribution
- Track export job status with progress indicators and error handling
- Download completed exports with organized file management

### Analytics Widget Library (`/components/features/analytics/widgets/`)
**Purpose**: Reusable analytics visualization widgets
**Widget Types**:
1. **LineChart Widget** (`line-chart-widget.tsx`): Time-series trend visualization
2. **BarChart Widget** (`bar-chart-widget.tsx`): Comparative metrics display
3. **PieChart Widget** (`pie-chart-widget.tsx`): Distribution analysis visualization
4. **GaugeChart Widget** (`gauge-chart-widget.tsx`): Performance level indicators
5. **TableWidget** (`table-widget.tsx`): Tabular data with sorting and filtering
6. **NetworkGraph Widget** (`network-graph-widget.tsx`): Relationship visualization
7. **Heatmap Widget** (`heatmap-widget.tsx`): Activity pattern visualization
8. **ProgressBar Widget** (`progress-bar-widget.tsx`): Goal tracking and completion
9. **StatusIndicator Widget** (`status-indicator-widget.tsx`): System health displays

**Widget Features**:
- **Real-time Data Streaming**: WebSocket integration for live updates
- **Interactive Controls**: Zoom, filter, and drill-down capabilities
- **Customizable Styling**: Theme-aware styling with customization options
- **Responsive Design**: Adaptive layouts for different screen sizes
- **Export Capabilities**: Individual widget export to images and data formats
- **Configuration Panels**: User-friendly widget configuration interfaces

### Analytics API Integration (`/lib/analytics-api.ts`)
**Purpose**: TypeScript client for Phase 10 analytics system backend
**Functionality**:
- Connect to analytics REST endpoints with full type safety
- Stream real-time analytics data via WebSocket connections
- Manage dashboard configurations with CRUD operations
- Generate and track export jobs with status monitoring
- Access predictive analytics with parameter configuration
- Retrieve metrics data with flexible querying capabilities
**Methods**:
- `getAnalyticsData()`: Retrieve system metrics and performance data
- `createDashboard()`: Create new custom analytics dashboards
- `updateWidget()`: Update widget configurations and data sources
- `generateExport()`: Initiate data exports with format and filter selection
- `getPredictions()`: Access ML predictions with confidence intervals
- `streamMetrics()`: Establish WebSocket connections for real-time data
- `getCollaborationMetrics()`: Retrieve agent collaboration analysis data

## API Integration Components

### Learning API Integration (`/lib/learning-api.ts`)
**Purpose**: TypeScript client for Phase 8 learning system backend
**Functionality**:
- Submit user feedback for processing (6 feedback types supported)
- Retrieve learning insights and statistics
- Get pattern recommendations based on context
- Apply and track adaptive behavior modifications
- Configure learning settings per agent
- Monitor system-wide learning statistics
**Methods**:
- `submitFeedback()`: Process user corrections, preferences, and guidance
- `getLearningInsights()`: Retrieve learning progress and metrics
- `getPatternRecommendations()`: Get workflow optimization suggestions
- `getAdaptations()`: Retrieve context-specific behavioral adaptations
- `recordAdaptationOutcome()`: Track adaptation success/failure rates
**Purpose**: Multi-line input area for user messages
**Actions**:
- Type and edit messages with markdown support
- Send messages via Enter or button click
- Use Ctrl+Enter for multi-line messages
- Show character count or limits
- Support file drag-and-drop
- Clear input after sending

### MessageList (`/components/features/chat/message-list.tsx`)
**Purpose**: Display conversation history in terminal-style flow
**Actions**:
- Render user and AI messages with distinct styling
- Show timestamps for each message
- Support message actions (copy, retry, edit)
- Display system messages and notifications
- Implement virtual scrolling for performance

### ArtifactViewer (`/components/features/artifacts/artifact-viewer.tsx`)
**Purpose**: Display individual artifacts with appropriate formatting
**Actions**:
- Syntax highlighting for 50+ languages
- Line numbers and code folding
- Search within artifact content
- Toggle word wrap
- Full-screen mode
- Print artifact content

### WorkflowProgress (`/components/features/workflow/workflow-progress.tsx`)
**Purpose**: Show real-time progress of multi-step workflows
**Actions**:
- Display workflow steps and current status
- Show elapsed time and estimates
- Indicate success/failure per step
- Allow workflow cancellation
- Expand/collapse detailed logs

### ThemeSelector (`/components/features/settings/theme-selector.tsx`)
**Purpose**: Switch between available color themes
**Actions**:
- Preview themes before applying
- Persist theme preference
- Support system theme detection
- Apply theme without page reload

### ConversationCompactor (`/components/features/conversation/conversation-compactor.tsx`)
**Purpose**: Monitor token usage and manage conversation compacting
**Actions**:
- Display real-time token usage with progress bar
- Show warning indicators at 80% and 90% thresholds
- Open compacting strategy selection dialog
- Execute conversation compacting with chosen strategy
- Display compacting results with before/after statistics
- Provide WebSocket notifications for auto-compacting suggestions
- Support five compacting strategies: Auto, Milestone, Selective, Aggressive, Conservative

## UI Components (Base)

### Button (`/components/ui/button.tsx`)
**Purpose**: Reusable button component with multiple variants
**Variants**:
- Primary (shepherd-blue actions)
- Secondary (outline style)
- Ghost (minimal style)
- Danger (destructive actions)
**Actions**:
- Click handling with loading states
- Keyboard navigation support
- Disabled state handling

### Input (`/components/ui/input.tsx`)
**Purpose**: Text input field with consistent styling
**Actions**:
- Text entry with validation
- Placeholder and label support
- Error state display
- Clear button option
- Password visibility toggle

### Textarea (`/components/ui/textarea.tsx`)
**Purpose**: Multi-line text input for longer content
**Actions**:
- Auto-resize based on content
- Character/line counting
- Markdown preview toggle
- Syntax highlighting hints

### Select (`/components/ui/select.tsx`)
**Purpose**: Dropdown selection component
**Actions**:
- Single/multi selection modes
- Search/filter options
- Keyboard navigation
- Custom option rendering

### Dialog (`/components/ui/dialog.tsx`)
**Purpose**: Modal dialog for confirmations and forms
**Actions**:
- Open/close with animations
- Backdrop click handling
- ESC key dismissal
- Focus trap management
- Nested dialog support

### Tabs (`/components/ui/tabs.tsx`)
**Purpose**: Tab navigation for grouped content
**Actions**:
- Switch between tab panels
- Keyboard navigation (arrow keys)
- Dynamic tab addition/removal
- Tab overflow handling
- Persist active tab state

### Tooltip (`/components/ui/tooltip.tsx`)
**Purpose**: Contextual information on hover
**Actions**:
- Show on hover/focus
- Position automatically
- Delay configuration
- Mobile touch support

### Badge (`/components/ui/badge.tsx`)
**Purpose**: Status indicators and labels
**Variants**:
- Status (online/offline/busy)
- Count (numeric indicators)
- Category (topic labels)
**Actions**:
- Click for filtering
- Dismiss/remove capability

### ScrollArea (`/components/ui/scroll-area.tsx`)
**Purpose**: Custom scrollbar styling and behavior
**Actions**:
- Smooth scrolling
- Custom scrollbar appearance
- Scroll position persistence
- Programmatic scroll control

### Separator (`/components/ui/separator.tsx`)
**Purpose**: Visual divider between sections
**Variants**:
- Horizontal/vertical orientation
- Solid/dashed styles
- With/without spacing

## Composite Components

### ConversationList (`/components/features/conversations/conversation-list.tsx`)
**Purpose**: Display list of all conversations in sidebar
**Actions**:
- Filter by date/status
- Sort by recent/name
- Delete conversations
- Export conversation history
- Pin important conversations

### SettingsPanel (`/components/features/settings/settings-panel.tsx`)
**Purpose**: Application configuration interface
**Actions**:
- Modify API endpoints
- Configure LLM models
- Set keyboard shortcuts
- Manage data privacy
- Import/export settings

### StatusIndicator (`/components/features/status/status-indicator.tsx`)
**Purpose**: Show connection status to backend services
**Actions**:
- Display connection state
- Show latency metrics
- Retry failed connections
- View detailed diagnostics

### CommandPalette (`/components/features/command/command-palette.tsx`)
**Purpose**: Quick action launcher (Ctrl+K)
**Actions**:
- Search all available actions
- Execute commands
- Navigate to conversations
- Access recent artifacts
- Keyboard-only operation

### ResizeHandle (`/components/ui/resize-handle.tsx`)
**Purpose**: Allow panel resizing via drag
**Actions**:
- Drag to resize panels
- Double-click to reset
- Snap to preset sizes
- Persist size preferences

## Specialized Components

### CodeEditor (`/components/features/editor/code-editor.tsx`)
**Purpose**: Embedded code editing with highlighting
**Actions**:
- Syntax highlighting
- Auto-completion hints
- Format on save
- Multiple cursor support
- Find/replace functionality

### MarkdownRenderer (`/components/features/markdown/markdown-renderer.tsx`)
**Purpose**: Render markdown content with extensions
**Actions**:
- Render standard markdown
- Support code blocks
- Handle tables and lists
- Copy code blocks
- Render mermaid diagrams

### FileUploader (`/components/features/files/file-uploader.tsx`)
**Purpose**: Handle file uploads and processing
**Actions**:
- Drag and drop files
- Browse file selection
- Show upload progress
- Validate file types
- Cancel uploads

### ErrorBoundary (`/components/features/error/error-boundary.tsx`)
**Purpose**: Gracefully handle component errors
**Actions**:
- Catch rendering errors
- Display fallback UI
- Log error details
- Offer recovery actions

## Animation Components

### LoadingSpinner (`/components/ui/loading-spinner.tsx`)
**Purpose**: Indicate loading states
**Variants**:
- Small (inline)
- Medium (content)
- Large (page)
**Actions**:
- Animate continuously
- Show/hide based on state

### ProgressBar (`/components/ui/progress-bar.tsx`)
**Purpose**: Show determinate progress
**Actions**:
- Update progress value
- Show percentage text
- Animate transitions
- Support multiple segments

### SkeletonLoader (`/components/ui/skeleton-loader.tsx`)
**Purpose**: Placeholder during content loading
**Actions**:
- Match content layout
- Animate shimmer effect
- Progressive content reveal

## Utility Components

### Portal (`/components/ui/portal.tsx`)
**Purpose**: Render content outside component hierarchy
**Actions**:
- Mount to document body
- Maintain React context
- Handle cleanup

### FocusTrap (`/components/ui/focus-trap.tsx`)
**Purpose**: Keep keyboard focus within bounds
**Actions**:
- Trap tab navigation
- Return focus on unmount
- Handle escape key

### VisuallyHidden (`/components/ui/visually-hidden.tsx`)
**Purpose**: Hide content visually but keep for screen readers
**Actions**:
- Provide accessible labels
- Announce dynamic changes

## State Management

### Stores (using Zustand)
- **useConversationStore**: Manage chat conversations and token usage monitoring
- **useArtifactStore**: Handle artifacts lifecycle
- **useSettingsStore**: Application preferences
- **useProjectStore**: Project folder and context
- **useThemeStore**: Theme selection and application
- **useWorkflowStore**: Workflow execution state

## Expected User Interactions

1. **New User Flow**:
   - Open application → See welcome message
   - Click "New Chat" → Start conversation
   - Type message → Press Enter to send
   - View AI response → See artifacts generated
   - Click artifact → View in artifacts panel

2. **Power User Flow**:
   - Ctrl+N → New chat
   - Ctrl+K → Command palette
   - Type command → Execute
   - Ctrl+1/2/3 → Switch panels
   - Drag borders → Resize panels

3. **File Operations**:
   - Click folder selector → Choose project
   - Drag files → Upload to conversation
   - Click artifact → Copy or download
   - Use keyboard shortcuts → Navigate efficiently

4. **Workflow Execution**:
   - Submit complex request → See workflow steps
   - Monitor progress → View real-time updates
   - Click step → See detailed logs
   - Cancel if needed → Rollback safely

This component structure provides a professional, efficient, and accessible interface for the Shepherd intelligent workflow orchestrator.