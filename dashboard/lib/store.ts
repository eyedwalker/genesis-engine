import { create } from 'zustand'

interface Factory {
  id: string
  name: string
  domain: string
  status: 'active' | 'building' | 'paused' | 'error'
  featuresBuilt: number
  lastActivity: string
  assistants: string[]
}

interface Assistant {
  id: string
  name: string
  domain: string
  tags: string[]
  description: string
}

interface GenesisState {
  // Data
  factories: Factory[]
  assistants: Assistant[]
  isLoading: boolean
  error: string | null

  // WebSocket
  wsConnected: boolean
  onlineUsers: string[]

  // Actions
  loadData: () => Promise<void>
  createFactory: (factory: Partial<Factory>) => Promise<void>
  updateFactory: (id: string, updates: Partial<Factory>) => void
  deleteFactory: (id: string) => void

  // WebSocket actions
  setWsConnected: (connected: boolean) => void
  setOnlineUsers: (users: string[]) => void
}

export const useGenesisStore = create<GenesisState>((set, get) => ({
  // Initial state
  factories: [],
  assistants: [],
  isLoading: false,
  error: null,
  wsConnected: false,
  onlineUsers: [],

  // Actions
  loadData: async () => {
    set({ isLoading: true, error: null })

    try {
      // In production, this would fetch from the API
      // For now, use demo data
      await new Promise(resolve => setTimeout(resolve, 1000))

      set({
        factories: [
          {
            id: '1',
            name: 'Healthcare Platform',
            domain: 'healthcare',
            status: 'active',
            featuresBuilt: 45,
            lastActivity: '2 minutes ago',
            assistants: ['security', 'fhir', 'accessibility']
          },
          {
            id: '2',
            name: 'E-Commerce Engine',
            domain: 'e-commerce',
            status: 'active',
            featuresBuilt: 32,
            lastActivity: '15 minutes ago',
            assistants: ['security', 'pci_dss', 'performance']
          },
        ],
        assistants: [
          {
            id: 'security',
            name: 'Security Reviewer',
            domain: 'security',
            tags: ['owasp', 'authentication', 'encryption'],
            description: 'OWASP Top 10, authentication, authorization'
          },
          // Add more assistants...
        ],
        isLoading: false
      })
    } catch (error) {
      set({ error: 'Failed to load data', isLoading: false })
    }
  },

  createFactory: async (factory) => {
    set({ isLoading: true })

    try {
      // In production, this would call the API
      await new Promise(resolve => setTimeout(resolve, 2000))

      const newFactory: Factory = {
        id: String(Date.now()),
        name: factory.name || 'New Factory',
        domain: factory.domain || 'custom',
        status: 'building',
        featuresBuilt: 0,
        lastActivity: 'Just now',
        assistants: factory.assistants || ['security', 'performance']
      }

      set(state => ({
        factories: [...state.factories, newFactory],
        isLoading: false
      }))
    } catch (error) {
      set({ error: 'Failed to create factory', isLoading: false })
    }
  },

  updateFactory: (id, updates) => {
    set(state => ({
      factories: state.factories.map(f =>
        f.id === id ? { ...f, ...updates } : f
      )
    }))
  },

  deleteFactory: (id) => {
    set(state => ({
      factories: state.factories.filter(f => f.id !== id)
    }))
  },

  setWsConnected: (connected) => set({ wsConnected: connected }),
  setOnlineUsers: (users) => set({ onlineUsers: users }),
}))
