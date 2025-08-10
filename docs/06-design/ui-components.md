# GUI Components Documentation

This document provides a comprehensive list of all GUI components in the Shepherd application's simplified interface, their purposes, and expected actions.

## Core Layout Components

### Sidebar (`/components/layout/sidebar/Sidebar.tsx`)
**Purpose**: Collapsible control panel for all application controls and settings
**Sections**:
1. **Header** - Shepherd.png logo and collapse toggle
2. **Quick Actions** - New conversation, history, save/export
3. **Workflow Controls** - Mode selection and agent settings
4. **Active Agents Monitor** - Real-time agent status
5. **Resource Usage** - Memory, tokens, API calls
6. **Footer** - Settings, analytics, help, connection status

**Actions**:
- Toggle collapse/expand state (280px ↔ 48px, showing full logo/text or logo only)
- Create new conversation
- Access conversation history
- Export current workflow
- Select workflow mode (Auto/Sequential/Parallel/Conditional/Hierarchical)
- Adjust agent settings (max agents, timeout)
- Toggle features (collaboration, vector memory)
- Monitor active agent status
- View resource consumption
- Access settings and analytics
- Check connection status

### ConversationArea (`/components/layout/conversation/ConversationArea.tsx`)
**Purpose**: Primary workspace for user-AI interaction
**Sections**:
1. **Top Bar** - Workflow status and controls
2. **Message List** - Conversation history
3. **Input Area** - Message composition

**Actions**:
- Display current workflow type and status
- Show/hide stop button during execution
- Render user and AI messages with timestamps
- Display execution steps with progress indicators
- Show generated artifacts as clickable buttons
- Auto-scroll to new messages
- Support message selection and copying
- Expand/collapse execution details
- Handle multi-line input with auto-resize
- Attach files to messages
- Use quick templates
- Execute/stop workflow

## Sidebar Components

### QuickActions (`/components/layout/sidebar/QuickActions.tsx`)
**Purpose**: Fast access to common operations
**Actions**:
- Start new conversation (clear current)
- Open conversation history modal
- Export conversation/workflow

### WorkflowControls (`/components/layout/sidebar/WorkflowControls.tsx`)
**Purpose**: Configure workflow execution parameters
**Controls**:
- **Mode Dropdown**: Select workflow pattern
- **Agent Slider**: Set max agents (1-10)
- **Timeout Input**: Set execution timeout
- **Feature Checkboxes**: Enable/disable features

**Actions**:
- Change workflow mode
- Adjust agent count dynamically
- Set custom timeout values
- Toggle collaboration features
- Enable/disable vector memory
- Show/hide advanced options

### AgentMonitor (`/components/layout/sidebar/AgentMonitor.tsx`)
**Purpose**: Real-time agent status visualization
**Display Elements**:
- Agent type icon and name
- Status indicator (🟢🟡🔴⚫)
- Current activity description
- View details link

**Actions**:
- Auto-update agent status via WebSocket
- Filter agents by status
- Expand for detailed view
- Show agent performance metrics

### ResourceUsage (`/components/layout/sidebar/ResourceUsage.tsx`)
**Purpose**: Monitor system resource consumption
**Metrics**:
- Memory usage (progress bar + percentage)
- Token usage (current/maximum)
- API call count
- Execution timer

**Actions**:
- Real-time metric updates
- Color-coded warnings (green/yellow/red)
- Hover for detailed breakdowns
- Reset counters on new conversation

## Conversation Components

### MessageList (`/components/layout/conversation/MessageList.tsx`)
**Purpose**: Display conversation history
**Message Types**:
- User messages
- AI responses
- System notifications
- Error messages

**Actions**:
- Render messages with sender identification
- Display timestamps (relative/absolute)
- Show execution steps in collapsible panels
- Highlight artifacts as clickable buttons
- Support markdown rendering
- Enable text selection and copying
- Virtual scrolling for long conversations

### Message (`/components/layout/conversation/Message.tsx`)
**Purpose**: Individual message rendering
**Elements**:
- Sender avatar/icon
- Message content
- Timestamp
- Action buttons
- Execution details (AI messages)

**Actions**:
- Copy message content
- Expand/collapse details
- Click artifacts to open modal
- Show status indicators
- Display progress animations

### InputArea (`/components/layout/conversation/InputArea.tsx`)
**Purpose**: Message composition and submission
**Controls**:
- Multi-line text area
- Attach file button
- Templates dropdown
- Execute/Stop button

**Actions**:
- Auto-expand text area (3-10 lines)
- Handle file attachments
- Show template menu
- Submit with Ctrl+Enter
- Toggle execute/stop based on state
- Show character/token count
- Display input validation

## Modal Components

### ArtifactModal (`/components/layout/modals/ArtifactModal.tsx`)
**Purpose**: Display and interact with generated artifacts
**Features**:
- Title bar with file info
- Content viewer with syntax highlighting
- Action buttons

**Actions**:
- View artifact content
- Copy to clipboard
- Download file
- Execute scripts (with confirmation)
- Edit inline
- Save as new file
- Close modal (Esc or X)
- Maximize/minimize view

## Utility Components

### StatusIndicator (`/components/ui/StatusIndicator.tsx`)
**Purpose**: Visual status representation
**States**:
- Ready (green)
- Running (pulsing blue)
- Complete (green check)
- Error (red X)
- Warning (yellow triangle)

### ProgressBar (`/components/ui/ProgressBar.tsx`)
**Purpose**: Visual progress indication
**Variants**:
- Determinate (with percentage)
- Indeterminate (animated)
- Segmented (multi-step)

### Tooltip (`/components/ui/Tooltip.tsx`)
**Purpose**: Contextual help and information
**Features**:
- Auto-positioning
- Delay before showing
- Keyboard accessible

## State Management Components

### WorkflowStore (`/stores/workflowStore.ts`)
**Purpose**: Global workflow state management
**State**:
- Current workflow mode
- Agent settings
- Execution status
- Resource metrics

### ConversationStore (`/stores/conversationStore.ts`)
**Purpose**: Conversation data management
**State**:
- Message history
- Current conversation ID
- Artifacts list
- Input draft

### UIStore (`/stores/uiStore.ts`)
**Purpose**: UI preferences and state
**State**:
- Sidebar collapsed state
- Theme selection
- Font size
- Animation preferences

## Real-time Components

### WebSocketProvider (`/components/providers/WebSocketProvider.tsx`)
**Purpose**: WebSocket connection management
**Features**:
- Auto-reconnection
- Message queuing
- Connection status
- Event subscription

### LiveUpdates (`/components/features/LiveUpdates.tsx`)
**Purpose**: Real-time data synchronization
**Updates**:
- Agent status changes
- Execution progress
- Resource metrics
- New messages

## Accessibility Components

### SkipLinks (`/components/a11y/SkipLinks.tsx`)
**Purpose**: Keyboard navigation shortcuts
**Links**:
- Skip to main content
- Skip to sidebar
- Skip to input

### ScreenReaderAnnouncer (`/components/a11y/ScreenReaderAnnouncer.tsx`)
**Purpose**: Dynamic content announcements
**Announcements**:
- Status changes
- New messages
- Error notifications
- Progress updates

## Theme Components

### ThemeProvider (`/components/providers/ThemeProvider.tsx`)
**Purpose**: Theme management and application
**Themes**:
- Light theme
- Dark theme
- Blue (Professional) theme
- High contrast mode

### ThemeToggle (`/components/ui/ThemeToggle.tsx`)
**Purpose**: Theme selection interface
**Actions**:
- Switch between themes
- Preview themes
- Save preference
- Apply system theme

## Analytics Components (Backend-Required)

### AnalyticsDashboard (`/components/features/analytics/AnalyticsDashboard.tsx`)
**Purpose**: Main analytics visualization interface
**Features**:
- Dashboard template selection
- Widget grid layout
- Real-time metric updates via WebSocket
- Export functionality

**Actions**:
- Create/clone dashboards
- Add/remove widgets
- Configure widget settings
- Export dashboard data
- Subscribe to real-time updates

### CollaborationAnalysis (`/components/features/analytics/CollaborationAnalysis.tsx`)
**Purpose**: Visualize agent collaboration patterns
**Displays**:
- Agent interaction network graph
- Collaboration efficiency metrics
- Communication patterns
- Bottleneck identification

### PredictiveInsights (`/components/features/analytics/PredictiveInsights.tsx`)
**Purpose**: Display AI-powered predictions and recommendations
**Features**:
- Workflow success predictions
- Resource usage forecasts
- Optimization recommendations
- Risk assessments

### MetricsViewer (`/components/features/analytics/MetricsViewer.tsx`)
**Purpose**: Real-time metrics visualization
**Metrics**:
- System performance
- Agent performance
- Workflow metrics
- Resource utilization
- Error rates

**Actions**:
- Stream metrics via WebSocket
- Filter by time range
- Aggregate metrics
- Export metric data

### ExportManager (`/components/features/analytics/ExportManager.tsx`)
**Purpose**: Handle data exports in multiple formats
**Formats**:
- PDF reports
- CSV data
- JSON exports
- Excel workbooks
- HTML reports
- Markdown documentation

**Actions**:
- Configure export settings
- Track export progress
- Download completed exports
- Schedule recurring exports

## Conversation Management Components

### ConversationCompactor (`/components/features/conversation/ConversationCompactor.tsx`)
**Purpose**: Manage conversation memory and token usage
**Features**:
- Token usage display
- Compaction strategy selection
- Auto-compact threshold settings
- Context preservation options

**Actions**:
- Trigger manual compaction
- Monitor token usage in real-time
- Configure auto-compact rules
- Preview compaction results

### ConversationHistory (`/components/features/conversation/ConversationHistory.tsx`)
**Purpose**: Browse and manage past conversations
**Features**:
- Conversation list with search
- Filter by date/status
- Conversation preview
- Bulk operations

**Actions**:
- Load previous conversations
- Search conversation content
- Delete conversations
- Export conversation history

### TokenUsageIndicator (`/components/features/conversation/TokenUsageIndicator.tsx`)
**Purpose**: Real-time token usage monitoring
**Display**:
- Current token count
- Maximum token limit
- Usage percentage
- Cost estimation

**Actions**:
- Update via WebSocket
- Show usage trends
- Alert on high usage
- Display breakdown by agent

## Learning System Components

### FeedbackPanel (`/components/features/learning/FeedbackPanel.tsx`)
**Purpose**: Collect user feedback for system improvement
**Types**:
- Task success/failure
- Quality ratings
- Improvement suggestions
- Error reports

**Actions**:
- Submit feedback
- Rate workflow execution
- Provide detailed comments
- View feedback history

### PatternInsights (`/components/features/learning/PatternInsights.tsx`)
**Purpose**: Display learned patterns and optimizations
**Shows**:
- Discovered workflow patterns
- Optimization suggestions
- Performance improvements
- Usage trends

### AdaptiveBehavior (`/components/features/learning/AdaptiveBehavior.tsx`)
**Purpose**: Configure and monitor adaptive system behavior
**Settings**:
- Learning rate
- Adaptation thresholds
- Behavior preferences
- Performance goals

## System Status Components

### OllamaStatus (`/components/features/status/OllamaStatus.tsx`)
**Purpose**: Monitor Ollama LLM connection status
**Display**:
- Connection state
- Model information
- Response time
- Error messages

**Actions**:
- Reconnect to Ollama
- Switch models
- View model details
- Configure connection settings

### SystemHealth (`/components/features/status/SystemHealth.tsx`)
**Purpose**: Overall system health monitoring
**Monitors**:
- API server status
- WebSocket connections
- Database status
- External service availability

### ErrorBoundary (`/components/features/error/ErrorBoundary.tsx`)
**Purpose**: Graceful error handling and recovery
**Features**:
- Error catching
- Fallback UI
- Error reporting
- Recovery actions

**Actions**:
- Display error details
- Report errors to backend
- Attempt recovery
- Reset application state

## Workflow Configuration Components

### WorkflowTemplates (`/components/features/workflow/WorkflowTemplates.tsx`)
**Purpose**: Pre-configured workflow templates
**Categories**:
- Data analysis
- Code generation
- System administration
- Content creation

**Actions**:
- Browse templates
- Preview template details
- Apply template to input
- Customize template parameters

### WorkflowVisualizer (`/components/features/workflow/WorkflowVisualizer.tsx`)
**Purpose**: Visual representation of workflow execution
**Display**:
- Workflow graph
- Execution path
- Agent assignments
- Progress indicators

**Actions**:
- Zoom/pan workflow graph
- Highlight active steps
- Show step details on hover
- Export workflow diagram

---

This comprehensive component structure ensures all backend API endpoints have corresponding frontend components, providing a complete and functional user interface for the Shepherd application.