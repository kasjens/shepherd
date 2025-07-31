# 🐑 Shepherd - Intelligent Workflow Orchestrator

**By InfraWorks.io**

*"Your intelligent workflow shepherd - guiding and protecting your digital operations"*

## Overview

Shepherd is an intelligent multi-agent system that automatically determines the optimal workflow pattern and orchestration strategy based on natural language user requests. It analyzes your requests, selects the best execution approach, creates specialized AI agents, and coordinates their work to accomplish complex tasks.

### Key Features

- 🧠 **Intelligent Prompt Analysis** - Automatically analyzes complexity, urgency, and task requirements
- 🔀 **Dynamic Workflow Selection** - Chooses optimal patterns (Sequential, Parallel, Conditional, etc.)
- 🤖 **Multi-Agent Orchestration** - Creates and coordinates specialized AI agents
- 🖥️ **Multiple Interfaces** - Web UI, desktop app, and command-line modes
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
- Create a virtual environment
- Install all Python packages
- Install and configure Ollama (local LLM)
- Download default AI models
- Set up environment configuration

### 2. Running the Application

#### Native Desktop App (Recommended)
```bash
./scripts/start.sh --native-app
```
Opens Shepherd as a true desktop application (Chrome app mode or native webview).

#### Web Interface
```bash
./scripts/start.sh
```
Starts a web server accessible at http://localhost:7860

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
├── src/                          # Source code  
│   ├── core/                     # Core orchestration logic
│   │   ├── models.py            # Data models and enums
│   │   ├── prompt_analyzer.py   # Natural language analysis
│   │   ├── workflow_selector.py # Pattern selection logic
│   │   └── orchestrator.py      # Main coordination engine
│   ├── agents/                   # AI agent system
│   │   ├── base_agent.py         # Agent base class
│   │   ├── task_agent.py         # Specialized task agents
│   │   └── agent_factory.py      # Agent creation logic
│   ├── workflows/                # Workflow implementations
│   │   ├── base_workflow.py      # Workflow base class
│   │   ├── sequential_workflow.py # Sequential execution
│   │   └── parallel_workflow.py   # Parallel execution
│   └── utils/                    # Utilities and logging
│       └── logger.py            # Comprehensive logging system
├── scripts/                      # Installation and startup scripts
│   ├── install.sh               # Comprehensive installation
│   └── start.sh                 # Smart multi-mode launcher
├── desktop/                      # Desktop application launchers
│   ├── desktop_app.py           # Native webview desktop app
│   ├── app_mode.py             # Chrome app mode launcher
│   └── setup_desktop.sh        # Desktop dependencies installer
├── tools/                        # Development and analysis tools
│   ├── analyze_logs.py          # Log analysis and troubleshooting
│   └── test_app_mode.py         # Desktop compatibility tester
├── logs/                         # Application logs (auto-created)
├── app.py                        # Gradio web interface
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
└── SCRIPTS.md                    # Scripts documentation
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

# Safety Configuration
MAX_EXECUTION_TIME=300
SANDBOX_MODE=True
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

### Running Tests
```bash
source venv/bin/activate
pytest
```

### Code Formatting
```bash
source venv/bin/activate
black src/ tests/
```

### Type Checking
```bash
source venv/bin/activate
mypy src/
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
- Basic prompt analysis engine
- Simple workflow pattern detection (Sequential & Parallel)
- Sequential and parallel workflow execution
- Basic agent creation and task assignment
- Gradio web interface
- Desktop app mode
- Comprehensive installation system
- **Advanced logging system with rotation and analysis tools**

### 🚧 Phase 2 (Next Steps)
- Interactive confirmation system
- Risk assessment and validation
- Backup and rollback capabilities
- Real-time execution monitoring
- Enhanced error handling and recovery

### 🔮 Future Phases
- **Phase 3**: Advanced workflow patterns (Conditional, Iterative, Hierarchical)
- **Phase 4**: Learning from user feedback and workflow optimization
- **Phase 5**: Enterprise features (multi-user, audit logging, API)

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

# Verify installation
python -c "import gradio, crewai, pydantic; print('All imports successful')"
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

## Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent orchestration
- [Gradio](https://gradio.app/) for the web interface
- [Ollama](https://ollama.com/) for local LLM support
- Inspired by the need for intelligent workflow automation

---

**Shepherd** - *Guiding your digital operations with intelligence and care* 🐑