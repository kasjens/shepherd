# GUI Implementation Plan - Simplified Shepherd Interface

**Version**: 1.0  
**Date**: 2025-08-10  
**Objective**: Implement a fast, responsive, and user-friendly GUI for the Shepherd workflow orchestrator

---

## Overview

This plan outlines a phased approach to implementing the simplified Shepherd GUI with a focus on performance, testing, and user experience. Each phase builds upon the previous one, with comprehensive testing at every step.

## Success Criteria

- **Performance**: First Contentful Paint < 1s, Time to Interactive < 2s
- **Responsiveness**: All interactions respond within 100ms
- **Testing**: Minimum 80% code coverage
- **Accessibility**: WCAG 2.1 AA compliance
- **Bundle Size**: Initial JS bundle < 200KB (gzipped)

---

## Phase 0: Cleanup & Migration Preparation (Days 1-2)

### 0.1 Audit Existing Components
**Analysis Tasks:**
```bash
# Generate component usage report
cd shepherd-gui
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "export" > component-inventory.txt

# Check for unused components
npx depcheck

# Analyze bundle for dead code
npm run build:analyze
```

### 0.2 Backup Current Implementation
**Backup Strategy:**
```bash
# Create backup branch
git checkout -b backup/old-gui-implementation
git add .
git commit -m "Backup: Old 3-panel GUI implementation before migration"

# Archive old components
mkdir -p archive/old-gui
cp -r src/components archive/old-gui/
cp -r src/app archive/old-gui/
```

### 0.3 Remove Obsolete Components
**Components to Remove:**
```bash
# Old 3-panel layout components
rm -rf src/components/layout/artifacts-panel.tsx
rm -rf src/components/layout/three-panel-layout.tsx
rm -rf src/components/layout/conversation-area.tsx  # Old implementation
rm -rf src/components/layout/sidebar.tsx  # Old non-collapsible version
rm -rf src/components/features/settings/project-folder-selector.tsx  # Moving to modal

# Deprecated feature components
rm -rf src/components/features/chat/message-input.tsx  # Replaced with InputArea
rm -rf src/components/features/agents/agent-status.tsx  # Old implementation
rm -rf src/components/features/agents/agent-collaboration.tsx  # Old visualization
rm -rf src/components/features/agents/communication-flow.tsx  # Outdated
rm -rf src/components/features/memory/memory-flow.tsx  # Outdated visualization
rm -rf src/components/features/learning/learning-progress.tsx  # Moving to modal
rm -rf src/components/features/performance/performance-metrics.tsx  # Integrated into ResourceUsage

# Old page components
rm -rf src/app/page.tsx  # Old home page with 3-panel layout
rm -rf src/app/layout.tsx  # Will be recreated with new structure

# Old styles that won't be needed
rm -rf src/styles/panels.css
rm -rf src/styles/resizable.css

# Old utility files
rm -rf src/utils/panel-resize.ts
rm -rf src/utils/drag-handlers.ts

# Old test files
rm -rf __tests__/components/ArtifactsPanel.test.tsx
rm -rf __tests__/components/ProjectFolderSelector.test.tsx
rm -rf __tests__/components/ThreePanelLayout.test.tsx
rm -rf __tests__/features/*.test.tsx  # All old feature tests
```

**File Structure After Cleanup:**
```
shepherd-gui/
├── src/
│   ├── components/
│   │   ├── ui/           # Keep: Reusable UI components
│   │   └── providers/     # Keep: Context providers
│   ├── lib/              # Keep: Utilities and helpers
│   ├── styles/
│   │   └── globals.css   # Keep: Global styles
│   └── types/            # Keep: TypeScript definitions
├── public/
│   └── Shepherd.png      # Keep: Logo
└── __tests__/
    └── setup/            # Keep: Test setup files
```

### 0.4 Clean Dependencies
**Package Cleanup:**
```json
// Remove from package.json
{
  "dependencies": {
    // Remove if not used elsewhere:
    "react-resizable-panels": "^0.0.55",  // Old panel system
    "react-split-pane": "^0.1.92",        // Old split implementation
    "@dnd-kit/sortable": "^7.0.2",        // If not using drag-drop
    "react-beautiful-dnd": "^13.1.1"      // Old DnD library
  }
}
```

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### 0.5 Migration Checklist
**Pre-Implementation Validation:**
```typescript
// migration-checklist.ts
export const migrationChecklist = {
  removed: [
    'artifacts-panel.tsx',
    'three-panel-layout.tsx',
    'old agent status components',
    'deprecated hooks'
  ],
  migrated: [
    'theme system -> preserved',
    'websocket service -> updated',
    'api client -> enhanced'
  ],
  new: [
    'Sidebar with collapse',
    'Modal system',
    'Virtual scrolling',
    'Performance monitoring'
  ]
};
```

**Tests for Cleanup:**
```typescript
// __tests__/migration/cleanup.test.ts
describe('Migration Cleanup', () => {
  test('no references to removed components', () => {
    const srcFiles = glob.sync('src/**/*.{ts,tsx}');
    const removedImports = [
      'ArtifactsPanel',
      'ThreePanelLayout',
      'ProjectFolderSelector'
    ];
    
    srcFiles.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');
      removedImports.forEach(imp => {
        expect(content).not.toContain(imp);
      });
    });
  });
  
  test('no unused dependencies', () => {
    const { dependencies } = require('../package.json');
    const blacklist = ['react-resizable-panels', 'react-split-pane'];
    
    blacklist.forEach(dep => {
      expect(dependencies).not.toHaveProperty(dep);
    });
  });
});
```

---

## Phase 1: Foundation & Core Layout (Week 1)

### 1.1 Project Setup & Configuration
**Tasks:**
```bash
# Now working with clean slate
cd shepherd-gui

# Install performance dependencies
npm install --save-dev @next/bundle-analyzer webpack-bundle-analyzer
npm install react-intersection-observer react-window react-virtualized-auto-sizer
npm install @tanstack/react-query zustand immer
```

**Configuration:**
- Configure Next.js 15 for optimal performance
- Set up code splitting and dynamic imports
- Configure Tailwind CSS purging
- Set up ESLint and Prettier
- Configure Jest and React Testing Library

**Files to Create:**
```typescript
// next.config.js - Performance optimizations
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
  },
}

// src/lib/performance.ts - Performance monitoring
export const measurePerformance = (name: string, fn: () => void) => {
  performance.mark(`${name}-start`);
  fn();
  performance.mark(`${name}-end`);
  performance.measure(name, `${name}-start`, `${name}-end`);
}
```

**Tests:**
```typescript
// __tests__/setup/performance.test.ts
describe('Performance Configuration', () => {
  test('Bundle size is under limit', () => {
    // Test bundle analyzer output
  });
  
  test('Lazy loading is configured', () => {
    // Verify dynamic imports
  });
});
```

### 1.2 Core Layout Implementation
**Components to Build:**
```typescript
// src/components/layout/AppLayout.tsx
// Main application layout with sidebar and conversation area

// src/components/layout/sidebar/Sidebar.tsx
// Collapsible sidebar with smooth animations

// src/components/layout/conversation/ConversationArea.tsx
// Main conversation interface
```

**Performance Optimizations:**
- Use CSS transforms for sidebar animation (GPU accelerated)
- Implement `will-change` CSS property for animated elements
- Use `React.memo()` for component memoization
- Implement `useMemo()` and `useCallback()` hooks

**Tests:**
```typescript
// __tests__/layout/Sidebar.test.tsx
describe('Sidebar Component', () => {
  test('renders without blocking main thread', async () => {
    const { container } = render(<Sidebar />);
    const paintTime = performance.getEntriesByType('paint')[0];
    expect(paintTime.startTime).toBeLessThan(1000);
  });
  
  test('collapse animation uses transform', () => {
    // Test CSS transform usage
  });
  
  test('memoizes expensive computations', () => {
    // Test React.memo effectiveness
  });
});
```

**Performance Metrics:**
- Sidebar toggle animation: < 16ms per frame (60 FPS)
- Initial render: < 500ms
- Memory usage: < 50MB

---

## Phase 2: State Management & Data Flow (Week 2)

### 2.1 Zustand Store Setup
**Stores to Implement:**
```typescript
// src/stores/uiStore.ts
interface UIStore {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'blue';
  toggleSidebar: () => void;
  setTheme: (theme: Theme) => void;
}

// src/stores/conversationStore.ts
interface ConversationStore {
  messages: Message[];
  currentConversationId: string | null;
  addMessage: (message: Message) => void;
  clearConversation: () => void;
}

// src/stores/workflowStore.ts
interface WorkflowStore {
  mode: WorkflowMode;
  agents: Agent[];
  status: 'idle' | 'running' | 'complete' | 'error';
  setMode: (mode: WorkflowMode) => void;
  updateAgentStatus: (agentId: string, status: AgentStatus) => void;
}
```

**Performance Optimizations:**
- Use Immer for immutable updates
- Implement store subscriptions with selectors
- Use shallow equality checks
- Implement store persistence with debouncing

**Tests:**
```typescript
// __tests__/stores/conversationStore.test.ts
describe('Conversation Store', () => {
  test('updates without unnecessary re-renders', () => {
    const renderCount = jest.fn();
    const TestComponent = () => {
      renderCount();
      const messages = useConversationStore(state => state.messages);
      return <div>{messages.length}</div>;
    };
    
    // Add message and verify single re-render
  });
  
  test('selector prevents unrelated updates', () => {
    // Test selector isolation
  });
});
```

### 2.2 API Integration Layer
**Services to Create:**
```typescript
// src/services/api.ts
export const api = {
  workflow: {
    execute: async (request: WorkflowRequest) => {
      // Implement with abort controller for cancellation
    }
  },
  conversation: {
    compact: async (id: string, strategy: CompactStrategy) => {
      // Implement with request caching
    }
  }
}

// src/services/websocket.ts
export class WebSocketService {
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect() {
    // Implement with exponential backoff
  }
}
```

**Performance Optimizations:**
- Implement request debouncing and throttling
- Use React Query for caching and background refetching
- Implement optimistic updates
- Use AbortController for request cancellation

**Tests:**
```typescript
// __tests__/services/api.test.ts
describe('API Service', () => {
  test('caches repeated requests', async () => {
    // Test React Query caching
  });
  
  test('cancels in-flight requests', async () => {
    // Test AbortController
  });
  
  test('implements exponential backoff', async () => {
    // Test reconnection strategy
  });
});
```

---

## Phase 3: Core Components Implementation (Week 3)

### 3.1 Sidebar Components
**Components to Build:**
```typescript
// src/components/layout/sidebar/QuickActions.tsx
// Optimized with icon lazy loading

// src/components/layout/sidebar/WorkflowControls.tsx
// Debounced input handlers

// src/components/layout/sidebar/AgentMonitor.tsx
// Virtual scrolling for agent list

// src/components/layout/sidebar/ResourceUsage.tsx
// Throttled updates for metrics
```

**Performance Optimizations:**
- Lazy load icons using dynamic imports
- Virtualize long lists (react-window)
- Debounce slider inputs (300ms)
- Throttle metric updates (1s)
- Use CSS containment for layout stability

**Tests:**
```typescript
// __tests__/components/sidebar/AgentMonitor.test.tsx
describe('Agent Monitor', () => {
  test('virtualizes list with > 10 agents', () => {
    const agents = Array.from({ length: 100 }, (_, i) => createMockAgent(i));
    const { container } = render(<AgentMonitor agents={agents} />);
    
    // Verify only visible agents are rendered
    const renderedAgents = container.querySelectorAll('[data-testid="agent-item"]');
    expect(renderedAgents.length).toBeLessThan(20);
  });
  
  test('updates efficiently with WebSocket data', () => {
    // Test selective re-rendering
  });
});
```

### 3.2 Conversation Components
**Components to Build:**
```typescript
// src/components/conversation/MessageList.tsx
// Virtual scrolling with dynamic height

// src/components/conversation/Message.tsx
// Memoized with shallow comparison

// src/components/conversation/InputArea.tsx
// Debounced auto-save, optimized textarea
```

**Performance Optimizations:**
- Implement virtual scrolling with react-window
- Use Intersection Observer for lazy loading
- Implement message pagination (load 50 at a time)
- Use Web Workers for markdown parsing
- Implement efficient syntax highlighting

**Tests:**
```typescript
// __tests__/components/conversation/MessageList.test.tsx
describe('Message List', () => {
  test('renders 1000+ messages without lag', () => {
    const messages = generateMockMessages(1000);
    const startTime = performance.now();
    
    render(<MessageList messages={messages} />);
    
    const renderTime = performance.now() - startTime;
    expect(renderTime).toBeLessThan(100); // Under 100ms
  });
  
  test('lazy loads message content', () => {
    // Test Intersection Observer
  });
});
```

---

## Phase 4: Real-time Features & WebSocket (Week 4)

### 4.1 WebSocket Integration
**Implementation:**
```typescript
// src/hooks/useWebSocket.ts
export const useWebSocket = () => {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  
  useEffect(() => {
    const ws = new WebSocketService();
    
    // Implement with reconnection logic
    ws.on('message', handleMessage);
    ws.on('error', handleError);
    
    return () => ws.close();
  }, []);
  
  return { status, send };
};
```

**Performance Optimizations:**
- Batch WebSocket messages (100ms window)
- Implement message queuing during disconnection
- Use binary protocols for large data
- Implement compression (permessage-deflate)

**Tests:**
```typescript
// __tests__/hooks/useWebSocket.test.ts
describe('WebSocket Hook', () => {
  test('batches rapid messages', async () => {
    const { result } = renderHook(() => useWebSocket());
    
    // Send 100 messages rapidly
    for (let i = 0; i < 100; i++) {
      result.current.send({ type: 'test', data: i });
    }
    
    // Verify batching occurred
    expect(mockWebSocket.send).toHaveBeenCalledTimes(1);
  });
  
  test('reconnects with exponential backoff', () => {
    // Test reconnection delays: 1s, 2s, 4s, 8s, 16s
  });
});
```

### 4.2 Live Updates Implementation
**Components:**
```typescript
// src/components/features/LiveUpdates.tsx
// Efficient diff-based updates

// src/components/features/AgentStatus.tsx
// Throttled status updates

// src/components/features/TokenUsageIndicator.tsx
// Animated progress with RAF
```

**Performance Optimizations:**
- Use requestAnimationFrame for animations
- Implement selective component updates
- Use CSS animations where possible
- Throttle non-critical updates

---

## Phase 5: Modal System & Overlays (Week 5)

### 5.1 Modal Components
**Implementation:**
```typescript
// src/components/modals/ModalProvider.tsx
// Portal-based rendering

// src/components/modals/ArtifactModal.tsx
// Lazy-loaded content viewers

// src/components/modals/AnalyticsModal.tsx
// Chart lazy loading with suspense

// src/components/modals/SettingsModal.tsx
// Tab-based lazy loading
```

**Performance Optimizations:**
- Use React Portals for modal rendering
- Lazy load modal content
- Implement code splitting per modal
- Use Suspense boundaries
- Prevent body scroll when modal open

**Tests:**
```typescript
// __tests__/components/modals/ModalProvider.test.tsx
describe('Modal System', () => {
  test('lazy loads modal content', async () => {
    const { getByText, queryByTestId } = render(<App />);
    
    // Modal content not in DOM initially
    expect(queryByTestId('analytics-charts')).toBeNull();
    
    // Open modal
    fireEvent.click(getByText('Analytics'));
    
    // Content loads
    await waitFor(() => {
      expect(queryByTestId('analytics-charts')).toBeInTheDocument();
    });
  });
  
  test('prevents memory leaks on unmount', () => {
    // Test cleanup
  });
});
```

---

## Phase 6: Advanced Features & Analytics (Week 6)

### 6.1 Analytics Components
**Implementation:**
```typescript
// src/components/analytics/Dashboard.tsx
// Virtualized chart grid

// src/components/analytics/Charts.tsx
// Lazy-loaded chart library

// src/components/analytics/ExportManager.tsx
// Web Worker for data processing
```

**Performance Optimizations:**
- Lazy load chart libraries (Chart.js/D3)
- Use Web Workers for data processing
- Implement virtual scrolling for data tables
- Use canvas rendering for complex visualizations
- Implement progressive data loading

### 6.2 Learning System Integration
**Components:**
```typescript
// src/components/learning/FeedbackPanel.tsx
// Debounced feedback submission

// src/components/learning/PatternInsights.tsx
// Paginated pattern display
```

---

## Phase 7: Performance Optimization & Polish (Week 7)

### 7.1 Bundle Optimization
**Tasks:**
- Analyze bundle with webpack-bundle-analyzer
- Implement route-based code splitting
- Optimize images with next/image
- Implement font subsetting
- Remove unused CSS with PurgeCSS

**Target Metrics:**
```javascript
// performance.config.js
module.exports = {
  budgets: [
    {
      type: 'bundle',
      name: 'main',
      maximumWarning: '200kb',
      maximumError: '250kb'
    },
    {
      type: 'entry',
      name: 'polyfills',
      maximumWarning: '50kb'
    }
  ]
};
```

### 7.2 Runtime Optimization
**Implementation:**
- Implement service worker for caching
- Add resource hints (preconnect, prefetch)
- Implement progressive enhancement
- Add loading skeletons
- Optimize Critical Rendering Path

**Tests:**
```typescript
// __tests__/performance/lighthouse.test.ts
describe('Lighthouse Metrics', () => {
  test('achieves 90+ performance score', async () => {
    const results = await runLighthouse('http://localhost:3000');
    expect(results.performance).toBeGreaterThan(90);
  });
  
  test('Time to Interactive < 2s', async () => {
    const metrics = await getMetrics();
    expect(metrics.tti).toBeLessThan(2000);
  });
});
```

---

## Phase 8: Testing & Quality Assurance (Week 8)

### 8.1 Comprehensive Testing
**Test Suites:**
```bash
# Unit Tests
npm run test:unit         # Component logic
npm run test:stores       # State management
npm run test:hooks        # Custom hooks

# Integration Tests  
npm run test:integration  # Component interaction
npm run test:api         # API integration
npm run test:ws          # WebSocket communication

# E2E Tests
npm run test:e2e         # Full user flows
npm run test:a11y        # Accessibility
npm run test:performance # Performance benchmarks
```

### 8.2 Performance Testing
**Metrics to Track:**
```typescript
// performance-metrics.ts
export const performanceMetrics = {
  FCP: 1000,     // First Contentful Paint < 1s
  LCP: 2500,     // Largest Contentful Paint < 2.5s
  FID: 100,      // First Input Delay < 100ms
  CLS: 0.1,      // Cumulative Layout Shift < 0.1
  TTI: 3500,     // Time to Interactive < 3.5s
  TBT: 300,      // Total Blocking Time < 300ms
};
```

### 8.3 Load Testing
```javascript
// load-test.js
import { check } from 'k6';
import http from 'k6/http';

export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
  },
};
```

---

## Phase 9: Deployment & Monitoring (Week 9)

### 9.1 Production Build
**Optimizations:**
```json
// package.json scripts
{
  "build:analyze": "ANALYZE=true next build",
  "build:prod": "next build && next-sitemap",
  "build:docker": "docker build -t shepherd-gui .",
  "start:prod": "next start -p 3000"
}
```

### 9.2 Monitoring Setup
**Tools:**
- Performance monitoring with Web Vitals
- Error tracking with Sentry
- Analytics with Plausible/Umami
- Real User Monitoring (RUM)

**Implementation:**
```typescript
// src/lib/monitoring.ts
export const reportWebVitals = (metric: NextWebVitalsMetric) => {
  if (metric.label === 'web-vital') {
    // Send to analytics
    analytics.track('Web Vital', {
      name: metric.name,
      value: metric.value,
    });
  }
};
```

---

## Testing Strategy

### Unit Testing
- Every component has a test file
- Test user interactions
- Test error states
- Test loading states
- Mock external dependencies

### Integration Testing
- Test component communication
- Test store updates
- Test API calls
- Test WebSocket messages

### Performance Testing
- Measure render times
- Track re-render counts
- Monitor memory usage
- Check bundle sizes
- Test with CPU throttling

### Accessibility Testing
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- Focus management
- ARIA attributes

---

## Performance Checklist

### Initial Load
- [ ] First Contentful Paint < 1s
- [ ] Time to Interactive < 2s
- [ ] JavaScript bundle < 200KB gzipped
- [ ] CSS bundle < 50KB gzipped
- [ ] Image optimization with WebP/AVIF

### Runtime Performance
- [ ] 60 FPS animations
- [ ] < 100ms response to user input
- [ ] Virtual scrolling for long lists
- [ ] Debounced/throttled inputs
- [ ] Memoized expensive computations

### Network Optimization
- [ ] HTTP/2 or HTTP/3
- [ ] Brotli compression
- [ ] Service Worker caching
- [ ] Request batching
- [ ] WebSocket connection pooling

### Memory Management
- [ ] Component cleanup on unmount
- [ ] Event listener removal
- [ ] WeakMap for object caching
- [ ] Pagination for large datasets
- [ ] Lazy loading for images/components

---

## Success Metrics

### Performance KPIs
| Metric | Target | Measurement Tool |
|--------|--------|------------------|
| First Contentful Paint | < 1s | Lighthouse |
| Time to Interactive | < 2s | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Web Vitals |
| First Input Delay | < 100ms | Web Vitals |
| JavaScript Bundle Size | < 200KB | Webpack Analyzer |
| Test Coverage | > 80% | Jest Coverage |
| Accessibility Score | > 90 | Lighthouse |

### User Experience KPIs
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Sidebar Toggle | < 16ms | Performance API |
| Message Render | < 50ms | React DevTools |
| Modal Open | < 100ms | Performance API |
| API Response | < 500ms | Network Tab |
| WebSocket Latency | < 50ms | Custom Metrics |

---

## Risk Mitigation

### Performance Risks
- **Risk**: Large message history slowing down app
  - **Mitigation**: Virtual scrolling, pagination, message archiving

- **Risk**: WebSocket connection instability
  - **Mitigation**: Exponential backoff, message queuing, fallback to polling

- **Risk**: Bundle size growth
  - **Mitigation**: Regular bundle analysis, code splitting, tree shaking

### Technical Risks
- **Risk**: State management complexity
  - **Mitigation**: Clear store separation, comprehensive testing, TypeScript

- **Risk**: Memory leaks
  - **Mitigation**: Proper cleanup, WeakMap usage, monitoring tools

---

## Timeline Summary

| Week | Phase | Deliverables | Tests |
|------|-------|--------------|-------|
| 0 (Days 1-2) | Cleanup | Remove old components, backup | Migration tests |
| 1 | Foundation | Core layout, setup | Layout tests, performance baseline |
| 2 | State Management | Stores, API layer | Store tests, API mocks |
| 3 | Core Components | Sidebar, conversation | Component tests, integration |
| 4 | Real-time | WebSocket, live updates | WebSocket tests, real-time |
| 5 | Modals | Modal system, overlays | Modal tests, lazy loading |
| 6 | Advanced | Analytics, learning | Feature tests, data handling |
| 7 | Optimization | Performance tuning | Performance tests, benchmarks |
| 8 | Testing | Full test coverage | E2E, accessibility, load tests |
| 9 | Deployment | Production ready | Monitoring, deployment tests |

---

## Conclusion

This implementation plan provides a structured approach to building a high-performance, user-friendly GUI for Shepherd. By following this plan with its emphasis on performance optimization and comprehensive testing at each phase, we ensure a responsive and reliable user experience.

The phased approach allows for iterative development with continuous testing and optimization, reducing risks and ensuring quality throughout the development process.