/**
 * Conversation Store - Phase 5
 * 
 * Zustand store for managing conversation state, token usage,
 * and compacting operations.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

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
      (set, get) => ({
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
          set({ currentConversation: conversation }, false, 'setCurrentConversation'),

        updateConversation: (conversation) =>
          set((state) => ({
            conversations: state.conversations.map(c => 
              c.id === conversation.id ? conversation : c
            ),
            currentConversation: state.currentConversation?.id === conversation.id 
              ? conversation 
              : state.currentConversation
          }), false, 'updateConversation'),

        addConversation: (conversation) =>
          set((state) => ({
            conversations: [conversation, ...state.conversations]
          }), false, 'addConversation'),

        removeConversation: (conversationId) =>
          set((state) => ({
            conversations: state.conversations.filter(c => c.id !== conversationId),
            currentConversation: state.currentConversation?.id === conversationId 
              ? null 
              : state.currentConversation
          }), false, 'removeConversation'),

        setConversations: (conversations) =>
          set({ conversations }, false, 'setConversations'),

        // Token usage actions
        setTokenUsage: (usage) =>
          set({ tokenUsage: usage, lastUpdate: new Date().toISOString() }, false, 'setTokenUsage'),

        updateTokenUsage: (updates) =>
          set((state) => ({
            tokenUsage: state.tokenUsage ? { ...state.tokenUsage, ...updates } : null,
            lastUpdate: new Date().toISOString()
          }), false, 'updateTokenUsage'),

        // Compacting actions
        addCompactingResult: (result) =>
          set((state) => ({
            compactingHistory: [result, ...state.compactingHistory.slice(0, 19)] // Keep last 20
          }), false, 'addCompactingResult'),

        setCompactingHistory: (history) =>
          set({ compactingHistory: history }, false, 'setCompactingHistory'),

        // Status actions
        setLoading: (loading) =>
          set({ isLoading: loading }, false, 'setLoading'),

        setError: (error) =>
          set({ error }, false, 'setError'),

        setConnected: (connected) =>
          set({ isConnected: connected }, false, 'setConnected'),

        setLastUpdate: (timestamp) =>
          set({ lastUpdate: timestamp }, false, 'setLastUpdate'),

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
        }
      }),
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