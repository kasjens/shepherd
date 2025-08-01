# 🐑 Shepherd - Intelligent Workflow Orchestrator

**By InfraWorks.io**

*"Your intelligent workflow shepherd - guiding and protecting your digital operations"*

## Overview

Shepherd is an intelligent multi-agent system that automatically determines the optimal workflow pattern and orchestration strategy based on natural language user requests. It analyzes your requests, selects the best execution approach, creates specialized AI agents, and coordinates their work to accomplish complex tasks.

### Key Features

- 🧠 **Intelligent Prompt Analysis** - Automatically analyzes complexity, urgency, and task requirements
- 🔀 **Dynamic Workflow Selection** - Chooses optimal patterns (Sequential, Parallel, Conditional, etc.)
- 🤖 **Multi-Agent Orchestration** - Creates and coordinates specialized AI agents
- 🖥️ **Multiple Interfaces** - Modern TypeScript desktop GUI with Tauri, FastAPI backend, and command-line modes
- 🛡️ **Safety-First Design** - Built-in validation and error handling
- 🚀 **Local LLM Support** - Works with Ollama for privacy-focused AI

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd shepherd

# Run the comprehensive installation script
./scripts/install.sh
```

The installation script will:
- Install Python 3.9+ and system dependencies
- Install Node.js 18+ and npm for the modern GUI
- Install Rust toolchain for Tauri desktop builds
- Create a virtual environment
- Install all Python packages (FastAPI, CrewAI, etc.)
- Install GUI dependencies (Next.js, TypeScript, Tailwind CSS)
- Install and configure Ollama (local LLM)
- Download default AI models (llama3.1:8b)
- Set up environment configuration

### 2. Running the Application

#### Professional Desktop GUI (Recommended)
```bash
./scripts/start.sh --gui
```
Launches the modern TypeScript/React desktop application with Tauri. This automatically starts both the FastAPI backend and the desktop GUI.

#### API Backend Server
```bash
./scripts/start.sh --api
```
Starts the FastAPI backend server at http://localhost:8000 with documentation at /docs

#### Manual GUI Development
```bash
# Terminal 1: Start backend
./scripts/start.sh --api

# Terminal 2: Start GUI
cd shepherd-gui && npm run tauri:dev  # Desktop app
# OR
cd shepherd-gui && npm run dev        # Web version at localhost:3000
```

#### Command Line Interface
```bash
# Direct execution
./scripts/start.sh --cli "Create a todo list application"

# Interactive mode with step confirmation
./scripts/start.sh --cli --interactive

# Interactive prompt
./scripts/start.sh --cli
```

### 3. Example Requests

Try these natural language requests:

- **Simple Tasks**: "Create a basic todo list application"
- **Data Analysis**: "Analyze sales data and create a report with visualizations"
- **System Admin**: "Check server performance and optimize database queries"
- **Research**: "Research current AI trends and create a presentation"
- **Development**: "Implement user authentication with JWT tokens"

## How It Works

### 1. Prompt Analysis
Shepherd analyzes your natural language request to determine:
- **Complexity Score** (0.0-1.0) - How complex is the task?
- **Urgency Level** - How quickly does it need to be done?
- **Task Types** - What kinds of work are involved? (Research, Technical, Creative, etc.)
- **Dependencies** - Do tasks need to run in sequence?
- **Parallel Potential** - Can work be done simultaneously?

### 2. Workflow Selection
Based on the analysis, Shepherd selects the optimal workflow pattern:
- **Sequential** - Tasks that must run one after another
- **Parallel** - Independent tasks that can run simultaneously
- **Conditional** - Different paths based on conditions
- **Iterative** - Repeated refinement until quality goals are met
- **Hierarchical** - Complex coordination with specialized teams

### 3. Agent Creation
Shepherd creates specialized AI agents based on detected task types:
- **Research Agents** - Information gathering and analysis
- **Technical Agents** - Code implementation and system work  
- **Creative Agents** - Content creation and design
- **Analytical Agents** - Data analysis and insights
- **Communication Agents** - Documentation and reporting

### 4. Execution & Monitoring
The system executes the workflow with:
- Real-time progress tracking
- Error handling and recovery
- Execution time monitoring
- Structured result compilation

## Project Structure

```
shepherd/
├── src/                          # Python source code  
│   ├── core/                     # Core orchestration logic
│   │   ├── models.py            # Data models and enums
│   │   ├── prompt_analyzer.py   # Natural language analysis
│   │   ├── workflow_selector.py # Pattern selection logic
│   │   └── orchestrator.py      # Main coordination engine
│   ├── agents/                   # AI agent system
│   │   ├── base_agent.py         # Agent base class
│   │   ├── task_agent.py         # Specialized task agents
│   │   ├── system_agent.py       # System operations agent
│   │   └── agent_factory.py      # Agent creation logic
│   ├── workflows/                # Workflow implementations
│   │   ├── base_workflow.py      # Workflow base class
│   │   ├── sequential_workflow.py # Sequential execution
│   │   └── parallel_workflow.py   # Parallel execution
│   └── utils/                    # Utilities and logging
│       └── logger.py            # Comprehensive logging system
├── shepherd-gui/                 # Modern TypeScript GUI
│   ├── src/                     # Next.js 15 with App Router
│   │   ├── app/                 # Next.js app pages
│   │   ├── components/          # React components (UI + Layout)
│   │   ├── lib/                 # API integration and utilities  
│   │   ├── stores/              # Zustand state management
│   │   └── styles/              # Tailwind CSS and themes
│   ├── src-tauri/               # Tauri 2 desktop integration
│   ├── package.json             # Node.js dependencies
│   └── tailwind.config.js       # Tailwind CSS configuration
├── api/                          # FastAPI backend server
│   └── main.py                  # REST API with WebSocket support
├── scripts/                      # Installation and startup scripts
│   ├── install.sh               # Comprehensive installation
│   └── start.sh                 # Multi-mode launcher (API/GUI/CLI)
├── tools/                        # Development and analysis tools
│   ├── analyze_logs.py          # Log analysis and troubleshooting
│   └── test_app_mode.py         # Desktop compatibility tester
├── docs/                         # Documentation
│   ├── GUI_LAYOUT.md            # GUI design specification
│   ├── PROPOSED_GUI_APPROACH.md # Architecture decision
│   └── intelligent_orchestrator_context.md # Core concepts
├── logs/                         # Application logs (auto-created)
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
├── CLAUDE.md                     # Guidance for Claude Code
└── MIGRATION_GUIDE.md            # GUI migration documentation
```

## Architecture Deep Dive

### Core Components

#### Prompt Analysis Engine (`src/core/prompt_analyzer.py`)
- Analyzes natural language requests using keyword matching and heuristics
- Extracts complexity, urgency, quality requirements, and task types
- Identifies workflow patterns based on linguistic indicators
- Calculates confidence scores for recommendations

#### Workflow Selector (`src/core/workflow_selector.py`)
- Maps analysis results to optimal workflow patterns
- Provides configuration for each workflow type
- Estimates execution time based on complexity and team size
- Registry system for pluggable workflow implementations

#### Agent Factory (`src/agents/agent_factory.py`)
- Creates specialized agents based on task requirements
- Maps task types to appropriate agent configurations
- Supports extensible agent types through registry pattern
- Handles agent lifecycle and resource management

#### Workflow Implementations (`src/workflows/`)
- **BaseWorkflow**: Abstract base with common functionality
- **SequentialWorkflow**: Executes tasks in order with dependency handling
- **ParallelWorkflow**: Concurrent execution with thread pool management
- Extensible architecture for additional patterns (Conditional, Iterative, etc.)

### Data Models (`src/core/models.py`)

Key data structures:
- **PromptAnalysis**: Results of natural language analysis
- **ExecutionStep**: Individual task execution unit
- **WorkflowResult**: Complete workflow execution results
- **ExecutionStatus**: Task and workflow status tracking

## Configuration

### Environment Variables

Create a `.env` file (copied from `.env.example`):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_GENERAL=llama3.1:8b
OLLAMA_MODEL_CODE=codellama:7b
OLLAMA_MODEL_ANALYSIS=mistral:7b

# API Configuration
SHEPHERD_API_HOST=0.0.0.0
SHEPHERD_API_PORT=8000

# Safety Configuration
MAX_EXECUTION_TIME=300
SANDBO_MODE=True
```

### Ollama Models

Install additional models for specialized tasks:
```bash
# General purpose (recommended)
ollama pull llama3.1:8b

# Code-focused tasks
ollama pull codellama:7b

# Analysis tasks
ollama pull mistral:7b

# Lightweight option
ollama pull llama3.1:7b
```

## Advanced Usage

### Custom Workflow Patterns

Extend Shepherd by implementing new workflow patterns:

```python
from src.workflows.base_workflow import BaseWorkflow

class CustomWorkflow(BaseWorkflow):
    def create_agents(self):
        # Your agent creation logic
        pass
    
    def define_steps(self):
        # Your step definition logic
        pass
    
    def execute(self):
        # Your execution logic
        pass
```

### Custom Agents

Create specialized agents for specific domains:

```python
from src.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def create_crew_agent(self):
        # Your CrewAI agent configuration
        pass
    
    def execute_task(self, task_description):
        # Your task execution logic
        pass
```

## Development

### Python Backend Development
```bash
# Activate environment
source venv/bin/activate

# Run tests
pytest

# Code formatting
black src/ tests/

# Type checking
mypy src/
```

### GUI Development
```bash
# Enter GUI directory
cd shepherd-gui

# Install dependencies
npm install

# Development server (web)
npm run dev

# Development server (desktop)
npm run tauri:dev

# Build for production
npm run build

# Desktop app build
npm run tauri:build
```

## Logging & Troubleshooting

### Comprehensive Logging System

Shepherd includes a sophisticated logging system with rotation for development and troubleshooting:

#### Log Files (in `logs/` directory):
- **`shepherd.log`** - Main application log with rotation (10MB max, 5 backups)
- **`shepherd_errors.log`** - Error-only log for quick issue identification
- **`shepherd_YYYYMMDD.log`** - Daily logs with 30-day retention
- **`shepherd_structured.log`** - JSON-formatted logs for analysis tools

#### Log Analysis Tool

Use the built-in log analyzer for troubleshooting:

```bash
# Complete analysis (recommended)
./tools/analyze_logs.py --all

# Specific analyses
./tools/analyze_logs.py --errors 6          # Errors from last 6 hours
./tools/analyze_logs.py --workflows 20      # Last 20 workflow executions
./tools/analyze_logs.py --agents 50         # Agent performance analysis
./tools/analyze_logs.py --performance       # System performance metrics
./tools/analyze_logs.py --tail 100          # Recent log entries
./tools/analyze_logs.py --search "timeout"  # Search for specific terms
```

#### What Gets Logged:
- **Workflow Execution**: Start/end times, patterns used, success/failure rates
- **Agent Actions**: Task execution, performance metrics, error details
- **User Interactions**: Gradio requests, CLI commands, interaction patterns
- **System Events**: Startup, configuration, resource usage
- **Errors**: Full stack traces, context information, recovery attempts

## Current Status: Phase 1 MVP

### ✅ Completed Features
- Basic prompt analysis engine with natural language processing
- Simple workflow pattern detection (Sequential & Parallel)
- Sequential and parallel workflow execution
- Basic agent creation and task assignment
- **Professional TypeScript/React GUI with Tauri desktop support**
- **FastAPI backend with REST API and WebSocket support**
- **Modern installation system with Node.js and Rust support**
- Advanced logging system with rotation and analysis tools
- System task execution with real performance analysis (SystemAgent)
- **Three-panel responsive GUI with resizable panels and themes**

### 🚧 Phase 2 (In Progress)
- Interactive confirmation system for high-risk operations
- Risk assessment and validation
- Enhanced error handling and recovery
- Advanced workflow patterns (Conditional, Iterative)

### 🔮 Future Phases
- **Phase 3**: Advanced workflow patterns (Conditional, Iterative, Hierarchical)
- **Phase 4**: Learning from user feedback and workflow optimization  
- **Phase 5**: Enterprise features (multi-user, audit logging, advanced API)

## Troubleshooting

### Common Issues

**Python Version Error**
```bash
# Install Python 3.9+ on Ubuntu
sudo apt install python3.9 python3.9-venv python3-pip
```

**Missing Dependencies**
```bash
# Reinstall all dependencies
./scripts/install.sh
```

**Ollama Not Running**
```bash
# Start Ollama manually
ollama serve

# Or restart with the start script
./scripts/start.sh
```

**Import Errors**
```bash
# Activate virtual environment
source venv/bin/activate

# Verify Python dependencies
python -c "import fastapi, uvicorn, crewai, pydantic; print('All imports successful')"

# Verify GUI dependencies
cd shepherd-gui && npm list
```

**GUI Issues**
```bash
# Check Node.js version (requires 18+)
node --version

# Check Rust installation (for desktop builds)
rustc --version

# Reinstall GUI dependencies
cd shepherd-gui && rm -rf node_modules && npm install
```

### Getting Help

- Check the installation logs for detailed error messages
- Ensure all prerequisites are installed (`./scripts/install.sh`)
- Verify virtual environment is activated
- Check Ollama status: `ollama list`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## License

[Add your license information here]

## Technology Stack

### Backend
- [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for API backend
- [Ollama](https://ollama.com/) for local LLM support
- [Pydantic](https://pydantic.dev/) for data validation

### Frontend
- [Next.js 15](https://nextjs.org/) with App Router
- [TypeScript](https://www.typescriptlang.org/) for type safety
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Tauri](https://tauri.app/) for cross-platform desktop apps
- [Zustand](https://zustand-demo.pmnd.rs/) for state management

## Acknowledgments

Inspired by the need for intelligent workflow automation with modern, professional interfaces.

---

**Shepherd** - *Guiding your digital operations with intelligence and care* 🐑