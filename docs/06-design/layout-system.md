# ![Shepherd Logo](/Shepherd.png) Shepherd - GUI Layout Specification

**By InfraWorks.io**

*Simplified Conversational Interface for Intelligent Workflow Orchestration*

---

## Overview

This document describes the simplified GUI layout for Shepherd's conversational interface, designed to provide an intuitive chat-based experience for workflow orchestration with focus on clarity and ease of use. The design features a collapsible left sidebar for controls and a main conversation area as the primary workspace.

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│ [Logo] Shepherd - Intelligent Workflow Orchestrator      [- □ ✕]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┬────────────────────────────────────────────────────┐  │
│ │          │                                                    │  │
│ │ SIDEBAR  │          CONVERSATION AREA (Main)                  │  │
│ │          │                                                    │  │
│ │ [Collap- │                                                    │  │
│ │  sible   │         [Primary Focus - Flexible Width]           │  │
│ │  280px]  │                                                    │  │
│ │          │                                                    │  │
│ └──────────┴────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Left Sidebar (Control Panel) - 280px Width

### 1.1 Header Section
```
┌─────────────────────────────────┐
│ [Logo] Shepherd          [<->] │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
└─────────────────────────────────┘
```

**Components:**
- **Logo & Title**: Shepherd.png logo (24x24px) with "Shepherd" text (collapses to logo only)
- **Collapse/Expand Toggle**: Arrow button to minimize sidebar
- **Implementation**: `<img src="/Shepherd.png" alt="Shepherd" className="w-6 h-6" />`

### 1.2 Quick Actions
```
┌─────────────────────────────────┐
│ 🆕 New Conversation             │
│ 📁 History                      │
│ 💾 Save/Export                  │
└─────────────────────────────────┘
```

**Features:**
- **New Conversation**: Clear current session and start fresh
- **History**: Access and search previous conversations
- **Save/Export**: Export current workflow or conversation

### 1.3 Workflow Controls (Collapsible Section)
```
┌─────────────────────────────────┐
│ ▼ WORKFLOW SETTINGS             │
│ ─────────────────────────────── │
│ Mode: [Auto-Select        ▼]   │
│       • Auto (AI Selects)      │
│       • Sequential              │
│       • Parallel                │
│       • Conditional             │
│       • Hierarchical            │
│                                 │
│ Max Agents: [====----] 5       │
│ Timeout: [300] seconds          │
│                                 │
│ ☑ Enable Agent Collaboration   │
│ ☑ Use Vector Memory            │
│ ☐ Advanced Mode                │
└─────────────────────────────────┘
```

**Features:**
- **Workflow Mode**: Dropdown for workflow pattern selection
- **Agent Settings**: Slider for max agents (1-10)
- **Timeout Configuration**: Input field for execution timeout
- **Feature Toggles**: Checkboxes for optional features

### 1.4 Active Agents Monitor
```
┌─────────────────────────────────┐
│ 👥 ACTIVE AGENTS                │
│ ─────────────────────────────── │
│ 🟢 Research Agent               │
│    └─ Analyzing data...         │
│                                 │
│ 🟡 Task Agent                   │
│    └─ Waiting for input         │
│                                 │
│ ⚫ System Agent                 │
│    └─ Idle                      │
│                                 │
│ [View Details...]               │
└─────────────────────────────────┘
```

**Status Indicators:**
- 🟢 Active (currently executing)
- 🟡 Waiting (queued or paused)
- 🔴 Error (failed or stopped)
- ⚫ Idle (available)

### 1.5 Resource Usage & Token Management
```
┌─────────────────────────────────┐
│ 📊 RESOURCES                    │
│ ─────────────────────────────── │
│ Memory:  [========--] 78%       │
│ Tokens:  2,345 / 10,000 ⚠️      │
│ API:     12 calls               │
│ Time:    00:02:34               │
│                                 │
│ [Auto-compact at 80%] ☑         │
│ [Compact Now]                   │
└─────────────────────────────────┘
```

**Metrics:**
- **Memory Usage**: Progress bar with percentage
- **Token Count**: Current/Maximum with warning indicators
- **API Calls**: Number of external API calls made
- **Execution Time**: Running time counter
- **Token Management**: Auto-compact settings and manual trigger

### 1.6 Footer Section
```
┌─────────────────────────────────┐
│ ⚙️  Settings                    │
│ 📊  Analytics Dashboard         │
│ 📈  Learning Insights           │
│ 💬  Feedback                    │
│ ❓  Help & Documentation        │
│ ─────────────────────────────── │
│ Status: ● Ollama | ● API | ● WS│
└─────────────────────────────────┘
```

**Components:**
- **Settings**: API keys, Ollama configuration, preferences
- **Analytics**: View detailed analytics dashboard (opens modal)
- **Learning Insights**: View patterns and adaptive behavior
- **Feedback**: Submit feedback for improvement
- **Help**: Access documentation and support
- **System Status**: Multi-service status indicators (Ollama, API, WebSocket)

### 1.7 Collapsed State (48px Width)
```
┌────┐
│[L] │  ← Logo only (Shepherd.png)
│────│
│ 🆕 │  ← Icon only buttons
│ 📁 │
│ 💾 │
│────│
│ 🎯 │  ← Workflow indicator
│ 👥 │  ← Agents indicator
│ 📊 │  ← Resources indicator
│────│
│ ⚙️ │
│ 📊 │
│ ❓ │
│────│
│ ● │  ← Status dot
└────┘
```

**Collapsed Features:**
- Icons only, no text labels
- Tooltips on hover for all icons
- Click to expand temporarily for that section
- Visual indicators for active states

---

## 2. Conversation Area (Main Panel) - Flexible Width

### 2.1 Top Bar
```
┌─────────────────────────────────────────────────────────────────┐
│ Current Workflow: Sequential       Status: ● Ready    [⏹ Stop] │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Workflow Type Badge**: Shows current execution pattern
- **Status Indicator**: Ready/Running/Complete/Error
- **Stop Button**: Cancel current execution (visible when running)

### 2.2 Message Display Area
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 👤 You • 2:34 PM                                          │  │
│ │ Analyze my server performance and optimize running        │  │
│ │ services for better resource utilization                  │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ [Logo] Shepherd • 2:34 PM                                 │  │
│ │                                                           │  │
│ │ I'll analyze your server performance and help optimize    │  │
│ │ your services. Let me start by examining system metrics.  │  │
│ │                                                           │  │
│ │ ┌─────────────────────────────────────────────────────┐  │  │
│ │ │ 🔄 Execution Steps:                                  │  │  │
│ │ │ ✅ System analysis initiated                        │  │  │
│ │ │ ✅ CPU usage: 45%                                   │  │  │
│ │ │ ✅ Memory usage: 6.2GB/8GB (78%)                    │  │  │
│ │ │ ⏳ Analyzing running services...                    │  │  │
│ │ └─────────────────────────────────────────────────────┘  │  │
│ │                                                           │  │
│ │ Based on my analysis, here are the findings:             │  │
│ │                                                           │  │
│ │ 📊 Key Metrics:                                          │  │
│ │ • High memory usage by PostgreSQL (1.2GB)                │  │
│ │ • 127 services running (23 can be optimized)             │  │
│ │ • Disk I/O bottleneck detected on /var/log               │  │
│ │                                                           │  │
│ │ 📦 Generated Artifacts:                                  │  │
│ │ [📄 performance_report.md] [🔧 optimize.sh]              │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 👤 You • 2:36 PM                                          │  │
│ │ Run the optimization script                               │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Message Features:**
- **User Messages**: Clear visual distinction with user icon
- **AI Responses**: Shepherd icon with structured output
- **Execution Steps**: Collapsible real-time progress tracking
- **Results Display**: Formatted metrics and findings
- **Artifact Buttons**: Inline clickable artifacts (open in modal)
- **Timestamps**: Relative or absolute time display
- **Status Icons**: ✅ Complete, ⏳ In Progress, ❌ Error

### 2.3 Input Area
```
┌─────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Describe your task or request...                           │ │
│ │                                                             │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ [📎 Attach] [⚡ Templates ▼]                      [▶️ Execute] │
└─────────────────────────────────────────────────────────────────┘
```

**Input Features:**
- **Multi-line Text Area**: Auto-expanding (3-10 lines max)
- **Placeholder Text**: Helpful prompt suggestions
- **Attach Files**: Upload context files
- **Quick Templates**: Dropdown with common tasks
- **Execute Button**: Primary action (changes to ⏹️ Stop when running)
- **Keyboard Shortcut**: Ctrl+Enter to execute

---

## 3. Modal Overlays

### 3.1 Artifact Modal
When artifacts are clicked, they open in a modal overlay:

```
┌─────────────────────────────────────────────────────────────────┐
│ 📦 performance_report.md                          [📋] [📥] [✕] │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ # Server Performance Analysis Report                           │
│                                                                 │
│ ## Executive Summary                                           │
│ Your server is experiencing high memory usage (78%) primarily  │
│ due to database processes and unnecessary services...          │
│                                                                 │
│ ## Detailed Findings                                           │
│ ...                                                            │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│ [Run] [Edit] [Save As...] [Share]                   [Close]   │
└─────────────────────────────────────────────────────────────────┘
```

**Modal Features:**
- **Full-Screen Option**: Maximize for better viewing
- **Syntax Highlighting**: For code files
- **Copy to Clipboard**: Quick copy button
- **Download**: Save artifact locally
- **Execute**: Run scripts directly (with confirmation)
- **Edit Mode**: Modify artifacts inline

### 3.2 Analytics Dashboard Modal
Accessed via sidebar Analytics button:

```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Analytics Dashboard                      [Export] [⚙️] [✕]  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [Overview] [Agents] [Workflows] [Predictions] [Custom]         │
│                                                                 │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│ │ Success Rate  │ │ Avg Duration  │ │ Token Usage   │         │
│ │    87.3%      │ │    2m 34s     │ │   45,234      │         │
│ │ ▲ +5.2%       │ │ ▼ -12s        │ │ ▲ +2,345      │         │
│ └───────────────┘ └───────────────┘ └───────────────┘         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────┐        │
│ │ Workflow Performance (Last 7 Days)                  │        │
│ │ [Line chart showing workflow metrics]               │        │
│ └─────────────────────────────────────────────────────┘        │
│                                                                 │
│ ┌─────────────────────────────────────────────────────┐        │
│ │ Agent Collaboration Network                         │        │
│ │ [Network graph of agent interactions]               │        │
│ └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Conversation History Modal
Accessed via sidebar History button:

```
┌─────────────────────────────────────────────────────────────────┐
│ 📁 Conversation History                    [Search] [Filter] [✕]│
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔵 Server Optimization - 2 hours ago                       │ │
│ │    Analyzed performance, created optimization scripts      │ │
│ │    Tokens: 3,456 | Duration: 2m 15s | 3 artifacts        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ⚪ Database Migration - Yesterday                          │ │
│ │    Created migration scripts for PostgreSQL upgrade        │ │
│ │    Tokens: 5,234 | Duration: 4m 32s | 5 artifacts        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Load More...]                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Settings Modal
Comprehensive settings interface:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ Settings                                              [✕]   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [General] [API] [Appearance] [Workflow] [Advanced]             │
│                                                                 │
│ API Configuration                                               │
│ ─────────────────────────────────────────────────────────────── │
│ Ollama URL:     [http://localhost:11434          ]             │
│ Ollama Model:   [llama3.1:8b                    ▼]             │
│ API Key:        [••••••••••••••••                ]             │
│ Timeout (s):    [300                             ]             │
│                                                                 │
│ Appearance                                                      │
│ ─────────────────────────────────────────────────────────────── │
│ Theme:          (●) Light  ( ) Dark  ( ) Blue                  │
│ Font Size:      [14px                           ▼]             │
│ Animations:     [Enabled                        ▼]             │
│                                                                 │
│ [Save Changes] [Reset to Defaults]                             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 Export Configuration Modal
For data exports:

```
┌─────────────────────────────────────────────────────────────────┐
│ 📥 Export Data                                           [✕]   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ Export Format:                                                  │
│ ( ) PDF Report                                                  │
│ (●) CSV Data                                                    │
│ ( ) JSON                                                        │
│ ( ) Excel Workbook                                             │
│ ( ) HTML Report                                                │
│ ( ) Markdown                                                    │
│                                                                 │
│ Data Range:                                                     │
│ From: [2024-01-01] To: [2024-01-31]                           │
│                                                                 │
│ Include:                                                        │
│ ☑ Conversation History                                         │
│ ☑ Agent Performance Metrics                                    │
│ ☑ Workflow Analytics                                           │
│ ☐ System Logs                                                  │
│                                                                 │
│ [Export] [Cancel]                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Responsive Design

### 4.1 Desktop (1200px+)
- Full layout with expanded sidebar
- Optimal conversation area width
- All features visible

### 4.2 Tablet (768px - 1199px)
- Sidebar starts collapsed
- Touch-friendly controls
- Swipe gestures for sidebar

### 4.3 Mobile (< 768px)
- Sidebar as slide-out drawer
- Full-width conversation area
- Bottom input bar
- Simplified controls

---

## 5. Keyboard Shortcuts

```
Ctrl + N        New conversation
Ctrl + Enter    Execute/Send message
Ctrl + /        Toggle sidebar
Ctrl + K        Quick search/command palette
Ctrl + S        Save conversation
Ctrl + H        Open history
Esc             Close modals/overlays
↑/↓             Navigate message history
```

---

## 6. Theme System

### 6.1 Light Theme
```
Background:      #FFFFFF
Sidebar:         #F8F9FA
Borders:         #E9ECEF
Text Primary:    #212529
Text Secondary:  #6C757D
Accent:          #0066CC
Success:         #10B981
Warning:         #F59E0B
Error:           #EF4444
```

### 6.2 Dark Theme
```
Background:      #0F0F0F
Sidebar:         #1A1A1A
Borders:         #2D2D2D
Text Primary:    #F0F0F0
Text Secondary:  #A0A0A0
Accent:          #3B82F6
Success:         #10B981
Warning:         #F59E0B
Error:           #EF4444
```

### 6.3 Blue Theme (Professional)
```
Background:      #F0F4F8
Sidebar:         #1E3A5F
Borders:         #CBD5E1
Text Primary:    #1A202C
Text Secondary:  #4A5568
Accent:          #2563EB
Success:         #059669
Warning:         #D97706
Error:           #DC2626
```

---

## 7. Animation & Transitions

### 7.1 Sidebar Collapse/Expand
- **Duration**: 200ms ease-out
- **Style**: Smooth width transition
- **Icons**: Rotate arrow indicator

### 7.2 Message Appearance
- **New Messages**: Fade in from bottom (300ms)
- **Loading States**: Pulsing dots animation
- **Progress Updates**: Smooth percentage transitions

### 7.3 Status Changes
- **Color Transitions**: 150ms ease
- **Icon Changes**: Fade transition
- **Progress Bars**: Smooth fill animation

---

## 8. Accessibility

### 8.1 Keyboard Navigation
- Full keyboard support for all interactions
- Clear focus indicators
- Logical tab order
- Skip links for main content

### 8.2 Screen Reader Support
- Semantic HTML structure
- ARIA labels and live regions
- Status announcements
- Role definitions

### 8.3 Visual Accessibility
- High contrast mode support
- Minimum 14px font sizes
- Clear visual hierarchy
- Color-blind friendly indicators

---

## 9. Performance Optimizations

### 9.1 Rendering
- Virtual scrolling for long conversations
- Message pagination (load more on scroll)
- Lazy loading for artifacts
- Debounced input handling

### 9.2 State Management
- Local state for UI controls
- Global state for conversation data
- Persistent storage for preferences
- Optimistic updates for better UX

### 9.3 Network
- WebSocket for real-time updates
- Request batching for efficiency
- Progressive loading for large artifacts
- Offline mode with queue

---

## 10. Implementation Notes

### 10.1 Technology Stack
- **Framework**: Next.js 15 with React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom Components
- **State**: Zustand for state management
- **Desktop**: Tauri for native app
- **Icons**: Lucide React
- **Logo**: Shepherd.png (located at project root, 362KB)

### 10.2 Component Structure
```
src/components/
├── layout/
│   ├── sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── QuickActions.tsx
│   │   ├── WorkflowControls.tsx
│   │   ├── AgentMonitor.tsx
│   │   └── ResourceUsage.tsx
│   ├── conversation/
│   │   ├── ConversationArea.tsx
│   │   ├── MessageList.tsx
│   │   ├── Message.tsx
│   │   └── InputArea.tsx
│   └── modals/
│       └── ArtifactModal.tsx
└── ui/
    └── (shared components)
```

---

This simplified layout focuses on ease of use while maintaining all the powerful features of Shepherd. The collapsible sidebar keeps controls accessible but out of the way, allowing users to focus on their conversation and workflow execution.