# 🐑 Shepherd - GUI Layout Specification

**By InfraWorks.io**

*Modern Conversational Interface for Intelligent Workflow Orchestration*

---

## Overview

This document describes the GUI layout for Shepherd's conversational interface, designed to provide an intuitive chat-based experience for workflow orchestration with support for multi-context conversations, artifact management, and real-time output visualization.

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 🐑 Shepherd - Intelligent Workflow Orchestrator              [- □ ✕] │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│ ┌─────────────┐ ┌───────────────────────────────────────┐ ┌─────────────────────┐ │
│ │             │ │                                       │ │                     │ │
│ │  SIDEBAR    │ │         CONVERSATION AREA             │ │    ARTIFACTS PANEL  │ │
│ │             │ │                                       │ │                     │ │
│ │ [Collapsible│ │                                       │ │   [Context-aware    │ │
│ │   280px]    │ │            [Flexible]                 │ │     350px]          │ │
│ │             │ │                                       │ │                     │ │
│ │             │ │                                       │ │                     │ │
│ └─────────────┘ └───────────────────────────────────────┘ └─────────────────────┘ │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Sidebar (Left Panel) - 280px Width

### 1.1 Header Section
```
┌─────────────────────────────────┐
│ 🐑 Shepherd                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [+ New Chat]            [≡]    │
└─────────────────────────────────┘
```

**Components:**
- **Logo & Title**: "🐑 Shepherd" with brand styling
- **New Chat Button**: Primary button to create new conversation
- **Collapse Button**: Three-line hamburger menu to collapse sidebar

### 1.2 Chat List Section
```
┌─────────────────────────────────┐
│ 📋 CONVERSATIONS                │
│ ─────────────────────────────── │
│ 🔵 Server Performance Analysis  │
│    └─ 2 artifacts • 15m ago    │
│                                 │
│ ⚪ React Authentication Setup   │
│    └─ 1 artifact • 1h ago      │
│                                 │
│ ⚪ Database Optimization        │
│    └─ 3 artifacts • 2h ago     │
│                                 │
│ [Show more...]                  │
└─────────────────────────────────┘
```

**Features:**
- **Active Chat Indicator**: Blue dot for current conversation
- **Chat Titles**: Auto-generated or user-renamed
- **Metadata**: Artifact count and last activity timestamp
- **Context Switching**: Click to switch between conversations
- **Search Bar**: Quick filter for chat history

### 1.3 Artifacts Section
```
┌─────────────────────────────────┐
│ 📦 ARTIFACTS                    │
│ ─────────────────────────────── │
│ 🔧 system_analysis.py          │
│    └─ Python Script • 12m ago  │
│                                 │
│ 📊 performance_report.md        │
│    └─ Report • 15m ago          │
│                                 │
│ 🐚 optimize_services.sh         │
│    └─ Shell Script • 18m ago    │
│                                 │
│ [View all artifacts...]         │
└─────────────────────────────────┘
```

**Features:**
- **Artifact Types**: Code, scripts, reports, diagrams, configs
- **File Icons**: Visual indicators for different file types
- **Quick Access**: Click to open artifact in right panel
- **Cross-Chat Artifacts**: Artifacts from all conversations

### 1.4 Footer Section
```
┌─────────────────────────────────┐
│ ⚙️  Settings                    │
│ 🔗  Integrations                │
│ ❓  Help & Documentation        │
│ ─────────────────────────────── │
│ Status: ● Connected to Ollama   │
└─────────────────────────────────┘
```

**Components:**
- **Settings**: Configuration, themes, preferences
- **Integrations**: External tool connections
- **Help**: Documentation and support
- **Status Indicator**: LLM connection status

---

## 2. Conversation Area (Center Panel) - Flexible Width

### 2.1 Chat Header
```
┌─────────────────────────────────────────────────────────────────┐
│ Server Performance Analysis                    [📋] [🔄] [⚙️]   │
│ Started 25 minutes ago • 3 messages • 2 artifacts generated    │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Chat Title**: Editable conversation name
- **Actions**: Copy conversation, refresh, settings
- **Metadata**: Start time, message count, artifact count

### 2.2 Message History
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│ 👤 You • 25m ago                                               │
│ Fix performance issues in my server and optimize running       │
│ services                                                        │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ 🐑 Shepherd • 24m ago                                          │
│ I'll help you analyze and optimize your server performance.    │
│ Let me start by examining your system metrics and running      │
│ services.                                                       │
│                                                                 │
│ 🔄 Analyzing system performance...                             │
│ ┌─ CPU Usage: 45%                                              │
│ ┌─ Memory: 78% (6.2GB/8GB used)                                │
│ ┌─ Disk: 62% used                                              │
│ └─ Services: 127 running                                       │
│                                                                 │
│ Based on the analysis, I've identified optimization            │
│ opportunities. I've created a system analysis script and       │
│ performance report for you.                                     │
│                                                                 │
│ [📦 system_analysis.py] [📊 performance_report.md]            │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ 👤 You • 20m ago                                               │
│ Can you also check what's using the most memory?               │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ 🐑 Shepherd • 19m ago                                          │
│ Let me analyze the memory usage by process...                  │
│                                                                 │
│ 🔄 Memory analysis in progress...                              │
│                                                                 │
│ Top memory consumers:                                           │
│ ┌─ postgres: 1.2GB (15%)                                       │
│ ┌─ chrome: 0.8GB (10%)                                         │
│ ┌─ java: 0.6GB (7.5%)                                          │
│ └─ [View full analysis in artifact]                            │
│                                                                 │
│ [📊 memory_analysis.json]                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Message Bubbles**: Clear sender identification (User/AI)
- **Timestamps**: Relative time display
- **Rich Content**: Inline progress indicators, metrics, tables
- **Artifact Links**: Clickable buttons to open artifacts
- **Status Indicators**: Real-time execution progress
- **Auto-scroll**: New messages automatically scroll into view

### 2.3 Input Area
```
┌─────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Type your message...                                        │ │
│ │                                                             │ │
│ │                                                             │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ Now optimize the database queries for better           │ │ │
│ │ │ performance and create a maintenance script             │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ [📎] [🎯] [⚡]                                          [Send] │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Multi-line Input**: Expandable text area (3-8 lines)
- **Rich Text Support**: Markdown formatting
- **Attachments**: File upload capability
- **Quick Actions**: Template suggestions, workflow shortcuts
- **Auto-complete**: Smart suggestions based on context
- **Send Button**: Primary action (Ctrl+Enter also works)

---

## 3. Artifacts Panel (Right Panel) - 350px Width

### 3.1 Panel Header
```
┌─────────────────────────────────────────────┐
│ 📦 Artifacts              [🔍] [📥] [✕]    │
│ ─────────────────────────────────────────── │
│ [Code] [Scripts] [Reports] [Diagrams]       │
└─────────────────────────────────────────────┘
```

**Components:**
- **Title**: "Artifacts" with count indicator
- **Actions**: Search, download all, close panel
- **Filter Tabs**: Category-based filtering

### 3.2 Artifact Viewer
```
┌─────────────────────────────────────────────┐
│ 🔧 system_analysis.py          [📋] [📥]   │
│ ─────────────────────────────────────────── │
│ ```python                                   │
│ #!/usr/bin/env python3                      │
│ import psutil                               │
│ import json                                 │
│                                             │
│ def analyze_system():                       │
│     """Analyze system performance."""       │
│     cpu_percent = psutil.cpu_percent(1)     │
│     memory = psutil.virtual_memory()        │
│     disk = psutil.disk_usage('/')          │
│                                             │
│     return {                                │
│         'cpu': cpu_percent,                 │
│         'memory': {                         │
│             'percent': memory.percent,      │
│             'available': memory.available   │
│         },                                  │
│         'disk': {                           │
│             'percent': disk.percent,        │
│             'free': disk.free               │
│         }                                   │
│     }                                       │
│                                             │
│ if __name__ == '__main__':                  │
│     result = analyze_system()               │
│     print(json.dumps(result, indent=2))     │
│ ```                                         │
│                                             │
│ ─────────────────────────────────────────── │
│ Language: Python • 45 lines • Created 12m  │
│ [Run Script] [Edit] [Save As...]            │
└─────────────────────────────────────────────┘
```

### 3.3 Command Output Viewer
```
┌─────────────────────────────────────────────┐
│ 🖥️  Command Output           [📋] [🔄]     │
│ ─────────────────────────────────────────── │
│ $ python system_analysis.py                 │
│                                             │
│ {                                           │
│   "cpu": 45.2,                             │
│   "memory": {                              │
│     "percent": 78.4,                       │
│     "available": 1843200000                │
│   },                                        │
│   "disk": {                                │
│     "percent": 62.1,                       │
│     "free": 45231616000                    │
│   }                                         │
│ }                                           │
│                                             │
│ ✅ Executed successfully in 0.8s            │
│                                             │
│ ─────────────────────────────────────────── │
│ [Save Output] [Run Again] [Clear]           │
└─────────────────────────────────────────────┘
```

### 3.4 Artifact Types Support

**Code Files:**
- Syntax highlighting for 50+ languages
- Line numbers and folding
- Copy to clipboard functionality
- Direct execution for scripts

**Reports & Documentation:**
- Markdown rendering
- PDF preview
- Export options
- Print support

**Diagrams:**
- SVG/PNG image display
- Zoom and pan controls
- Export functionality
- Inline editing for text diagrams

**Configuration Files:**
- YAML/JSON/XML formatting
- Validation indicators
- Apply/deploy buttons
- Diff view for changes

---

## 4. Responsive Design & Interactions

### 4.1 Responsive Breakpoints

**Desktop (1200px+):**
- Full three-panel layout
- Sidebar: 280px, Artifacts: 350px
- Conversation area gets remaining space

**Tablet (768px - 1199px):**
- Collapsible panels default to closed
- Artifacts panel becomes overlay
- Touch-friendly controls

**Mobile (< 768px):**
- Single-panel view with tab navigation
- Full-screen conversation mode
- Slide-out panels for sidebar/artifacts

### 4.2 Keyboard Shortcuts

```
Ctrl + N        New chat
Ctrl + K        Focus search
Ctrl + Enter    Send message
Ctrl + /        Toggle sidebar
Ctrl + .        Toggle artifacts panel
Ctrl + 1-9      Switch between recent chats
Esc             Close overlays/panels
```

### 4.3 Drag & Drop Support

- **Files to Input**: Attach files to conversation
- **Artifacts to Filesystem**: Save artifacts directly
- **Panel Resizing**: Adjust panel widths
- **Message Reorganization**: Reorder conversation history

---

## 5. Theme & Visual Design

### 5.1 Color Scheme

**Light Theme:**
```
Background:     #FFFFFF
Panel BG:       #F8F9FA
Borders:        #E9ECEF
Text Primary:   #212529
Text Secondary: #6C757D
Accent:         #0D6EFD
Success:        #198754
Warning:        #FFC107
Error:          #DC3545
```

**Dark Theme:**
```
Background:     #1A1D21
Panel BG:       #212529
Borders:        #495057
Text Primary:   #F8F9FA
Text Secondary: #ADB5BD
Accent:         #0D6EFD
Success:        #198754
Warning:        #FFC107
Error:          #DC3545
```

### 5.2 Typography

```
Headers:     Inter, -apple-system, sans-serif
Body:        Inter, -apple-system, sans-serif
Code:        'JetBrains Mono', 'Monaco', monospace
```

### 5.3 Animations

- **Panel Transitions**: 300ms ease-in-out
- **Message Appearance**: Fade in from bottom
- **Artifact Loading**: Skeleton placeholders
- **Status Changes**: Smooth color transitions

---

## 6. Accessibility Features

### 6.1 Keyboard Navigation
- Full keyboard navigation support
- Tab order follows logical flow
- Focus indicators clearly visible
- Screen reader announcements

### 6.2 Screen Reader Support
- Semantic HTML structure
- ARIA labels and descriptions
- Live regions for dynamic content
- Alternative text for images

### 6.3 Visual Accessibility
- High contrast mode support
- Scalable UI elements
- Minimum 14px font sizes
- Clear visual hierarchy

---

## 7. Technical Implementation Notes

### 7.1 Frontend Framework
- **Primary**: React 18+ with TypeScript
- **State Management**: Zustand or Redux Toolkit
- **Styling**: Tailwind CSS + Custom Components
- **Icons**: Lucide React or Heroicons

### 7.2 Real-time Features
- **WebSocket Connection**: For live updates
- **Server-Sent Events**: For streaming responses
- **Optimistic Updates**: Immediate UI feedback
- **Connection Status**: Visual connection indicators

### 7.3 Data Persistence
- **Local Storage**: UI preferences, draft messages
- **Session Storage**: Temporary conversation state
- **IndexedDB**: Offline artifact storage
- **Backend API**: Persistent conversation history

### 7.4 Performance Optimizations
- **Virtual Scrolling**: For long conversations
- **Code Splitting**: Lazy load artifact viewers
- **Image Optimization**: Responsive image loading
- **Caching Strategy**: Intelligent artifact caching

---

## 8. Future Enhancements

### 8.1 Advanced Features
- **Voice Input**: Speech-to-text integration
- **Collaborative Mode**: Multi-user conversations
- **Workflow Templates**: Pre-built conversation starters
- **AI Agents Marketplace**: Custom agent plugins

### 8.2 Integration Capabilities
- **IDE Extensions**: VS Code, IntelliJ plugins
- **Cloud Platforms**: AWS, Azure, GCP integration
- **DevOps Tools**: Jenkins, Docker, Kubernetes
- **Monitoring Systems**: Grafana, Prometheus dashboards

---

This GUI layout provides a modern, intuitive interface for Shepherd's intelligent workflow orchestration, focusing on conversational interaction while maintaining powerful artifact management and visualization capabilities.