# Shepherd - Development Context

**By InfraWorks.io**

## Project Overview

**Product Name**: Shepherd  
**Developer**: InfraWorks.io  
**Tagline**: "Your intelligent workflow shepherd - guiding and protecting your digital operations"

**Goal**: Create an intelligent multi-agent system that automatically determines the optimal workflow pattern and orchestration strategy based on natural language user requests, with specialized applications for codebase analysis, Linux system administration, and other complex task domains.

## Core Concept

The system acts as an **Intelligent Workflow AI** that:
1. **Analyzes** user requests in natural language
2. **Determines** the optimal workflow pattern (Sequential, Parallel, Conditional, Iterative, Hierarchical, Event-driven, Hybrid)
3. **Selects** appropriate specialized agents based on task requirements
4. **Orchestrates** execution with built-in safety checks and user confirmation
5. **Monitors** and provides real-time feedback during execution
6. **Handles** errors and provides rollback capabilities

## Technical Architecture

### Core Components

#### 1. **Prompt Analysis Engine**
- **Purpose**: Analyze user requests to determine optimal workflow patterns
- **Key Functions**:
  - Complexity scoring (0.0-1.0)
  - Urgency detection (low/medium/high/critical)
  - Quality requirements assessment
  - Task type classification (research, creative, analytical, technical, communication)
  - Dependency analysis
  - Risk assessment

#### 2. **Workflow Pattern Selector**
- **Purpose**: Choose the best orchestration pattern based on analysis
- **Patterns Supported**:
  - **Sequential**: A → B → C → D (linear dependencies)
  - **Parallel**: A, B, C → D (simultaneous execution + coordination)
  - **Conditional**: A → [Decision] → B₁|B₂|B₃ (branching logic)
  - **Iterative**: A → B → [Quality Check] → (Pass: End | Fail: Refine → B)
  - **Hierarchical**: Manager → Team Leads → Specialists
  - **Event-Driven**: Event → Route → Specialized Handler
  - **Hybrid**: Combination of multiple patterns

#### 3. **Dynamic Agent Factory**
- **Purpose**: Create specialized agents based on detected task types
- **Agent Types**:
  - **Research Agents**: Information gathering, analysis
  - **Technical Agents**: Code analysis, implementation, system administration
  - **Creative Agents**: Content creation, writing, design
  - **Security Agents**: Safety validation, risk assessment
  - **Monitoring Agents**: Execution tracking, performance monitoring
  - **Coordination Agents**: Workflow orchestration, result compilation

#### 4. **Interactive Execution Engine**
- **Purpose**: Execute workflows with user confirmation and safety checks
- **Features**:
  - Step-by-step execution with confirmation
  - Risk-based approval requirements
  - Real-time progress monitoring
  - Automatic backup creation
  - Rollback capabilities
  - Error handling and recovery

#### 5. **Safety and Validation System**
- **Purpose**: Ensure safe execution of all operations
- **Components**:
  - Command validation and sandboxing
  - Risk assessment and scoring
  - Backup and rollback planning
  - User confirmation workflows
  - Safety constraint enforcement

## Specialized Applications

### 1. **Codebase Analysis & Feature Implementation**

**Use Case**: "Analyze my React codebase and implement user authentication with JWT"

**Workflow**: 
- **Pattern**: Hierarchical (Complex project with multiple specialists)
- **Agents**: Codebase Analyzer → Documentation Reader → System Designer → Feature Implementer → Test Creator → Integration Guide Generator

**Key Features**:
- Framework detection and adaptation
- Architecture pattern recognition
- Code style consistency
- Database integration
- API endpoint generation
- Comprehensive testing
- Deployment guidance

### 2. **Linux System Administration**

**Use Case**: "My server is slow, diagnose and fix performance issues"

**Workflow**:
- **Pattern**: Conditional (Different fixes based on diagnosis)
- **Agents**: System Monitor → Performance Analyzer → [Decision Router] → Package Manager|Service Manager|Security Admin|Storage Manager

**Key Features**:
- Distribution-aware commands
- Safety validation and confirmation
- Service impact analysis
- Backup before changes
- Step-by-step execution with rollback
- Real-time monitoring

### 3. **Business Intelligence & Analysis**

**Use Case**: "Analyze our Q3 sales data and create executive presentation"

**Workflow**:
- **Pattern**: Parallel + Sequential (Data analysis in parallel, then coordination)
- **Agents**: Data Analyst + Market Researcher + Financial Analyst → Report Compiler → Presentation Creator

## Implementation Stack

### Backend Framework
- **Primary**: Python with CrewAI for multi-agent orchestration
- **Alternative**: LangGraph for complex state-based workflows
- **LLM Backend**: 
  - **Local**: Ollama (llama3.1, mistral, codellama)
  - **Cloud**: OpenAI GPT-4, Anthropic Claude, or others

### Frontend Interface
- **Primary**: Gradio for rapid prototyping and demo
- **Production**: React/Vue.js with WebSocket for real-time updates
- **Features**: 
  - Real-time execution monitoring
  - Interactive confirmation dialogs
  - Progress tracking
  - Result visualization

### Tools and Integrations
- **File Processing**: FileReadTool, DirectoryReadTool for codebase analysis
- **Web Integration**: Web scraping tools for research
- **System Integration**: Subprocess execution with safety constraints
- **Database**: SQLite/PostgreSQL for execution history and learning

## Key Classes and Interfaces

### Core Classes

```python
@dataclass
class PromptAnalysis:
    complexity_score: float
    urgency_score: float  
    quality_requirements: float
    task_types: List[str]
    dependencies: bool
    parallel_potential: bool
    decision_points: bool
    iteration_needed: bool
    team_size_needed: int
    recommended_pattern: WorkflowPattern
    confidence: float

@dataclass 
class ExecutionStep:
    id: str
    command: str
    description: str
    risk_level: str
    requires_confirmation: bool
    backup_command: Optional[str]
    rollback_command: Optional[str] 
    status: ExecutionStatus
    output: str
    error: str
    execution_time: float

class IntelligentOrchestrator:
    def analyze_prompt(self, user_request: str) -> PromptAnalysis
    def create_workflow(self, analysis: PromptAnalysis) -> Crew
    def execute_interactive(self, workflow: Crew) -> ExecutionResults
```

### Specialized Orchestrators

```python
class CodebaseOrchestrator(IntelligentOrchestrator):
    def analyze_codebase_structure(self, path: str) -> CodebaseAnalysis
    def create_feature_implementation_plan(self, feature_request: str, codebase: CodebaseAnalysis) -> ExecutionPlan
    def generate_code_implementation(self, plan: ExecutionPlan) -> CodeImplementation

class LinuxSystemOrchestrator(IntelligentOrchestrator):
    def analyze_system_request(self, request: str) -> SystemAnalysis
    def create_execution_plan(self, analysis: SystemAnalysis) -> ExecutionPlan
    def execute_with_confirmation(self, plan: ExecutionPlan) -> ExecutionResults
```

## Development Phases

### Phase 1: Core Framework (MVP)
- [ ] Basic prompt analysis engine
- [ ] Simple workflow pattern detection
- [ ] Sequential and parallel workflow execution
- [ ] Basic agent creation and task assignment
- [ ] Gradio interface for testing

### Phase 2: Safety and Interaction
- [ ] Interactive confirmation system
- [ ] Risk assessment and validation
- [ ] Backup and rollback capabilities
- [ ] Real-time execution monitoring
- [ ] Error handling and recovery

### Phase 3: Specialized Applications
- [ ] Codebase analysis orchestrator  
- [ ] Linux system administration orchestrator
- [ ] Advanced workflow patterns (conditional, iterative, hierarchical)
- [ ] Context-aware agent selection

### Phase 4: Advanced Features
- [ ] Learning from user feedback
- [ ] Workflow optimization based on historical data
- [ ] Advanced safety constraints and sandboxing
- [ ] Integration with external tools and APIs
- [ ] Production-ready web interface

### Phase 5: Enterprise Features
- [ ] Multi-user support and permissions
- [ ] Audit logging and compliance
- [ ] Scalable execution infrastructure
- [ ] Plugin system for custom agents
- [ ] API for external integrations

## Technical Requirements

### Dependencies
```python
# Core framework
crewai>=0.1.0
langchain>=0.1.0
gradio>=4.0.0

# Local LLM support
ollama-python>=0.1.0
transformers>=4.30.0
torch>=2.0.0

# System integration
psutil>=5.9.0
subprocess32>=3.5.4

# Web and file processing
requests>=2.28.0
beautifulsoup4>=4.11.0
python-magic>=0.4.27

# Development and testing
pytest>=7.0.0
black>=22.0.0
mypy>=1.0.0
```

### System Requirements
- **Python**: 3.9+
- **Memory**: 8GB+ (for local LLM execution)
- **Storage**: 20GB+ (for model storage)
- **OS**: Linux (primary), macOS, Windows (with WSL)

## Configuration Examples

### Ollama Setup
```python
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "models": {
        "general": "llama3.1:8b",
        "code": "codellama:7b", 
        "analysis": "mistral:7b"
    },
    "temperature": 0.7,
    "timeout": 30
}
```

### Safety Configuration
```python
SAFETY_CONFIG = {
    "blocked_commands": [
        "rm -rf /", "dd if=/dev/zero", "mkfs", "format"
    ],
    "requires_confirmation": [
        "systemctl stop", "userdel", "iptables -F"
    ],
    "backup_paths": [
        "/etc/", "/home/", "/var/lib/"
    ],
    "max_execution_time": 300,
    "sandbox_mode": True
}
```

## Testing Strategy

### Unit Tests
- Prompt analysis accuracy
- Workflow pattern selection logic
- Agent creation and task assignment
- Safety validation functions

### Integration Tests  
- End-to-end workflow execution
- Multi-agent coordination
- Interactive confirmation flows
- Rollback and recovery procedures

### Safety Tests
- Command validation and blocking
- Sandbox execution verification
- Backup and rollback functionality
- Error handling edge cases

## Deployment Options

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Run development server
python main.py --dev
```

### Production Deployment
- **Docker**: Containerized deployment with Ollama
- **Cloud**: AWS/GCP/Azure with GPU instances for LLM
- **On-premise**: Kubernetes cluster for scalability

## Security Considerations

### Command Execution Safety
- Whitelist-based command validation
- Sandboxed execution environment
- User permission verification
- Audit logging for all operations

### Data Protection
- Local LLM processing (no data sent to external APIs)
- Encrypted storage for sensitive configurations
- Secure credential management
- RBAC for multi-user deployments

## Future Extensions

### Advanced AI Features
- **Reinforcement Learning**: Learn optimal workflow patterns from success/failure feedback
- **Context Memory**: Remember user preferences and system configurations
- **Predictive Analysis**: Anticipate common issues and proactively suggest solutions

### Domain Expansions
- **DevOps Orchestration**: CI/CD pipeline management
- **Database Administration**: Query optimization, schema management
- **Cloud Management**: AWS/Azure/GCP resource orchestration
- **Security Operations**: Automated threat response workflows

## Success Metrics

### User Experience
- Time to complete common tasks (target: 50% reduction)
- Error rate in command execution (target: <5%)
- User satisfaction with natural language interface

### Technical Performance  
- Workflow pattern selection accuracy (target: >90%)
- Agent coordination efficiency
- System resource utilization
- Execution time optimization

## Getting Started

1. **Clone repository** and set up development environment
2. **Install Ollama** and pull required models
3. **Configure safety settings** for your environment
4. **Run basic examples** to understand workflow patterns
5. **Implement specialized orchestrators** for your use cases
6. **Add interactive confirmation** and safety features
7. **Deploy and iterate** based on user feedback

---

This context provides the foundation for building an intelligent, safe, and user-friendly workflow orchestration system that can handle complex multi-step tasks across various domains while maintaining high safety standards and user control.