# GUI Migration Checklist

## Pre-Migration Backup
- [ ] Create backup branch: `backup/old-gui-implementation`
- [ ] Archive current components to `archive/old-gui/`
- [ ] Document current component dependencies
- [ ] Export current test coverage report
- [ ] Save bundle analysis report

## Phase 0: Cleanup (Days 1-2)

### Components to Remove
- [ ] **Layout Components**
  - [ ] `artifacts-panel.tsx` - Old right panel
  - [ ] `three-panel-layout.tsx` - Old layout system
  - [ ] `conversation-area.tsx` - Old implementation
  - [ ] `sidebar.tsx` - Old non-collapsible version

- [ ] **Feature Components**
  - [ ] `message-input.tsx` - Replaced with InputArea
  - [ ] `agent-status.tsx` - Old agent display
  - [ ] `agent-collaboration.tsx` - Old visualization
  - [ ] `communication-flow.tsx` - Outdated
  - [ ] `memory-flow.tsx` - Outdated visualization
  - [ ] `learning-progress.tsx` - Moving to modal
  - [ ] `performance-metrics.tsx` - Integrated into ResourceUsage
  - [ ] `project-folder-selector.tsx` - Moving to settings modal

- [ ] **App Structure**
  - [ ] `src/app/page.tsx` - Old home page
  - [ ] `src/app/layout.tsx` - To be recreated

- [ ] **Styles to Remove**
  - [ ] `panels.css` - Panel-specific styles
  - [ ] `resizable.css` - Resizing styles
  - [ ] Unused CSS classes in `globals.css`

- [ ] **Utilities to Remove**
  - [ ] `panel-resize.ts` - Panel resizing logic
  - [ ] `drag-handlers.ts` - Drag functionality
  - [ ] Deprecated hooks

- [ ] **Tests to Remove**
  - [ ] All tests for removed components
  - [ ] Integration tests for old layout
  - [ ] E2E tests for old workflows

### Dependencies to Remove
- [ ] `react-resizable-panels` - Old panel system
- [ ] `react-split-pane` - Old split implementation
- [ ] `@dnd-kit/sortable` - If not using drag-drop
- [ ] `react-beautiful-dnd` - Old DnD library
- [ ] Any unused icon libraries

### Files to Keep/Migrate
- [ ] **UI Components** (`src/components/ui/`)
  - [ ] Button
  - [ ] Input
  - [ ] Card
  - [ ] Dialog
  - [ ] Dropdown
  - [ ] All shadcn/ui components

- [ ] **Providers** (`src/components/providers/`)
  - [ ] ThemeProvider - Update for new layout
  - [ ] WebSocketProvider - Enhance with batching

- [ ] **Libraries** (`src/lib/`)
  - [ ] API client - Enhance with caching
  - [ ] Utils - Keep and optimize
  - [ ] Constants - Update as needed

- [ ] **Assets**
  - [ ] Shepherd.png logo
  - [ ] Any other images/icons

## Phase 1: New Implementation

### Core Layout Components
- [ ] `AppLayout.tsx` - Main layout container
- [ ] `Sidebar.tsx` - Collapsible sidebar
- [ ] `ConversationArea.tsx` - Main chat area

### Sidebar Components
- [ ] `QuickActions.tsx` - New, History, Export
- [ ] `WorkflowControls.tsx` - Mode and settings
- [ ] `AgentMonitor.tsx` - Live agent status
- [ ] `ResourceUsage.tsx` - Metrics display

### Conversation Components
- [ ] `MessageList.tsx` - Virtual scrolling
- [ ] `Message.tsx` - Individual messages
- [ ] `InputArea.tsx` - Multi-line input

### Modal Components
- [ ] `ModalProvider.tsx` - Modal system
- [ ] `ArtifactModal.tsx` - Code/file viewer
- [ ] `AnalyticsModal.tsx` - Dashboard
- [ ] `HistoryModal.tsx` - Conversation history
- [ ] `SettingsModal.tsx` - All settings
- [ ] `ExportModal.tsx` - Export configuration

### State Management
- [ ] `uiStore.ts` - UI state
- [ ] `conversationStore.ts` - Chat state
- [ ] `workflowStore.ts` - Workflow state

### Performance Features
- [ ] Virtual scrolling implementation
- [ ] Code splitting setup
- [ ] Lazy loading configuration
- [ ] Service worker setup
- [ ] WebSocket batching

## Testing Requirements

### Unit Tests
- [ ] All new components have tests
- [ ] Store actions tested
- [ ] Hooks tested
- [ ] Utils tested

### Integration Tests
- [ ] Component interactions
- [ ] Store updates
- [ ] API calls
- [ ] WebSocket messages

### Performance Tests
- [ ] Bundle size < 200KB
- [ ] FCP < 1s
- [ ] TTI < 2s
- [ ] 60 FPS animations

### Accessibility Tests
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] WCAG 2.1 AA compliance

## Validation Checklist

### Before Going Live
- [ ] All old components removed
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] All tests passing
- [ ] Performance metrics met
- [ ] Accessibility audit passed
- [ ] Cross-browser tested
- [ ] Mobile responsive
- [ ] Documentation updated

### Post-Migration
- [ ] User acceptance testing
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Analytics configured
- [ ] Backup strategy confirmed

## Rollback Plan

If issues arise:
1. [ ] Stop deployment
2. [ ] Checkout backup branch
3. [ ] Restore from `archive/old-gui/`
4. [ ] Revert package.json changes
5. [ ] Clean install dependencies
6. [ ] Verify old GUI works
7. [ ] Document issues for retry

## Sign-off

- [ ] Development team approval
- [ ] QA approval
- [ ] Performance benchmarks met
- [ ] Security review passed
- [ ] Documentation complete
- [ ] Ready for production

---

**Note**: Check off items as completed. Any unchecked items must be addressed before proceeding to the next phase.