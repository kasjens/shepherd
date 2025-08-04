# 🐑 Shepherd - Scripts & Tools Documentation

This document describes all the helper scripts and tools created for the Shepherd project, organized by category.

## 📁 **Project Structure**

```
shepherd/
├── scripts/           # Installation and startup scripts
├── api/              # FastAPI backend server
├── shepherd-gui/     # Modern TypeScript GUI with Tauri
├── tools/            # Development and analysis tools
├── src/              # Main application source code
├── main.py           # CLI entry point
└── requirements.txt  # Python dependencies
```

---

## 📂 **scripts/** - Installation & Startup

### **`install.sh`** - Comprehensive Installation Script
**Purpose**: Complete system setup and dependency installation

**What it does**:
- Detects OS (Ubuntu/Debian, RedHat/CentOS/Fedora)
- Installs Python 3.9+ and system dependencies
- Installs Node.js 18+ and npm for the GUI
- Installs Rust toolchain for Tauri desktop builds
- Creates Python virtual environment
- Installs all Python packages from requirements.txt
- Installs GUI dependencies (Next.js, TypeScript, Tailwind CSS)
- Installs and configures Ollama (local LLM)
- Downloads default AI models (llama3.1:8b)
- Creates environment configuration (.env)
- Tests installation and provides usage instructions

**Usage**:
```bash
./scripts/install.sh
```

**Features**:
- ✅ **Safe to run multiple times** (idempotent)
- ✅ **Colored output** with progress indicators
- ✅ **Error handling** with helpful messages
- ✅ **Cross-platform** Linux support
- ✅ **Modern stack setup** (Node.js, Rust, Python)

---

### **`start.sh`** - Smart Application Launcher
**Purpose**: Intelligent startup script with multiple modes and error handling

**What it does**:
- Checks all prerequisites (Python, Node.js, Rust, venv, dependencies)
- Activates virtual environment automatically
- Verifies Python dependencies and installs if missing
- Checks Ollama status and starts if needed
- Provides comprehensive logging information
- Supports multiple launch modes with process cleanup

**Launch Modes**:
- `./scripts/start.sh --gui` - **Professional Desktop GUI** (default, recommended)
- `./scripts/start.sh --api` - **FastAPI backend server only**
- `./scripts/start.sh --cli "request"` - **Command-line execution**
- `./scripts/start.sh --cli --interactive` - **Interactive CLI**

**GUI Mode Features**:
- Automatically starts FastAPI backend on port 8000
- Launches Tauri desktop application
- Handles process cleanup and port management 
- Falls back to web version if desktop fails

**Features**:
- ✅ **Smart dependency checking** and auto-installation
- ✅ **Ollama management** (auto-start, model verification)
- ✅ **Process cleanup** (kills existing processes on ports 3000, 8000)
- ✅ **Multiple interfaces** (desktop GUI, API server, CLI)
- ✅ **Comprehensive error handling**
- ✅ **Logging setup** information

---

## 📂 **api/** - Backend Server

### **`main.py`** - FastAPI Backend Server
**Purpose**: REST API server with WebSocket support for the GUI

**What it provides**:
- RESTful API endpoints for chat and workflow execution
- WebSocket support for real-time communication
- CORS support for frontend integration
- Integration with the core Shepherd orchestrator
- API documentation at `/docs` endpoint

**Endpoints**:
- `POST /api/chat/send` - Send messages and execute workflows
- `GET /api/health` - Health check endpoint
- `WS /ws` - WebSocket for real-time updates

**Usage**:
```bash
# Start API server directly
./scripts/start.sh --api

# API available at: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

---

## 📂 **shepherd-gui/** - Modern TypeScript GUI

### **Next.js + Tauri Application**
**Purpose**: Professional desktop application with web fallback

**Technology Stack**:
- **Next.js 15** with App Router
- **TypeScript 5** for type safety
- **Tailwind CSS** for styling
- **Tauri 2** for desktop integration
- **Zustand** for state management
- **Shadcn/ui** for components

**Development Commands**:
```bash
cd shepherd-gui

# Install dependencies
npm install

# Start web version (development)
npm run dev                # http://localhost:3000

# Start desktop app (development)  
npm run tauri:dev         # Native desktop application

# Build for production
npm run build             # Web build
npm run tauri:build       # Desktop app build
```

**GUI Features**:
- ✅ **Three-panel layout** (sidebar, conversation, artifacts)
- ✅ **Resizable panels** with drag handles
- ✅ **Multiple themes** (light, dark, blue) with persistence
- ✅ **Real-time communication** with backend via WebSocket
- ✅ **Cross-platform desktop** apps (Windows, macOS, Linux)
- ✅ **Responsive design** for multiple screen sizes

---

## 📂 **tools/** - Development & Analysis Tools

### **`analyze_logs.py`** - Log Analysis Tool
**Purpose**: Comprehensive log analysis for troubleshooting and monitoring

**What it analyzes**:
- **Error Analysis**: Recent errors with timestamps and context
- **Workflow Performance**: Execution times, success rates, patterns used
- **Agent Performance**: Task completion rates, average durations
- **System Performance**: Overall metrics and trends
- **Search Functionality**: Find specific terms in logs

**Usage Examples**:
```bash
./tools/analyze_logs.py --all                    # Complete analysis
./tools/analyze_logs.py --errors 6               # Errors from last 6 hours
./tools/analyze_logs.py --workflows 20           # Last 20 workflows
./tools/analyze_logs.py --performance            # System performance
./tools/analyze_logs.py --search "timeout"       # Search for terms
./tools/analyze_logs.py --tail 100               # Recent log entries
```

**Log Files Analyzed**:
- `logs/shepherd.log` - Main application log
- `logs/shepherd_errors.log` - Error-only log
- `logs/shepherd_structured.log` - JSON-formatted log
- `logs/shepherd_YYYYMMDD.log` - Daily logs

---

## 🚀 **Quick Start Guide**

### **First Time Setup**:
```bash
# 1. Install everything (Python, Node.js, Rust, dependencies)
./scripts/install.sh

# 2. Start the desktop application (recommended)
./scripts/start.sh --gui
```

### **Daily Usage**:
```bash
# Desktop GUI (recommended) - starts backend + GUI
./scripts/start.sh --gui

# API server only (for development)
./scripts/start.sh --api

# CLI mode
./scripts/start.sh --cli "Create a todo app"
```

### **Development Workflow**:
```bash
# Terminal 1: Start API backend
./scripts/start.sh --api

# Terminal 2: Start GUI development
cd shepherd-gui && npm run tauri:dev
```

### **Troubleshooting**:
```bash
# Check logs
./tools/analyze_logs.py --all

# Verify all dependencies are installed
./scripts/install.sh

# Check system status
./scripts/start.sh --api  # Check if backend starts correctly
```

---

## 🔧 **Architecture Overview**

### **Modern Stack**:
- **Backend**: FastAPI (Python) + CrewAI for orchestration
- **Frontend**: Next.js 15 (TypeScript) + Tailwind CSS
- **Desktop**: Tauri 2 (Rust) for native apps
- **State**: Zustand for client-side state management
- **LLM**: Ollama for local model support

### **Communication Flow**:
1. **GUI** ↔ **FastAPI** (REST + WebSocket)
2. **FastAPI** ↔ **Core Orchestrator** (Python)
3. **Orchestrator** ↔ **CrewAI Agents** (LLM execution)
4. **Agents** ↔ **Ollama** (Local LLM models)

### **Process Management**:
- **Port 8000**: FastAPI backend server
- **Port 3000**: Next.js development server (when in web mode)
- **Desktop App**: Native window via Tauri (no browser)

---

## 📋 **System Requirements**

### **For Users**:
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 8GB+ RAM (for local LLM)
- **Storage**: 20GB+ free space (for models)
- **Network**: Internet connection for installation

### **For Developers**:
- **Python**: 3.9+ with pip
- **Node.js**: 18+ with npm
- **Rust**: 1.60+ (for Tauri builds)
- **Ollama**: Latest version for LLM support

### **Auto-Installed Dependencies**:
- **Python packages**: FastAPI, CrewAI, Pydantic, etc.
- **Node.js packages**: Next.js, TypeScript, Tailwind CSS, etc.
- **Ollama models**: llama3.1:8b (default)

---

## 🔄 **Migration from Old System**

### **What Changed**:
- ❌ **Removed**: Gradio web interface (`app.py`)
- ❌ **Removed**: Desktop wrapper scripts (`desktop/` directory)
- ❌ **Removed**: Old start modes (`--web`, `--desktop`, `--native-app`)

### **What's New**:
- ✅ **Added**: FastAPI backend (`api/main.py`)
- ✅ **Added**: Professional TypeScript GUI (`shepherd-gui/`)
- ✅ **Added**: Tauri desktop integration
- ✅ **Added**: New start modes (`--gui`, `--api`, `--cli`)

### **Command Migration**:
```bash
# Old commands (deprecated)
./scripts/start.sh --web          # ❌ Removed
./scripts/start.sh --desktop      # ❌ Removed
./scripts/start.sh --native-app   # ❌ Removed

# New commands (current)
./scripts/start.sh --gui          # ✅ Desktop GUI (recommended)
./scripts/start.sh --api          # ✅ API server only
./scripts/start.sh --cli          # ✅ CLI mode (unchanged)
```

---

This new architecture provides:
- **Better Performance**: Native desktop app vs browser wrapper
- **Modern UX**: Professional React interface vs Gradio limitations
- **Type Safety**: Full TypeScript stack vs untyped Python
- **Cross-Platform**: Single codebase for all platforms
- **Maintainability**: Clean separation between backend and frontend
- **Extensibility**: Modern React ecosystem for future features

The scripts maintain the same ease-of-use while supporting a much more powerful and professional application stack.