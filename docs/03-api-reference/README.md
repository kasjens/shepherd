# 🔧 API Reference

Complete technical documentation for Shepherd's APIs and integration endpoints.

## 📋 API Documentation

### Core APIs
- **[REST API Reference](rest-api.md)** - Main API endpoints and workflows *(Coming Soon)*
- **[WebSocket API](websocket-api.md)** - Real-time communication and updates *(Coming Soon)*

### Specialized APIs
- **[Analytics API](analytics-api.md)** - Advanced analytics and reporting endpoints
- **[Authentication API](authentication.md)** - Security and user management *(Phase 11 - Coming Soon)*

## 🔗 API Overview

| API Category | Status | Endpoints | Description |
|--------------|--------|-----------|-------------|
| **REST API** | ✅ Active | 25+ | Core workflow and system operations |
| **WebSocket** | ✅ Active | 8+ | Real-time updates and streaming |
| **Analytics** | ✅ Active | 25+ | Analytics data and insights |
| **Authentication** | 🚧 Phase 11 | TBD | User management and security |

## 🚀 Quick Start

### Base URLs
```
Production API: http://localhost:8000/api
WebSocket:     ws://localhost:8000/ws
Documentation: http://localhost:8000/docs
```

### Authentication
```bash
# Most endpoints currently open (Phase 11 will add authentication)
curl -X GET "http://localhost:8000/api/status"
```

### Example Request
```bash
# Execute a workflow
curl -X POST "http://localhost:8000/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze system performance"}'
```

## 📊 Response Format

All APIs return consistent JSON responses:
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_123",
    "version": "1.0.0"
  }
}
```

## 🔗 Related Resources

- **[User Guides](../02-user-guides/)** - Feature usage guides
- **[Architecture](../04-architecture/)** - System design context
- **[Development](../05-development/)** - Contributing to APIs

---

**Start with the [Analytics API](analytics-api.md) for comprehensive examples!**