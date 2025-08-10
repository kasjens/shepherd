/**
 * Conversation Store - Phase 5
 * 
 * Zustand store for managing conversation state, token usage,
 * and compacting operations.
 */

import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { shallow } from 'zustand/shallow';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  last_activity: string;
  workflow_count: number;
  active: boolean;
}

interface TokenUsage {
  conversation_id: string;
  current_tokens: number;
  threshold: number;
  usage_percentage: number;
  needs_compacting: boolean;
  workflow_count: number;
  last_updated: string;
  warning_level: 'none' | 'warning' | 'critical';
}

interface CompactingHistory {
  timestamp: string;
  strategy: string;
  reduction: number;
  success: boolean;
}

interface ConversationState {
  // Current state
  currentConversation: Conversation | null;
  conversations: Conversation[];
  tokenUsage: TokenUsage | null;
  compactingHistory: CompactingHistory[];
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // WebSocket state
  isConnected: boolean;
  lastUpdate: string | null;
  
  // Actions
  setCurrentConversation: (conversation: Conversation | null) => void;
  updateConversation: (conversation: Conversation) => void;
  addConversation: (conversation: Conversation) => void;
  removeConversation: (conversationId: string) => void;
  setConversations: (conversations: Conversation[]) => void;
  
  // Token usage actions
  setTokenUsage: (usage: TokenUsage) => void;
  updateTokenUsage: (updates: Partial<TokenUsage>) => void;
  
  // Compacting actions
  addCompactingResult: (result: CompactingHistory) => void;
  setCompactingHistory: (history: CompactingHistory[]) => void;
  
  // Status actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConnected: (connected: boolean) => void;
  setLastUpdate: (timestamp: string) => void;
  
  // API actions
  fetchConversations: () => Promise<void>;
  fetchTokenUsage: (conversationId: string) => Promise<void>;
  compactConversation: (conversationId: string, strategy: string) => Promise<boolean>;
}

export const useConversationStore = create<ConversationState>()(
  devtools(
    persist(
      immer(
        subscribeWithSelector((set, get) => ({
        // Initial state
        currentConversation: null,
        conversations: [],
        tokenUsage: null,
        compactingHistory: [],
        isLoading: false,
        error: null,
        isConnected: false,
        lastUpdate: null,

        // Basic state actions
        setCurrentConversation: (conversation) =>
          set((state) => {
            state.currentConversation = conversation;
          }),

        updateConversation: (conversation) =>
          set((state) => {
            const index = state.conversations.findIndex(c => c.id === conversation.id);
            if (index !== -1) {
              state.conversations[index] = conversation;
            }
            if (state.currentConversation?.id === conversation.id) {
              state.currentConversation = conversation;
            }
          }),

        addConversation: (conversation) =>
          set((state) => {
            state.conversations.unshift(conversation);
          }),

        removeConversation: (conversationId) =>
          set((state) => {
            state.conversations = state.conversations.filter(c => c.id !== conversationId);
            if (state.currentConversation?.id === conversationId) {
              state.currentConversation = null;
            }
          }),

        setConversations: (conversations) =>
          set((state) => {
            state.conversations = conversations;
          }),

        // Token usage actions
        setTokenUsage: (usage) =>
          set((state) => {
            state.tokenUsage = usage;
            state.lastUpdate = new Date().toISOString();
          }),

        updateTokenUsage: (updates) =>
          set((state) => {
            if (state.tokenUsage) {
              Object.assign(state.tokenUsage, updates);
            }
            state.lastUpdate = new Date().toISOString();
          }),

        // Compacting actions
        addCompactingResult: (result) =>
          set((state) => {
            state.compactingHistory.unshift(result);
            // Keep only last 20 results
            state.compactingHistory = state.compactingHistory.slice(0, 20);
          }),

        setCompactingHistory: (history) =>
          set((state) => {
            state.compactingHistory = history;
          }),

        // Status actions
        setLoading: (loading) =>
          set((state) => {
            state.isLoading = loading;
          }),

        setError: (error) =>
          set((state) => {
            state.error = error;
          }),

        setConnected: (connected) =>
          set((state) => {
            state.isConnected = connected;
          }),

        setLastUpdate: (timestamp) =>
          set((state) => {
            state.lastUpdate = timestamp;
          }),

        // API actions
        fetchConversations: async () => {
          const { setLoading, setError, setConversations } = get();
          
          setLoading(true);
          setError(null);
          
          try {
            const response = await fetch('/api/conversations');
            if (!response.ok) {
              throw new Error('Failed to fetch conversations');
            }
            
            const conversationIds: string[] = await response.json();
            
            // Convert IDs to conversation objects (simplified)
            const conversations: Conversation[] = conversationIds.map(id => ({
              id,
              title: `Conversation ${id}`,
              created_at: new Date().toISOString(),
              last_activity: new Date().toISOString(),
              workflow_count: 0,
              active: true
            }));
            
            setConversations(conversations);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Unknown error');
            console.error('Failed to fetch conversations:', error);
          } finally {
            setLoading(false);
          }
        },

        fetchTokenUsage: async (conversationId: string) => {
          const { setError, setTokenUsage } = get();
          
          try {
            const response = await fetch(`/api/conversations/${conversationId}/token-usage`);
            if (!response.ok) {
              throw new Error('Failed to fetch token usage');
            }
            
            const usage: TokenUsage = await response.json();
            setTokenUsage(usage);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to fetch token usage');
            console.error('Failed to fetch token usage:', error);
          }
        },

        compactConversation: async (conversationId: string, strategy: string): Promise<boolean> => {
          const { setError, addCompactingResult, fetchTokenUsage } = get();
          
          try {
            const response = await fetch(`/api/conversations/${conversationId}/compact`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                conversation_id: conversationId,
                strategy: strategy
              })
            });

            if (!response.ok) {
              throw new Error('Compacting request failed');
            }

            const result = await response.json();
            
            // Add to history
            addCompactingResult({
              timestamp: result.timestamp,
              strategy: result.strategy_used,
              reduction: result.reduction_percentage,
              success: result.success
            });

            // Refresh token usage
            await fetchTokenUsage(conversationId);

            return result.success;
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Compacting failed');
            console.error('Compacting failed:', error);
            return false;
          }
        }))
      ),
      {
        name: 'conversation-store',
        partialize: (state) => ({
          // Only persist certain parts of the state
          currentConversation: state.currentConversation,
          conversations: state.conversations,
          compactingHistory: state.compactingHistory
        })
      }
    ),
    { name: 'conversation-store' }
  )
);

// Performance-optimized selectors
export const conversationSelectors = {
  // Current conversation
  current: (state: ConversationState) => ({
    currentConversation: state.currentConversation,
    tokenUsage: state.tokenUsage,
  }),
  
  // Conversations list
  conversations: (state: ConversationState) => ({
    conversations: state.conversations,
    totalCount: state.conversations.length,
    activeCount: state.conversations.filter(c => c.active).length,
  }),
  
  // Status
  status: (state: ConversationState) => ({
    isLoading: state.isLoading,
    isConnected: state.isConnected,
    error: state.error,
    lastUpdate: state.lastUpdate,
  }),
  
  // Compacting
  compacting: (state: ConversationState) => ({
    compactingHistory: state.compactingHistory,
    recentCompacting: state.compactingHistory.slice(0, 5),
    totalCompactions: state.compactingHistory.length,
    successRate: state.compactingHistory.length > 0 
      ? state.compactingHistory.filter(h => h.success).length / state.compactingHistory.length 
      : 0,
  }),
};

// Typed hooks for better DX
export const useCurrentConversation = () => useConversationStore(conversationSelectors.current, shallow);
export const useConversations = () => useConversationStore(conversationSelectors.conversations, shallow);
export const useConversationStatus = () => useConversationStore(conversationSelectors.status, shallow);
export const useCompactingHistory = () => useConversationStore(conversationSelectors.compacting, shallow);