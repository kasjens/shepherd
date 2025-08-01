import { create } from 'zustand'
import { ChatSession, ChatMessage, Artifact, Theme } from '@/lib/types'
import { api } from '@/lib/api'
import { useProjectStore } from './project-store'

interface ChatStore {
  // State
  sessions: ChatSession[]
  currentSessionId: string | null
  theme: Theme
  isLoading: boolean
  error: string | null

  // Actions
  createSession: () => string
  switchSession: (sessionId: string) => void
  sendMessage: (content: string) => Promise<void>
  addMessage: (message: ChatMessage) => void
  setTheme: (theme: Theme) => void
  clearError: () => void
}

const generateId = () => Math.random().toString(36).substr(2, 9)

export const useChatStore = create<ChatStore>((set, get) => ({
  // Initial state
  sessions: [],
  currentSessionId: null,
  theme: 'light',
  isLoading: false,
  error: null,

  // Create a new chat session
  createSession: () => {
    const newSession: ChatSession = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      artifacts: [],
      created_at: new Date(),
      updated_at: new Date(),
    }

    set(state => ({
      sessions: [...state.sessions, newSession],
      currentSessionId: newSession.id,
    }))

    return newSession.id
  },

  // Switch to a different session
  switchSession: (sessionId: string) => {
    const { sessions } = get()
    const session = sessions.find(s => s.id === sessionId)
    
    if (session) {
      set({ currentSessionId: sessionId })
    }
  },

  // Send a message and get AI response
  sendMessage: async (content: string) => {
    const { currentSessionId, sessions, createSession } = get()
    
    // Create session if none exists
    let sessionId = currentSessionId
    if (!sessionId) {
      sessionId = createSession()
    }

    const session = sessions.find(s => s.id === sessionId)
    if (!session) return

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      sender: 'user',
      content,
      timestamp: new Date(),
    }

    set(state => ({
      sessions: state.sessions.map(s =>
        s.id === sessionId
          ? { 
              ...s, 
              messages: [...s.messages, userMessage],
              updated_at: new Date(),
              title: s.messages.length === 0 ? content.substring(0, 50) + (content.length > 50 ? '...' : '') : s.title
            }
          : s
      ),
      isLoading: true,
      error: null,
    }))

    try {
      // Get project folder from project store
      const { projectFolder } = useProjectStore.getState()
      
      // Send to API with project folder context
      const result = await api.sendMessage(content, sessionId, projectFolder || undefined)
      
      // Create AI response
      const aiMessage: ChatMessage = {
        id: generateId(),
        sender: 'ai',
        content: `I'll help you with that request. Let me analyze and process your requirements...

🔄 **Analyzing request...**
- Complexity: ${Math.random() * 1}
- Pattern: ${result.pattern}
- Status: ${result.status}

**Execution Results:**
- Total Time: ${result.total_execution_time}s
- Steps Completed: ${result.steps.filter(s => s.status === 'completed').length}/${result.steps.length}

${result.output.response || 'Task completed successfully.'}`,
        timestamp: new Date(),
        artifacts: result.output.artifacts || [],
      }

      // Update session with AI response
      set(state => ({
        sessions: state.sessions.map(s =>
          s.id === sessionId
            ? { 
                ...s, 
                messages: [...s.messages, aiMessage],
                artifacts: [...s.artifacts, ...(result.output.artifacts || [])],
                updated_at: new Date(),
              }
            : s
        ),
        isLoading: false,
      }))
    } catch (error) {
      console.error('Failed to send message:', error)
      
      const errorMessage: ChatMessage = {
        id: generateId(),
        sender: 'ai',
        content: `❌ Sorry, I encountered an error while processing your request: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      }

      set(state => ({
        sessions: state.sessions.map(s =>
          s.id === sessionId
            ? { ...s, messages: [...s.messages, errorMessage], updated_at: new Date() }
            : s
        ),
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }))
    }
  },

  // Add a message directly (for manual updates)
  addMessage: (message: ChatMessage) => {
    const { currentSessionId } = get()
    if (!currentSessionId) return

    set(state => ({
      sessions: state.sessions.map(s =>
        s.id === currentSessionId
          ? { ...s, messages: [...s.messages, message], updated_at: new Date() }
          : s
      ),
    }))
  },

  // Set theme
  setTheme: (theme: Theme) => {
    set({ theme })
    localStorage.setItem('shepherd-theme', theme)
    
    // Update document class
    document.documentElement.className = theme === 'dark' ? 'dark' : theme === 'blue' ? 'theme-blue' : ''
  },

  // Clear error
  clearError: () => {
    set({ error: null })
  },
}))

// Initialize theme from localStorage
if (typeof window !== 'undefined') {
  const savedTheme = localStorage.getItem('shepherd-theme') as Theme
  if (savedTheme) {
    useChatStore.getState().setTheme(savedTheme)
  }
}