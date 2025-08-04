# 🐑 Shepherd - Intelligent Workflow Orchestrator

**By InfraWorks.io**

*"Your intelligent workflow shepherd - guiding and protecting your digital operations"*

## Overview

Shepherd is an intelligent multi-agent system that automatically determines the optimal workflow pattern and orchestration strategy based on natural language user requests. It analyzes your requests, selects the best execution approach, creates specialized AI agents, and coordinates their work to accomplish complex tasks.

### Key Features

- 🧠 **Intelligent Prompt Analysis** - Automatically analyzes complexity, urgency, and task requirements
- 🔀 **Advanced Workflow Patterns** - Conditional branching, iterative refinement, hierarchical delegation
- 🤖 **Multi-Agent Orchestration** - Creates and coordinates specialized AI agents with team structures
- 🔧 **Tool Use Integration** - Execute external tools, APIs, and code for enhanced capabilities
- 🧩 **Semantic Memory System** - Vector-based learning with pattern recognition and failure avoidance
- 🎓 **Learning Systems** - User feedback processing, pattern recognition, and adaptive behavior
- 📊 **Real-time Collaboration UI** - Live agent visualization, memory flow monitoring, and performance analytics
- 📈 **Advanced Analytics** - Agent collaboration analysis, predictive insights, and performance optimization
- 📊 **Custom Dashboards** - User-configurable analytics dashboards with real-time data streaming
- 📤 **Multi-Format Exports** - PDF, CSV, JSON, Excel, HTML, Markdown reports and data analysis
- 💬 **Conversation Compacting** - Unlimited conversation length with intelligent context preservation
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

### 2. Advanced Workflow Selection
Based on the analysis, Shepherd intelligently selects the optimal workflow pattern:
- **Sequential** - Tasks that must run one after another
- **Parallel** - Independent tasks that can run simultaneously  
- **Conditional** - Dynamic branching based on context evaluation and conditions
- **Iterative** - Quality-driven refinement with convergence criteria until standards are met
- **Hierarchical** - Multi-level team coordination with executive management and specialist delegation
- **Hybrid** - Complex scenarios combining multiple patterns

### 3. Agent Creation
Shepherd creates specialized AI agents based on detected task types:
- **Research Agents** - Information gathering and analysis
- **Technical Agents** - Code implementation and system work  
- **Creative Agents** - Content creation and design
- **Analytical Agents** - Data analysis and insights
- **Communication Agents** - Documentation and reporting

### 4. Tool Execution
Agents can execute external tools including:
- **Mathematical calculations and code execution** - Advanced computations and custom scripts
- **Web searches and API calls** - Real-time information gathering and service integration
- **File operations and system interactions** - Data processing and system administration
- **Custom tool integrations** - Domain-specific tools and specialized capabilities

### 5. Execution & Monitoring
The system executes the workflow with:
- Real-time progress tracking
- Tool execution monitoring with timeout handling
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
│   │   ├── base_agent.py         # Agent base class with memory, communication & learning
│   │   ├── task_agent.py         # Specialized task agents
│   │   ├── system_agent.py       # System operations agent
│   │   └── agent_factory.py      # Agent creation logic
│   ├── memory/                   # Three-tier memory system (Phases 2, 5 & 7)
│   │   ├── base.py              # Memory interface and base classes
│   │   ├── local_memory.py      # Agent-local memory with LRU eviction
│   │   ├── shared_context.py    # Shared context pool with pub/sub
│   │   ├── vector_store.py      # Vector-based semantic memory (Phase 7)
│   │   ├── persistent_knowledge.py # Persistent knowledge base (Phase 7)
│   │   ├── conversation_compactor.py # Conversation compacting engine (Phase 5)
│   │   └── context_preservation.py   # Context preservation strategy (Phase 5)
│   ├── communication/            # Agent communication system (Phase 3)
│   │   ├── manager.py           # CommunicationManager with async routing
│   │   ├── protocols.py         # Message protocols and patterns
│   │   └── peer_review.py       # Peer review and consensus mechanisms
│   ├── learning/                 # Learning systems (Phase 8)
│   │   ├── feedback_processor.py # User feedback processing (6 feedback types)
│   │   ├── pattern_learner.py   # Pattern recognition and optimization  
│   │   └── adaptive_system.py   # Adaptive behavior management
│   ├── tools/                    # Tool registry and execution system (Phase 4)
│   │   ├── base_tool.py         # Tool interface and execution framework
│   │   ├── registry.py          # Tool discovery and permissions
│   │   ├── execution_engine.py  # Tool execution with monitoring
│   │   └── core/                # Built-in tool implementations
│   ├── workflows/                # Workflow implementations (Phases 1 & 6)
│   │   ├── base_workflow.py      # Workflow base class
│   │   ├── sequential_workflow.py # Sequential execution
│   │   ├── parallel_workflow.py   # Parallel execution
│   │   ├── conditional_workflow.py # Conditional branching (Phase 6)
│   │   ├── iterative_workflow.py  # Iterative refinement (Phase 6)
│   │   └── hierarchical_workflow.py # Hierarchical delegation (Phase 6)
│   ├── analytics/                # Advanced analytics system (Phase 10)
│   │   ├── collaboration_analyzer.py # Agent interaction pattern analysis
│   │   ├── predictive_engine.py  # ML-based predictions and insights
│   │   ├── metrics_aggregator.py # Performance metrics collection
│   │   ├── dashboard_engine.py   # Custom dashboard management
│   │   └── export_manager.py     # Multi-format data export
│   └── utils/                    # Utilities and logging
│       └── logger.py            # Comprehensive logging system
├── shepherd-gui/                 # Modern TypeScript GUI
│   ├── src/                     # Next.js 15 with App Router
│   │   ├── app/                 # Next.js app pages
│   │   ├── components/          # React components (UI + Layout + Features)
│   │   │   ├── features/        # Phase 9 collaboration UI components
│   │   │   │   ├── agents/      # Agent status & communication visualization
│   │   │   │   ├── memory/      # Memory flow monitoring
│   │   │   │   ├── learning/    # Learning progress indicators
│   │   │   │   └── performance/ # Performance metrics dashboard
│   │   │   ├── layout/          # Layout components (sidebar, conversation area)
│   │   │   └── ui/              # Base UI components (buttons, cards, etc.)
│   │   ├── lib/                 # API integration and utilities
│   │   │   ├── api.ts           # Core API client
│   │   │   └── learning-api.ts  # Phase 8 learning system API client
│   │   ├── stores/              # Zustand state management
│   │   └── styles/              # Tailwind CSS and themes
│   ├── __tests__/               # Frontend test infrastructure (Phase 9)
│   │   ├── components/          # Component tests with mocking
│   │   ├── lib/                 # API client tests
│   │   └── setup.ts             # Test utilities and fixtures
│   ├── src-tauri/               # Tauri 2 desktop integration
│   ├── package.json             # Node.js dependencies
│   └── tailwind.config.js       # Tailwind CSS configuration
├── api/                          # FastAPI backend server
│   ├── main.py                  # REST API with WebSocket support
│   ├── conversation_manager.py  # Conversation compacting API endpoints (Phase 5)
│   └── analytics_manager.py     # Analytics API endpoints (Phase 10)
├── scripts/                      # Installation and startup scripts
│   ├── install.sh               # Comprehensive installation
│   └── start.sh                 # Multi-mode launcher (API/GUI/CLI)
├── tools/                        # Development and analysis tools
│   ├── analyze_logs.py          # Log analysis and troubleshooting
│   └── test_app_mode.py         # Desktop compatibility tester
├── tests/                        # Comprehensive test infrastructure (Phases 1-10)
│   ├── unit/                    # Unit tests (450+ tests total)
│   │   ├── memory/              # Memory system tests (76 tests, Phases 2, 5, 7)
│   │   ├── communication/       # Communication tests (17 tests, Phase 3)  
│   │   ├── tools/               # Tool system tests (20 tests, Phase 4)
│   │   ├── workflows/           # Advanced workflow tests (68 tests, Phase 6)
│   │   ├── learning/            # Learning system tests (75+ tests, Phase 8)
│   │   └── analytics/           # Analytics system tests (110+ tests, Phase 10)
│   ├── integration/             # Integration tests (67+ tests)
│   │   ├── test_memory_integration.py    # Memory system integration
│   │   ├── test_agent_communication.py  # Agent communication integration
│   │   ├── test_basic_tool_integration.py # Tool system integration
│   │   ├── test_conversation_compacting_integration.py # Conversation compacting
│   │   ├── test_advanced_workflows_integration.py # Advanced workflow integration
│   │   ├── test_vector_memory_integration.py # Vector memory integration (Phase 7)
│   │   └── test_learning_systems_integration.py # Learning integration (Phase 8)
│   ├── test_infrastructure.py   # 32 infrastructure validation tests
│   ├── conftest.py              # pytest configuration and fixtures
│   └── fixtures/                # Mock agents and sample data
├── docs/                         # Documentation
│   ├── IMPLEMENTATION_PLAN.md   # Phase-based development plan (Phases 1-9 complete)
│   ├── PHASE1_COMPLETION_REPORT.md # Test infrastructure results
│   ├── PHASE2_COMPLETION_REPORT.md # Memory system implementation
│   ├── PHASE3_COMPLETION_REPORT.md # Agent communication system
│   ├── PHASE4_COMPLETION_REPORT.md # Tool use foundation
│   ├── PHASE5_COMPLETION_REPORT.md # Conversation compacting system
│   ├── PHASE6_COMPLETION_REPORT.md # Advanced workflow patterns
│   ├── PHASE7_COMPLETION_REPORT.md # Vector memory implementation
│   ├── PHASE8_COMPLETION_REPORT.md # Learning systems enhancement
│   ├── PHASE9_COMPLETION_REPORT.md # Frontend collaboration UI
│   ├── AGENT_COLLABORATION.md   # Agent collaboration and memory design
│   ├── GUI_COMPONENTS.md        # Complete GUI component documentation
│   ├── GUI_LAYOUT.md            # 3-panel layout specification
│   └── THEME_DESIGN.md          # Visual design system
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

#### Agent Memory System (`src/memory/`) - Phases 2, 5, 7
- **BaseMemory**: Abstract interface for all memory implementations
- **AgentLocalMemory**: Short-term, task-specific storage with LRU eviction
- **SharedContextPool**: Medium-term collaboration with pub/sub notifications
- **VectorMemoryStore**: Semantic similarity search with ChromaDB and sentence transformers
- **PersistentKnowledgeBase**: Long-term learning with six knowledge categories
- Agent memory integration enables context sharing, discovery collaboration, and semantic learning

#### Learning Systems (`src/learning/`) - Phase 8
- **UserFeedbackProcessor**: Processes 6 types of user feedback (correction, preference, guidance, rating, suggestion, warning)
- **PatternLearner**: Extracts and optimizes patterns from successful workflow executions with confidence scoring
- **AdaptiveBehaviorSystem**: Provides 6 types of behavioral adaptations based on context and learned patterns
- **BaseAgent Integration**: Enhanced with 12+ learning methods for feedback processing and adaptive behavior
- Complete learning lifecycle from feedback capture to behavioral adaptation and performance tracking

#### Agent Communication System (`src/communication/`) - Phase 3
- **CommunicationManager**: Async message routing and conversation tracking
- **Message Protocols**: 13 MessageType enums with structured communication patterns
- **PeerReviewMechanism**: Consensus building and quality assurance across agents
- Direct agent-to-agent messaging with request-response patterns and timeout handling

#### Tool System (`src/tools/`) - Phase 4
- **ToolRegistry**: Central catalog with permissions and discovery capabilities
- **ToolExecutionEngine**: Monitored execution with timeout and error handling
- **BaseAgent Integration**: Tool access with validation and memory integration
- Built-in tools for computation, web search, file operations, and code execution

#### Advanced Workflow Implementations (`src/workflows/`) - Phase 6
- **BaseWorkflow**: Abstract base with common functionality
- **SequentialWorkflow**: Executes tasks in order with dependency handling
- **ParallelWorkflow**: Concurrent execution with thread pool management
- **ConditionalWorkflow**: Dynamic branching based on context evaluation and conditions
- **IterativeWorkflow**: Quality-driven refinement with convergence criteria and improvement feedback
- **HierarchicalWorkflow**: Multi-level team coordination with executive management and specialist delegation
- Extensible architecture supporting hybrid patterns and custom workflow implementations

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

### Testing
```bash
# Run all tests (backend + frontend)
./scripts/run_tests.sh

# Run specific test suites
./scripts/run_tests.sh --backend-only      # Python tests only (407+ tests)
./scripts/run_tests.sh --frontend-only     # TypeScript tests only (131+ tests)
./scripts/run_tests.sh --coverage          # Generate coverage reports

# Run individual tests
pytest tests/test_infrastructure.py::TestMockAgents::test_mock_task_agent_creation -v
cd shepherd-gui && npm test -- --testNamePattern="ProjectFolderSelector"
```

### Python Backend Development
```bash
# Activate environment
source venv/bin/activate

# Run tests (407+ backend tests available across all implemented phases)
pytest tests/

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

# Run tests (131+ frontend tests including Phase 9 collaboration UI)
npm test

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

## Current Status: Phase 10 Complete

### ✅ Phase 1 Completed: Test Infrastructure
- **Comprehensive test infrastructure** with 32 backend tests and 7 frontend tests
- **Mock agent system** for isolated testing with configurable behavior
- **Test automation** with `./scripts/run_tests.sh` supporting multiple test modes
- **Coverage tracking** with HTML reports and 70% minimum threshold
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

### ✅ Phase 2 Completed: Memory System Foundation
- **Three-tier memory architecture** with local, shared, and persistent layers
- **Agent memory integration** with BaseAgent class supporting memory operations
- **Local Agent Memory** with LRU eviction and action tracking
- **Shared Context Pool** with pub/sub system and context types
- **Memory testing infrastructure** with 37 additional tests (31 unit + 6 integration)
- **Agent collaboration** via discovery sharing and context subscriptions
- **Memory lifecycle management** with proper cleanup and statistics tracking
- **Context isolation** between agents while enabling selective collaboration

### ✅ Phase 3 Completed: Agent Communication System
- **Direct agent-to-agent messaging** with CommunicationManager and structured protocols
- **Event-based communication** with Message dataclass and 13 MessageType enums
- **Peer review mechanisms** with consensus building and quality assurance
- **BaseAgent communication integration** with send_message, request_response, and broadcast methods
- **Communication testing infrastructure** with 25 additional tests (17 unit + 8 integration)
- **Request-response patterns** with timeout handling and error recovery
- **Message routing and queuing** with conversation tracking and statistics
- **Structured communication protocols** for discovery sharing, status updates, and peer feedback
- **Total working tests**: 134+ tests (109 previous + 25 tool system tests)

### ✅ Phase 4 Completed: Tool Use Foundation
- **Core tool registry and execution infrastructure** with comprehensive tool catalog and permissions
- **Tool-aware agent capabilities** with permission validation and execution monitoring
- **Basic tool types** (computation, information retrieval, file operations) implemented and tested
- **BaseAgent tool integration** with execute_tool(), validate_tool_access(), and select_tools_for_task()
- **Tool execution engine** with timeout handling, error recovery, and monitoring
- **Tool testing infrastructure** with comprehensive unit and integration tests (25 tests total)
- **Built-in tools**: Calculator, web search, file operations with safety measures and validation

### ✅ Phase 5 Completed: Conversation Compacting System
- **Intelligent conversation compacting** with multiple strategies (Auto, Milestone, Selective, Aggressive, Conservative)
- **Real-time token monitoring** with WebSocket notifications and three-level warning system
- **Context preservation strategy** with importance scoring and category-based preservation
- **Professional GUI components** for conversation management with live updates
- **Complete API integration** with RESTful endpoints and background task support
- **Comprehensive testing** with 44 tests covering all compacting scenarios and strategies

### ✅ Phase 6 Completed: Advanced Workflow Patterns
- **ConditionalWorkflow** with dynamic branching based on context evaluation and intelligent condition functions
- **IterativeWorkflow** with quality-driven convergence, improvement feedback, and multiple convergence strategies
- **HierarchicalWorkflow** with multi-level team coordination, executive management, and specialist delegation
- **Enhanced PromptAnalyzer** with sophisticated pattern detection using 20+ advanced indicators
- **Complete WorkflowSelector** with registry and configuration for all workflow patterns including hybrid scenarios
- **Comprehensive testing** with 87 tests covering all patterns, integration scenarios, and error handling

### ✅ Phase 7 Completed: Vector Memory Implementation
- **VectorMemoryStore** with ChromaDB integration and sentence transformer embeddings for semantic similarity search
- **PersistentKnowledgeBase** with six knowledge types (learned patterns, user preferences, failure patterns, etc.)
- **Enhanced BaseAgent** with vector memory integration including pattern learning and knowledge-enhanced task execution
- **Semantic search capabilities** with configurable similarity thresholds and cross-knowledge-type search
- **Complete integration** with existing three-tier memory architecture maintaining full backwards compatibility
- **Comprehensive testing** with 60 tests covering vector storage, knowledge management, and agent integration

### ✅ Phase 8 Completed: Learning Systems Enhancement
- **UserFeedbackProcessor** with 6 feedback types (correction, preference, guidance, rating, suggestion, warning)
- **PatternLearner** for extracting and optimizing patterns from successful workflow executions
- **AdaptiveBehaviorSystem** providing 6 types of behavioral adaptations based on learned patterns
- **Enhanced BaseAgent** with 12+ learning methods for feedback processing and adaptive behavior
- **Comprehensive testing** with 100+ tests covering all learning scenarios and integration
- **Complete learning lifecycle** from feedback capture to behavioral adaptation and performance tracking

### ✅ Phase 9 Completed: Frontend Collaboration UI  
- **Agent Status Visualization** with real-time agent monitoring and performance metrics
- **Memory Flow Display** showing three-tier memory operations and transfers
- **Learning Progress Indicators** visualizing Phase 8 learning system insights and recommendations
- **Communication Flow Visualization** with real-time agent messaging and network topology
- **Performance Metrics Dashboard** monitoring system resources, workflow execution, and agent efficiency
- **Complete API Integration** with TypeScript client for all learning system endpoints
- **Comprehensive testing** with 131+ frontend tests including component and API client testing

### ✅ Phase 10 Completed: Advanced Analytics and Reporting
- **CollaborationAnalyzer** - Advanced agent interaction pattern analysis with network topology
- **PredictiveEngine** - Machine learning predictions for workflow success, performance, and resource usage
- **MetricsAggregator** - Real-time metrics collection with trend analysis and anomaly detection
- **DashboardEngine** - Customizable dashboards with 9 widget types and real-time streaming
- **ExportManager** - Multi-format reporting (PDF, CSV, JSON, Excel, HTML, Markdown)
- **25+ REST endpoints** with WebSocket support for real-time analytics data streaming
- **110+ comprehensive tests** covering all analytics components and integration scenarios

### 🔮 Future Phases
- **Phase 11**: Enterprise features (multi-user, audit logging, advanced API)
- **Phase 12**: Advanced workflow orchestration and optimization
- **Phase 13**: Production deployment and scaling capabilities

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
4. Add tests for new functionality (use the comprehensive test infrastructure)
5. Run the test suite: `./scripts/run_tests.sh --coverage`
6. Ensure all tests pass (currently 538+ total tests: 407+ backend + 131+ frontend tests)
7. Run linting: `black src/ tests/` and `cd shepherd-gui && npm run lint`
8. Submit a pull request

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