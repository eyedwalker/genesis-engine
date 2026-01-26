import { create } from 'zustand'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Factory {
  id: string
  name: string
  domain: string
  description: string
  status: string
  features_built: number
  created_at: string
  updated_at: string
  assistants: string[]
}

interface Assistant {
  id: string
  name: string
  domain: string
  tags: string[]
  description: string
  methods_count: number
}

interface Finding {
  id: string
  severity: string
  title: string
  description: string
  assistant: string
  line?: number
  code_snippet?: string
  recommendation?: string
}

interface ReviewResult {
  review_id: string
  status: string
  file_name: string
  language: string
  findings: Finding[]
  summary: {
    critical: number
    high: number
    medium: number
    low: number
  }
  assistants_used: string[]
}

interface Stats {
  factories: { total: number; active: number }
  features: { total: number }
  reviews: { total: number; findings: Record<string, number> }
  assistants: { loaded: number }
}

interface GenesisState {
  // Data
  factories: Factory[]
  assistants: Assistant[]
  stats: Stats | null
  lastReview: ReviewResult | null
  isLoading: boolean
  error: string | null

  // WebSocket
  wsConnected: boolean
  onlineUsers: any[]

  // Actions
  loadData: () => Promise<void>
  loadStats: () => Promise<void>
  createFactory: (data: { name: string; domain: string; description: string; assistants: string[] }) => Promise<Factory | null>
  updateFactory: (id: string, updates: Partial<Factory>) => Promise<void>
  deleteFactory: (id: string) => Promise<void>
  reviewCode: (code: string, fileName: string, assistants: string[], factoryId?: string) => Promise<ReviewResult | null>

  // WebSocket actions
  setWsConnected: (connected: boolean) => void
  setOnlineUsers: (users: any[]) => void
}

export const useGenesisStore = create<GenesisState>((set, get) => ({
  // Initial state
  factories: [],
  assistants: [],
  stats: null,
  lastReview: null,
  isLoading: false,
  error: null,
  wsConnected: false,
  onlineUsers: [],

  // Load all data from API
  loadData: async () => {
    set({ isLoading: true, error: null })

    try {
      // Fetch factories and assistants in parallel
      const [factoriesRes, assistantsRes] = await Promise.all([
        fetch(`${API_URL}/api/factories`),
        fetch(`${API_URL}/api/assistants`)
      ])

      if (!factoriesRes.ok || !assistantsRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const factories = await factoriesRes.json()
      const assistants = await assistantsRes.json()

      set({
        factories,
        assistants,
        isLoading: false
      })

      // Also load stats
      get().loadStats()
    } catch (error) {
      console.error('Failed to load data:', error)
      set({ error: 'Failed to connect to API. Is the server running?', isLoading: false })
    }
  },

  // Load statistics
  loadStats: async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`)
      if (res.ok) {
        const stats = await res.json()
        set({ stats })
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  },

  // Create a new factory
  createFactory: async (data) => {
    set({ isLoading: true, error: null })

    try {
      const res = await fetch(`${API_URL}/api/factories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (!res.ok) {
        throw new Error('Failed to create factory')
      }

      const factory = await res.json()

      set(state => ({
        factories: [factory, ...state.factories],
        isLoading: false
      }))

      // Refresh stats
      get().loadStats()

      return factory
    } catch (error) {
      console.error('Failed to create factory:', error)
      set({ error: 'Failed to create factory', isLoading: false })
      return null
    }
  },

  // Update factory
  updateFactory: async (id, updates) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })

      if (res.ok) {
        const updated = await res.json()
        set(state => ({
          factories: state.factories.map(f => f.id === id ? updated : f)
        }))
      }
    } catch (error) {
      console.error('Failed to update factory:', error)
    }
  },

  // Delete factory
  deleteFactory: async (id) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/${id}`, {
        method: 'DELETE'
      })

      if (res.ok) {
        set(state => ({
          factories: state.factories.filter(f => f.id !== id)
        }))
        get().loadStats()
      }
    } catch (error) {
      console.error('Failed to delete factory:', error)
    }
  },

  // Review code using assistants
  reviewCode: async (code, fileName, assistants, factoryId) => {
    set({ isLoading: true, error: null })

    try {
      const res = await fetch(`${API_URL}/api/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          file_name: fileName,
          assistants,
          factory_id: factoryId
        })
      })

      if (!res.ok) {
        throw new Error('Failed to review code')
      }

      const result = await res.json()

      set({ lastReview: result, isLoading: false })

      // Refresh stats after review
      get().loadStats()

      return result
    } catch (error) {
      console.error('Failed to review code:', error)
      set({ error: 'Failed to review code', isLoading: false })
      return null
    }
  },

  setWsConnected: (connected) => set({ wsConnected: connected }),
  setOnlineUsers: (users) => set({ onlineUsers: users }),
}))

// Helper to format relative time
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return `${days} day${days > 1 ? 's' : ''} ago`
}
