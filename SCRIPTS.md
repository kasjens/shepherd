# 🐑 Shepherd - Scripts & Tools Documentation

This document describes all the helper scripts and tools created for the Shepherd project, organized by category.

## 📁 **Project Structure**

```
shepherd/
├── scripts/           # Installation and startup scripts
├── desktop/          # Desktop application launchers
├── tools/            # Development and analysis tools
├── src/              # Main application source code
├── app.py            # Gradio web interface
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
- Creates Python virtual environment
- Installs all Python packages from requirements.txt
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

---

### **`start.sh`** - Smart Application Launcher
**Purpose**: Intelligent startup script with multiple modes and error handling

**What it does**:
- Checks all prerequisites (Python, venv, dependencies)
- Activates virtual environment automatically
- Verifies Python dependencies and installs if missing
- Checks Ollama status and starts if needed
- Provides comprehensive logging information
- Supports multiple launch modes

**Launch Modes**:
- `./scripts/start.sh` - **Web interface** (default)
- `./scripts/start.sh --desktop` - **Browser-based desktop mode**
- `./scripts/start.sh --native-app` - **True desktop application**
- `./scripts/start.sh --cli "request"` - **Command-line execution**
- `./scripts/start.sh --cli --interactive` - **Interactive CLI**

**Features**:
- ✅ **Smart dependency checking** and auto-installation
- ✅ **Ollama management** (auto-start, model verification)
- ✅ **Multiple interfaces** (web, desktop, CLI)
- ✅ **Comprehensive error handling**
- ✅ **Logging setup** information

---

## 📂 **desktop/** - Desktop Application Launchers

### **`desktop_app.py`** - Native Desktop Application
**Purpose**: True native desktop app using pywebview

**What it does**:
- Creates native desktop window using pywebview
- Starts Gradio server in background (port 7861)
- Provides platform detection (GTK/Qt)
- Falls back to Chrome app mode if native fails
- Handles cleanup and shutdown gracefully

**Features**:
- ✅ **Native window** with OS integration
- ✅ **Platform detection** (GTK/Qt backends)
- ✅ **Automatic fallback** to browser mode
- ✅ **Proper cleanup** and signal handling

**Usage**:
```bash
python desktop/desktop_app.py
```

---

### **`app_mode.py`** - Chrome App Mode Launcher (Recommended)
**Purpose**: Reliable desktop experience using Chrome's app mode

**What it does**:
- Starts Gradio server on port 7862
- Launches Chrome/Chromium in app mode
- Provides desktop-like experience without browser UI
- Handles Chrome process management
- Supports multiple Chrome variants (google-chrome, chromium)

**Chrome App Mode Features**:
- ✅ **No browser UI** (address bar, tabs, bookmarks)
- ✅ **Native window controls** (minimize, maximize, close)
- ✅ **Desktop integration** with custom window class
- ✅ **Reliable cross-platform** support

**Usage**:
```bash
python desktop/app_mode.py
```

---

### **`setup_desktop.sh`** - Desktop Dependencies Installer
**Purpose**: Install system dependencies for native desktop support

**What it does**:
- Detects Linux distribution
- Installs GTK3 and Qt6 system packages
- Installs Python webview with proper backend
- Tests webview installation
- Provides troubleshooting guidance

**Supported Systems**:
- Ubuntu/Debian: `apt install python3-gi gtk3 webkit2gtk qt6-base`
- Fedora/RHEL: `dnf install python3-gobject gtk3-devel qt6-qtbase`
- Arch/Manjaro: `pacman -S python-gobject gtk3 qt6-base`

**Usage**:
```bash
./desktop/setup_desktop.sh
```

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

### **`test_app_mode.py`** - Desktop Mode Compatibility Tester
**Purpose**: Test Chrome/Chromium availability for app mode

**What it does**:
- Checks for Chrome/Chromium installations
- Tests version compatibility
- Verifies app mode support
- Provides installation guidance if missing

**Usage**:
```bash
python tools/test_app_mode.py
```

**Output Example**:
```
✅ Found: google-chrome
   Version: Google Chrome 138.0.7204.168
   App mode will work with: google-chrome --app=<url>
```

---

## 🚀 **Quick Start Guide**

### **First Time Setup**:
```bash
# 1. Install everything
./scripts/install.sh

# 2. Start as desktop app
./scripts/start.sh --native-app
```

### **Daily Usage**:
```bash
# Desktop app (recommended)
./scripts/start.sh --native-app

# Web interface
./scripts/start.sh

# CLI mode
./scripts/start.sh --cli "Create a todo app"
```

### **Troubleshooting**:
```bash
# Check logs
./tools/analyze_logs.py --all

# Test desktop compatibility
python tools/test_app_mode.py

# Setup native desktop support
./desktop/setup_desktop.sh
```

---

## 🔧 **Development Workflow**

### **For Development**:
1. **Use logging** - All actions are logged to `logs/` directory
2. **Analyze performance** - Use `analyze_logs.py` to identify bottlenecks
3. **Test changes** - Multiple interfaces (web, desktop, CLI) for testing
4. **Debug issues** - Structured JSON logs for automated analysis

### **For Deployment**:
1. **Run install.sh** - Sets up complete environment
2. **Use start.sh** - Handles all startup logic and error cases
3. **Monitor logs** - Automated log rotation and analysis tools
4. **Desktop experience** - Native app or Chrome app mode for users

---

## 📋 **Script Dependencies**

### **System Requirements**:
- **Linux** (Ubuntu/Debian/RHEL/Fedora/Arch)
- **Python 3.9+**
- **Bash 4.0+**
- **Internet connection** (for package installation)

### **Optional Dependencies**:
- **Chrome/Chromium** - For app mode (recommended)
- **GTK3/Qt6** - For native desktop (advanced)
- **Ollama** - For local LLM support

### **Auto-Installed**:
- **Python packages** - Via requirements.txt
- **Ollama** - Local LLM runtime
- **AI models** - Default llama3.1:8b

---

This organization provides a clear separation of concerns:
- **scripts/** - System setup and startup
- **desktop/** - Desktop application variants  
- **tools/** - Development and analysis utilities

Each script is self-contained with proper error handling, logging, and user guidance.