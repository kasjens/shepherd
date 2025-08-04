# 🏗️ Architecture Documentation

Technical architecture and system design documentation for Shepherd.

## 📋 Architecture Guides

### Core System Design
- **[System Overview](system-overview.md)** - High-level architecture and components *(Coming Soon)*
- **[Agent Collaboration](agent-collaboration.md)** - Multi-agent system design and communication
- **[Memory System](memory-system.md)** - Three-tier memory architecture *(Coming Soon)*

### Feature Architecture
- **[Conversation System](conversation-system.md)** - Conversation compacting and context management
- **[Workflow Patterns](workflow-patterns.md)** - Workflow execution patterns and orchestration *(Coming Soon)*
- **[Component Specifications](component-specs.md)** - Detailed component specifications *(Coming Soon)*

## 🎯 Architecture Overview

Shepherd implements a sophisticated multi-agent architecture with:

### Core Components
- **Prompt Analysis Engine** - Natural language request analysis
- **Workflow Selector** - Optimal execution pattern selection  
- **Agent Factory** - Specialized agent creation and management
- **Memory System** - Three-tier memory with vector capabilities
- **Tool Execution** - External tool integration and monitoring

### Integration Layers
- **FastAPI Backend** - RESTful API with WebSocket support
- **Professional GUI** - Next.js/Tauri desktop application
- **Analytics Engine** - Advanced reporting and insights
- **Learning System** - Adaptive behavior and pattern recognition

## 📊 System Maturity

| Component | Status | Implementation | Tests |
|-----------|--------|----------------|-------|
| **Core Orchestration** | Complete | Phase 1-3 | 150+ tests |
| **Memory & Communication** | Complete | Phase 2-3 | 65+ tests |
| **Tool System** | Complete | Phase 4 | 25+ tests |
| **Advanced Workflows** | Complete | Phase 6 | 87+ tests |
| **Vector Memory** | Complete | Phase 7 | 60+ tests |
| **Learning Systems** | Complete | Phase 8 | 100+ tests |
| **Collaboration UI** | Complete | Phase 9 | 131+ tests |
| **Analytics & Reporting** | Complete | Phase 10 | 110+ tests |

## 🔧 Technical Stack

### Backend
- **Python 3.9+** with FastAPI
- **CrewAI** for multi-agent orchestration
- **ChromaDB** for vector memory
- **Sentence Transformers** for embeddings

### Frontend  
- **TypeScript** with Next.js 15
- **Tauri 2** for desktop applications
- **Tailwind CSS** for styling
- **Zustand** for state management

## 🔗 Related Resources

- **[Implementation Plan](../05-development/implementation-plan.md)** - Development roadmap
- **[API Reference](../03-api-reference/)** - Technical API documentation
- **[Design System](../06-design/)** - UI/UX architecture

---

**Start with [Agent Collaboration](agent-collaboration.md) for the core architecture!**