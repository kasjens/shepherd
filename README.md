<div align="center">
  <img src="Shepherd.png" alt="Shepherd Logo" width="200" height="200">
  
  # Shepherd
  **Intelligent Multi-Agent Workflow Orchestrator**
  
  *By InfraWorks.io*
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)](https://python.org)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript&logoColor=white)](https://typescriptlang.org)
  [![Tests](https://img.shields.io/badge/Tests-658+-green)](docs/05-development/scripts-tools.md)
  [![Phase](https://img.shields.io/badge/Phase-10%20Complete-success)](docs/07-project-history/)
  [![License](https://img.shields.io/badge/License-MIT-blue)](#license)
</div>

---

## 🚀 What is Shepherd?

Shepherd is a **production-ready intelligent multi-agent workflow orchestrator** that automatically analyzes your natural language requests, selects optimal execution patterns, and coordinates specialized AI agents to accomplish complex tasks. 

With **10 complete phases** of development, Shepherd offers enterprise-grade analytics, learning systems, vector memory, and a professional desktop GUI.

### ✨ Key Highlights

- 🧠 **Intelligent Analysis** - Automatically determines optimal workflow patterns from natural language
- 🤖 **Multi-Agent Orchestration** - Creates and coordinates specialized AI agents 
- 📊 **Advanced Analytics** - Enterprise-grade reporting with predictive insights
- 🎓 **Learning Systems** - Adaptive behavior and continuous improvement
- 🖥️ **Professional GUI** - Modern TypeScript desktop application with real-time collaboration
- 🔧 **Tool Integration** - Execute external tools and APIs seamlessly
- 🧩 **Vector Memory** - Semantic search and intelligent context management
- 🏢 **Enterprise Ready** - Comprehensive testing, logging, and production features

---

## 📚 Documentation

### 🎯 **Getting Started**
New to Shepherd? Start here for quick setup and your first workflow.

- **[Quick Start Guide](docs/01-getting-started/quick-start.md)** - 5-minute setup
- **[Installation Guide](docs/01-getting-started/installation.md)** - Complete setup instructions *(Coming Soon)*
- **[Your First Workflow](docs/01-getting-started/first-workflow.md)** - Hands-on tutorial *(Coming Soon)*

### 📖 **User Guides**
Learn how to use Shepherd's powerful features effectively.

- **[Tool Usage Guide](docs/02-user-guides/tool-usage.md)** - External tool integration
- **[Conversation Management](docs/02-user-guides/conversation-management.md)** - Context optimization  
- **[Analytics Dashboard](docs/02-user-guides/analytics-dashboard.md)** - Advanced reporting and insights
- **[Browse All User Guides →](docs/02-user-guides/)**

### 🔧 **API Reference**
Technical documentation for developers and integrations.

- **[Analytics API](docs/03-api-reference/analytics-api.md)** - Analytics endpoints and data
- **[REST API Reference](docs/03-api-reference/rest-api.md)** - Main API endpoints *(Coming Soon)*
- **[WebSocket API](docs/03-api-reference/websocket-api.md)** - Real-time updates *(Coming Soon)*
- **[Browse All API Docs →](docs/03-api-reference/)**

### 🏗️ **Architecture**
System design and technical architecture for architects and contributors.

- **[Agent Collaboration](docs/04-architecture/agent-collaboration.md)** - Multi-agent system design
- **[Conversation System](docs/04-architecture/conversation-system.md)** - Context management architecture
- **[System Overview](docs/04-architecture/system-overview.md)** - High-level architecture *(Coming Soon)*
- **[Browse All Architecture Docs →](docs/04-architecture/)**

### 👨‍💻 **Development**
Resources for contributing to and extending Shepherd.

- **[Implementation Plan](docs/05-development/implementation-plan.md)** - Development roadmap
- **[Scripts & Tools](docs/05-development/scripts-tools.md)** - Development utilities
- **[Contributing Guide](docs/05-development/contributing.md)** - How to contribute *(Coming Soon)*
- **[Browse All Development Docs →](docs/05-development/)**

### 🎨 **Design System**
UI components and visual design guidelines.

- **[UI Components](docs/06-design/ui-components.md)** - Component library
- **[Layout System](docs/06-design/layout-system.md)** - Grid and responsive design
- **[Theme Design](docs/06-design/theme-design.md)** - Visual identity and themes
- **[Browse All Design Docs →](docs/06-design/)**

### 📜 **Project History**
Implementation timeline and phase completion records.

- **[Phase Completion Reports](docs/07-project-history/)** - Detailed implementation history
- **[Phase 10: Advanced Analytics](docs/07-project-history/phase-10-completion.md)** - Latest completion
- **[All Historical Records →](docs/07-project-history/)**

---

## ⚡ Quick Start

### 1. Installation
```bash
# Clone and install
git clone <repository-url>
cd shepherd
./scripts/install.sh
```

### 2. Launch Shepherd
```bash
# Desktop GUI (Recommended)
./scripts/start.sh --gui

# API Server
./scripts/start.sh --api

# CLI Mode
./scripts/start.sh --cli "Create a project plan"
```

### 3. Try It Out
Open the desktop app and try: *"Analyze system performance and create a report"*

**[→ Full Quick Start Guide](docs/01-getting-started/quick-start.md)**

---

## 🏆 Current Status

### ✅ Production Ready (Phase 10 Complete)
- **658+ Total Tests** (527+ backend + 131+ frontend)
- **10 Complete Phases** - From test infrastructure to advanced analytics
- **Enterprise Features** - Advanced analytics, learning systems, professional GUI
- **98%+ Success Rate** - Comprehensive test coverage and validation

### 🎯 Architecture Highlights
- **Multi-Agent Orchestration** - Intelligent workflow selection and agent coordination
- **Vector Memory System** - ChromaDB integration with semantic search
- **Learning & Adaptation** - User feedback processing and pattern recognition  
- **Real-Time Collaboration** - Live agent status and memory visualization
- **Advanced Analytics** - Predictive insights, custom dashboards, multi-format exports

### 📊 Key Metrics
| Component | Status | Tests | Description |
|-----------|--------|-------|-------------|
| **Core System** | ✅ Complete | 150+ | Orchestration, memory, communication |
| **Tool Integration** | ✅ Complete | 25+ | External tool execution and monitoring |
| **Advanced Workflows** | ✅ Complete | 87+ | Conditional, iterative, hierarchical patterns |
| **Vector Memory** | ✅ Complete | 60+ | Semantic search and knowledge management |
| **Learning Systems** | ✅ Complete | 100+ | Adaptive behavior and pattern recognition |
| **Analytics Engine** | ✅ Complete | 110+ | Advanced reporting and predictive insights |
| **Professional GUI** | ✅ Complete | 131+ | Real-time collaboration interface |

---

## 🛠️ Technology Stack

### Backend
- **[Python 3.9+](https://python.org)** with [FastAPI](https://fastapi.tiangolo.com/)
- **[CrewAI](https://github.com/joaomdmoura/crewAI)** for multi-agent orchestration
- **[ChromaDB](https://chromadb.com/)** for vector memory storage
- **[Ollama](https://ollama.com/)** for local LLM support

### Frontend
- **[Next.js 15](https://nextjs.org/)** with TypeScript and App Router
- **[Tauri 2](https://tauri.app/)** for cross-platform desktop applications
- **[Tailwind CSS](https://tailwindcss.com/)** for modern styling
- **[Zustand](https://zustand-demo.pmnd.rs/)** for state management

---

## 🌟 Use Cases

### Business Operations
- **Project Planning** - Automated project breakdown and timeline creation
- **Data Analysis** - Intelligent report generation with visualizations
- **Process Optimization** - Workflow analysis and improvement recommendations

### Development Teams  
- **Code Analysis** - Automated code review and quality assessment
- **System Administration** - Server monitoring and optimization
- **Documentation** - Automated documentation generation and updates

### Research & Analysis
- **Market Research** - Comprehensive research with structured reports
- **Competitive Analysis** - Multi-source data gathering and insights
- **Technical Research** - Literature review and technology assessment

---

## 🆘 Support & Help

### Need Help?
- 📧 **Email Support**: [support@infraworks.io](mailto:support@infraworks.io)
- 📖 **Documentation**: [Browse our comprehensive docs](docs/)
- 🚀 **Quick Start**: [Get up and running in 5 minutes](docs/01-getting-started/quick-start.md)

### Troubleshooting
- **Installation Issues**: Check [installation guide](docs/01-getting-started/installation.md)
- **API Problems**: Review [API reference](docs/03-api-reference/)
- **System Architecture**: Understand the [architecture](docs/04-architecture/)

---

## 🤝 Contributing

We welcome contributions! Shepherd is built with a comprehensive test-driven development approach.

1. **Fork** the repository
2. **Review** the [implementation plan](docs/05-development/implementation-plan.md)
3. **Follow** our [development workflow](docs/05-development/)
4. **Test** thoroughly with our 658+ test suite
5. **Submit** a pull request

**[→ Development Documentation](docs/05-development/)**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with ❤️ by the InfraWorks.io team. Inspired by the need for intelligent workflow automation with modern, professional interfaces.

Special thanks to the open-source community and the creators of CrewAI, FastAPI, Next.js, and Tauri for making this project possible.

---

<div align="center">
  
  **Shepherd** - *Guiding your digital operations with intelligence and care*
  
  [Get Started](docs/01-getting-started/quick-start.md) • [Documentation](docs/) • [Support](mailto:support@infraworks.io)
  
</div>