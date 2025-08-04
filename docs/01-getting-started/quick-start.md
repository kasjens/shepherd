# 🚀 Quick Start Guide

Get Shepherd up and running in 5 minutes.

## Prerequisites

- **Python 3.9+** installed on your system
- **Git** for cloning the repository
- **8GB+ RAM** recommended

## 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/shepherd
cd shepherd

# Run the installation script
./scripts/install.sh

# This installs:
# - Python dependencies in virtual environment
# - Node.js and npm for the GUI
# - Ollama for local LLM support
```

## 2. Start Shepherd

```bash
# Start the desktop GUI (recommended)
./scripts/start.sh --gui

# OR start API server only
./scripts/start.sh --api

# OR use CLI mode
./scripts/start.sh --cli "Analyze system performance"
```

## 3. First Workflow

1. **Open the GUI** - The desktop app will launch automatically
2. **Create a new conversation** - Click "New Chat" 
3. **Enter a request**: 
   ```
   Create a todo list for organizing a software project
   ```
4. **Watch the magic** - Agents will collaborate to create your list

## 🎉 Success!

You now have Shepherd running! The system will:
- Analyze your request automatically
- Select the optimal workflow pattern
- Create appropriate agents
- Execute and monitor the workflow
- Provide real-time feedback

## 🔗 Next Steps

- **[Installation Guide](installation.md)** - Detailed setup instructions
- **[Your First Workflow](first-workflow.md)** - In-depth tutorial
- **[User Guides](../02-user-guides/)** - Feature documentation

## ⚡ Quick Commands

```bash
# Check system status
./scripts/start.sh --cli "System status check"

# Run all tests
./scripts/run_tests.sh

# View logs
./tools/analyze_logs.py --recent

# Stop all services
pkill -f "shepherd"
```

---

**Having issues?** Check the [Installation Guide](installation.md) for detailed troubleshooting.