# 🐑 Shepherd GUI - Professional Desktop Application

A modern, professional desktop application for Shepherd's intelligent workflow orchestration system, built with Next.js, TypeScript, Tailwind CSS, and Tauri.

## 🚀 Features

- **Professional Interface**: Modern conversational UI with 3-panel layout
- **Real-time Collaboration UI**: Live agent monitoring, memory flow visualization, and performance analytics
- **Learning Progress Tracking**: Visual indicators for Phase 8 learning system insights and recommendations
- **Communication Flow Visualization**: Real-time agent-to-agent messaging and network topology
- **Performance Monitoring**: System resource monitoring, workflow execution tracking, and agent efficiency metrics
- **Terminal-Inspired Theme**: Clean design based on developer tools aesthetics
- **Cross-Platform Desktop**: Native desktop app via Tauri (Windows, macOS, Linux)
- **Responsive Design**: Works seamlessly across all screen sizes
- **Real-Time Communication**: WebSocket integration for live updates
- **Type-Safe**: Full TypeScript implementation with strict type checking
- **State Management**: Zustand for clean, performant state management
- **Theme System**: Light, Dark, and Blue themes with persistence

## 🛠️ Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript 5** - Type-safe JavaScript
- **Tailwind CSS 4** - Utility-first CSS framework
- **Shadcn/ui** - High-quality React components
- **Zustand** - Simple state management
- **Lucide React** - Beautiful icons

### Desktop Integration
- **Tauri 2** - Rust-based desktop app framework (~10MB bundle size)
- **Native APIs** - File system, shell commands, notifications

### Backend Integration
- **FastAPI** - Integration with Python Shepherd orchestrator
- **WebSocket** - Real-time communication
- **REST API** - HTTP-based communication

## 📦 Installation

### Prerequisites
- **Node.js 18+** - JavaScript runtime
- **Rust 1.60+** - For Tauri desktop compilation
- **Python 3.9+** - For Shepherd backend (from parent directory)

### Development Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```
   This starts Next.js at http://localhost:3000

3. **Start desktop app** (optional)
   ```bash
   npm run tauri:dev
   ```
   This opens the native desktop application

### Backend Connection

The GUI expects the Shepherd Python backend to be running on `http://localhost:8000`. To start the backend:

```bash
# From the parent directory
cd ../
./scripts/start.sh --api
```

Or set a custom backend URL:
```bash
export NEXT_PUBLIC_API_URL=http://your-backend:8000
npm run dev
```

## 🏗️ Project Structure

```
shepherd-gui/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main page
│   ├── components/          # React components
│   │   ├── ui/              # Base UI components (Shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx    # Badge component (Phase 9)
│   │   │   └── progress.tsx # Progress component (Phase 9)
│   │   ├── features/        # Phase 9 collaboration UI components
│   │   │   ├── agents/      # Agent visualization components
│   │   │   │   ├── agent-status.tsx
│   │   │   │   ├── agent-collaboration.tsx
│   │   │   │   └── communication-flow.tsx
│   │   │   ├── memory/      # Memory flow visualization
│   │   │   │   └── memory-flow.tsx
│   │   │   ├── learning/    # Learning progress indicators
│   │   │   │   └── learning-progress.tsx
│   │   │   └── performance/ # Performance metrics dashboard
│   │   │       └── metrics-dashboard.tsx
│   │   └── layout/          # Layout components
│   │       ├── sidebar.tsx
│   │       ├── conversation-area.tsx
│   │       └── artifacts-panel.tsx
│   ├── lib/                 # Utilities and configurations
│   │   ├── utils.ts         # Utility functions
│   │   ├── types.ts         # TypeScript types
│   │   ├── api.ts           # Backend API integration
│   │   └── learning-api.ts  # Phase 8 learning system API client
│   ├── stores/              # State management
│   │   └── chat-store.ts    # Chat state with Zustand
│   └── styles/              # Global styles
│       └── globals.css      # Tailwind + custom CSS
├── src-tauri/               # Tauri desktop configuration
│   ├── src/
│   │   └── main.rs          # Rust main file
│   ├── Cargo.toml           # Rust dependencies
│   └── tauri.conf.json      # Tauri configuration
├── public/                  # Static assets
├── package.json             # Node.js dependencies
└── tailwind.config.js       # Tailwind configuration
```

## 🎨 Theme System

The application includes three carefully designed themes based on terminal aesthetics:

### Light Theme (Terminal Day)
- Clean white backgrounds
- Dark text for readability
- Blue accents for actions

### Dark Theme (Terminal Night)
- Deep terminal black backgrounds
- Light text on dark surfaces
- Enhanced blue accents for visibility

### Blue Theme (Guided Mode)
- Professional blue-gray palette
- Warmer blues emphasizing guidance
- Optimized for extended use

Switch themes via the Settings panel in the sidebar.

## 🔧 Development Commands

```bash
# Development
npm run dev          # Start Next.js dev server
npm run tauri:dev    # Start desktop app in dev mode

# Building
npm run build        # Build Next.js app
npm run tauri:build  # Build desktop app for distribution

# Linting and Type Checking
npm run lint         # Run ESLint
npx tsc --noEmit     # Type checking
```

## 🖥️ Desktop Application

### Building for Production

1. **Build the frontend**
   ```bash
   npm run build
   ```

2. **Build desktop app**
   ```bash
   npm run tauri:build
   ```

The built application will be in `src-tauri/target/release/`.

### Desktop Features
- **Native Window Controls** - Standard minimize, maximize, close
- **System Integration** - File associations, notifications
- **Secure by Default** - Minimal permissions, sandboxed execution
- **Auto-Updates** - Built-in update mechanism
- **Small Bundle Size** - ~10-15MB (vs Electron's ~100MB)

## 🌐 Web Deployment

For web-only deployment without desktop features:

```bash
npm run build
npm start
```

Or deploy to platforms like Vercel, Netlify, or any static hosting:

```bash
npm run build
# Upload the 'out' directory to your hosting provider
```

## 🔌 API Integration

The application communicates with the Shepherd Python backend via:

### REST Endpoints
- `POST /api/chat/send` - Send message and get workflow result
- `POST /api/analyze` - Analyze prompt without execution

### WebSocket
- `WS /ws` - Real-time updates during workflow execution

### Mock Mode
When the backend is unavailable, the app automatically falls back to mock responses for development and testing.

## 🎯 Key Components

### Sidebar
- **Chat Management** - Create, switch between conversations
- **Artifact Browser** - Quick access to generated files
- **Settings Panel** - Theme selection, preferences

### Conversation Area
- **Message History** - Clean chat-style interface
- **Rich Content** - Code blocks, progress indicators, metrics
- **Artifact Links** - Clickable buttons to open generated files
- **Multi-line Input** - Support for complex requests

### Artifacts Panel
- **Code Viewer** - Syntax highlighting, line numbers
- **File Actions** - Copy, download, execute, edit
- **Command Output** - Terminal-style execution results
- **Multiple Formats** - Python, JSON, Markdown, Shell scripts

## 🔒 Security

- **Content Security Policy** - Strict CSP for web security
- **Secure Commands** - Sandboxed execution via Tauri
- **Input Validation** - Client and server-side validation
- **Local Storage Only** - No external data transmission

## 🚦 Development Status

### ✅ Completed
- [x] Modern Next.js + TypeScript + Tailwind setup
- [x] Professional UI components with terminal theme
- [x] Three-panel responsive layout
- [x] Zustand state management
- [x] Tauri desktop integration
- [x] API integration layer with fallback
- [x] Theme system with persistence
- [x] Phase 9 collaboration UI components (agent status, memory flow, learning progress)
- [x] Real-time performance monitoring and metrics dashboard
- [x] Complete Phase 8 learning system API integration

### 🚧 In Progress
- [x] WebSocket real-time updates (completed in Phase 9)
- [ ] File upload/download functionality
- [ ] Advanced keyboard shortcuts
- [ ] Offline mode support

### 🔮 Planned
- [ ] Multi-window support
- [ ] Plugin system for custom components
- [ ] Advanced code editor integration
- [ ] Mobile responsive improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper TypeScript types
4. Test both web and desktop modes
5. Submit a pull request

## 📄 License

[Same as parent Shepherd project]

---

**Shepherd GUI** - *Professional desktop interface for intelligent workflow orchestration* 🐑