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
- **useConversationStore**: Manage chat conversations
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