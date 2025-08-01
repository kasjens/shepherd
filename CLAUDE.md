# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Application Startup
```bash
# FastAPI backend server (default for new GUI)
./scripts/start.sh --api

# New professional desktop GUI (TypeScript/React)
./scripts/start.sh --gui

# Command line interface
./scripts/start.sh --cli "Create a todo list application"

# Interactive CLI mode
./scripts/start.sh --cli --interactive
```

### Development Commands
```bash
# Setup/Installation
./scripts/install.sh                    # Complete setup (Python, venv, Ollama, models)

# Backend Development
source venv/bin/activate
pytest                                  # Run tests
black src/ tests/                       # Format code
mypy src/                              # Type checking
uvicorn api.main:app --reload           # Start API server directly

# GUI Development (shepherd-gui/)
cd shepherd-gui
npm install                             # Install dependencies
npm run dev                             # Start Next.js dev server
npm run tauri:dev                       # Start desktop app in dev mode
npm run build                           # Build for production
npm run tauri:build                     # Build desktop app

# Log Analysis (Essential for debugging)
./tools/analyze_logs.py --all           # Complete log analysis
./tools/analyze_logs.py --errors 6      # Errors from last 6 hours
./tools/analyze_logs.py --workflows 20  # Last 20 workflow executions
./tools/analyze_logs.py --search "timeout"  # Search logs
```

## Architecture Overview

### Core Orchestration System
Shepherd is an intelligent multi-agent workflow orchestrator built around natural language analysis and dynamic workflow selection. The system follows this execution flow:

1. **Prompt Analysis** (`src/core/prompt_analyzer.py`) - Analyzes natural language requests to extract complexity, urgency, task types, and workflow patterns
2. **Workflow Selection** (`src/core/workflow_selector.py`) - Maps analysis results to optimal execution patterns (Sequential, Parallel, Conditional, etc.)
3. **Agent Creation** (`src/agents/agent_factory.py`) - Creates specialized AI agents based on detected task requirements
4. **Execution** (`src/workflows/`) - Executes workflows with real-time monitoring and error handling

### Key Data Models (`src/core/models.py`)
- `PromptAnalysis`: Results of natural language analysis including complexity scores and recommended patterns
- `ExecutionStep`: Individual task execution units with risk levels and rollback commands
- `WorkflowResult`: Complete execution results with timing, outputs, and error tracking
- `WorkflowPattern`: Enum defining execution patterns (SEQUENTIAL, PARALLEL, CONDITIONAL, etc.)

### Agent System Architecture
The agent system uses a factory pattern with specialized agents:
- **SystemAgent** (`src/agents/system_agent.py`): Real system administration tasks using psutil
- **TaskAgent** (`src/agents/task_agent.py`): General-purpose task execution
- **BaseAgent** (`src/agents/base_agent.py`): Abstract base with common functionality

### Interface Layers
- **FastAPI Backend** (`api/main.py`): RESTful API server with WebSocket support for real-time communication
- **Professional GUI** (`shepherd-gui/`): Modern TypeScript/React interface with desktop support via Tauri
- **CLI Interface** (`main.py`): Command-line execution with interactive confirmation

## Critical Implementation Details

### Logging System
Shepherd uses a comprehensive logging system with multiple output formats:
- `logs/shepherd.log`: Main rotating log (10MB max, 5 backups)
- `logs/shepherd_errors.log`: Error-only log for troubleshooting
- `logs/shepherd_structured.log`: JSON format for programmatic analysis
- `logs/shepherd_YYYYMMDD.log`: Daily logs with 30-day retention

All workflow executions, agent actions, and user interactions are logged with structured metadata for analysis.

### Environment Configuration
The application requires Ollama for LLM functionality and uses environment variables for configuration:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_GENERAL=llama3.1:8b
MAX_EXECUTION_TIME=300
SANDBOX_MODE=True
```

### Real vs Simulated Execution
- **SystemAgent**: Performs real system operations using psutil
- **TaskAgent**: Uses CrewAI for simulated/LLM-based task execution
- The system automatically creates appropriate agents based on task analysis

### Current UI Technology Stack
The project has migrated to a modern professional interface:
- **Backend API**: FastAPI with RESTful endpoints and WebSocket support
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and Shadcn/ui components
- **Desktop Integration**: Tauri 2 for cross-platform native desktop applications
- **State Management**: Zustand for clean, performant client-side state management
- **Theme System**: Three professionally designed themes (Light, Dark, Blue) with persistence

The old Gradio interface has been deprecated in favor of this modern architecture.

## Development Workflow

### Adding New Workflow Patterns
1. Define pattern in `WorkflowPattern` enum in `models.py`
2. Create workflow class inheriting from `BaseWorkflow` in `src/workflows/`
3. Update `WorkflowSelector` to recognize and create the new pattern
4. Add pattern detection logic to `PromptAnalyzer`

### Adding New Agent Types
1. Create agent class inheriting from `BaseAgent` in `src/agents/`
2. Register agent type in `AgentFactory.create_agent()`
3. Add task type mapping in prompt analysis if needed

### Debugging Execution Issues
1. **Check logs first**: `./tools/analyze_logs.py --all`
2. **Verify Python environment**: `source venv/bin/activate` and `python -c "import fastapi, crewai, pydantic"`
3. **Check Ollama status**: `ollama list` and `ollama serve` if needed
4. **Test CLI mode**: `./scripts/start.sh --cli --interactive` for direct debugging
5. **API testing**: Use `./scripts/start.sh --api` and visit `http://localhost:8000/docs`
6. **GUI debugging**: Check browser console and `npm run dev` logs
7. **Desktop app issues**: Try `npm run tauri:dev` for detailed Tauri logs

### API Integration
The new architecture separates concerns between the Python backend and TypeScript frontend:
- **Backend**: Python orchestrator with FastAPI web server providing RESTful endpoints
- **Frontend**: TypeScript GUI consuming API endpoints with real-time WebSocket updates
- **Data Transfer**: JSON serialization with proper handling of Python objects
- **Error Handling**: Comprehensive error responses with structured error information

## Technology Dependencies

### Backend Runtime
- **Python 3.9+** required
- **CrewAI** for multi-agent orchestration
- **FastAPI** for RESTful API server
- **Pydantic 2.0+** for data validation
- **psutil** for real system monitoring and performance analysis

### Frontend Runtime
- **Node.js 18+** for TypeScript/React development
- **Next.js 15** React framework with App Router
- **TypeScript 5** for type-safe development
- **Tailwind CSS 4** for styling
- **Tauri 2** for desktop app compilation (requires Rust 1.60+)

### LLM Integration
- **Ollama** for local LLM support (recommended models: llama3.1:8b, codellama:7b)
- Automatic fallback to simulated responses if Ollama unavailable

The application is designed to gracefully degrade functionality when optional dependencies are missing.

## Project Structure Overview

### Key Directories
```
shepherd/
├── src/                          # Python backend source code
│   ├── core/                     # Core orchestration logic
│   │   ├── models.py            # Data models and enums
│   │   ├── prompt_analyzer.py   # Natural language analysis engine
│   │   ├── workflow_selector.py # Pattern selection logic
│   │   └── orchestrator.py      # Main coordination engine
│   ├── agents/                   # AI agent system
│   │   ├── base_agent.py        # Agent base class
│   │   ├── task_agent.py        # General task agents
│   │   ├── system_agent.py      # System administration agents
│   │   └── agent_factory.py     # Agent creation factory
│   ├── workflows/                # Workflow implementations
│   │   ├── base_workflow.py     # Abstract workflow base
│   │   ├── sequential_workflow.py # Sequential execution
│   │   └── parallel_workflow.py # Parallel execution
│   └── utils/                    # Utilities and logging
│       └── logger.py            # Comprehensive logging system
├── shepherd-gui/                 # Modern TypeScript GUI
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/          # React components
│   │   │   ├── ui/              # Base UI components (Shadcn/ui)
│   │   │   └── layout/          # Layout components
│   │   ├── lib/                 # Utilities and API integration
│   │   ├── stores/              # Zustand state management
│   │   └── styles/              # Tailwind CSS styles
│   ├── src-tauri/               # Desktop app configuration
│   └── package.json             # Node.js dependencies
├── scripts/                      # Installation and startup scripts
│   ├── install.sh               # Comprehensive setup script
│   └── start.sh                 # Multi-mode launcher script
├── tools/                        # Development and analysis tools
│   ├── analyze_logs.py          # Log analysis and troubleshooting
│   └── test_app_mode.py         # Desktop compatibility testing
├── logs/                         # Application logs (auto-created)
├── main.py                       # CLI entry point
└── requirements.txt              # Python dependencies
```

### Missing Components (To Be Implemented)
- **api/** directory: FastAPI backend server (referenced in start.sh but not yet created)
- Advanced workflow patterns (Conditional, Iterative, Hierarchical)
- WebSocket real-time communication implementation
- Interactive confirmation system for high-risk operations

### Current Implementation Status
**✅ Working Components:**
- Core orchestration engine (`src/core/`)
- Agent factory and basic agents (`src/agents/`)
- Sequential and parallel workflows (`src/workflows/`)
- CLI interface (`main.py`)
- Professional GUI foundation (`shepherd-gui/`)
- Comprehensive logging system
- Installation and startup scripts

**🚧 In Development:**
- FastAPI backend integration (referenced but not implemented)
- WebSocket real-time communication
- Advanced workflow patterns

**📋 Architecture Notes for Developers:**
- The project uses a factory pattern for agent creation with extensible registry
- Workflow patterns are implemented as classes inheriting from `BaseWorkflow`
- The system supports both real system operations (SystemAgent) and LLM-based tasks (TaskAgent)
- All execution is logged comprehensively with structured metadata

## Project Documentation Context

### GUI Design Vision
The project has comprehensive GUI design documentation that outlines a modern conversational interface:

- **GUI_LAYOUT.md**: Detailed 3-panel layout specification (sidebar, conversation, artifacts) with responsive design, keyboard shortcuts, and accessibility features. Defines a professional chat-based interface for workflow orchestration.

- **THEME_DESIGN.md**: Complete visual design system based on terminal-inspired aesthetics with clean typography, developer-centric color palette, and three theme variations (light, dark, blue).

- **PROPOSED_GUI_APPROACH.md**: Technical roadmap for migrating from Gradio to a professional TypeScript-based desktop application using Tauri + Next.js for better performance and design freedom.

### Comprehensive Tooling
The project includes extensive tooling documentation:

- **SCRIPTS.md**: Complete reference for all helper scripts including installation (`install.sh`), startup (`start.sh`), desktop launchers, and analysis tools. Each script has comprehensive error handling and user guidance.

- **Desktop Application Variants**: Multiple desktop launch modes including native webview (`desktop_app.py`) and Chrome app mode (`app_mode.py`) with fallback strategies.

### Development Philosophy
The **intelligent_orchestrator_context.md** provides the core development philosophy:

- **Intelligent Workflow AI**: System that analyzes natural language, selects optimal patterns (Sequential, Parallel, Conditional, etc.), creates specialized agents, and orchestrates execution with safety checks.

- **Multi-Agent Architecture**: Dynamic agent creation based on task requirements (Research, Technical, Creative, Security, Monitoring agents).

- **Safety-First Design**: Interactive confirmation, risk assessment, backup/rollback capabilities, and command validation.

- **Specialized Applications**: Focus areas include codebase analysis, Linux system administration, and business intelligence.

### Current Status vs Vision
- **Current**: Modern TypeScript desktop app with FastAPI backend, basic workflow patterns, and comprehensive logging
- **Architecture**: Python backend with CrewAI orchestration + Next.js/Tauri professional GUI
- **Migration Complete**: Successfully transitioned from Gradio to professional TypeScript interface
- **Future**: Advanced workflow patterns (Conditional, Iterative, Hierarchical) and enterprise features