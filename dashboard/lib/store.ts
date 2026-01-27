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

interface PlanQuestion {
  id: string
  question: string
  context: string
  options?: string[]
  multiselect?: boolean
}

interface FeatureSubPlan {
  feature: string
  description: string
  tasks: string[]
  components: string[]
  api_routes: string[]
  data_models: string[]
  dependencies: string[]
  assistant_tools: string[]
  estimated_effort: string
}

interface UIUXPreferences {
  style: string
  color_scheme: string
  target_audience: string
  inspiration_urls: string[]
  key_pages: string[]
  component_library: string
  accessibility_level: string
  responsive_priority: string
  special_requirements: string[]
}

interface DesignReference {
  type: 'url' | 'description' | 'style_preset'
  value: string
  notes: string
}

interface FactoryPlan {
  name: string
  domain: string
  description: string
  architecture: string
  assistants: string[]
  features: string[]
  compliance: string[]
  integrations: string[]
  data_models: string[]
  api_endpoints: string[]
  security_considerations: string[]
  estimated_complexity: string
  ui_ux?: UIUXPreferences
  feature_plans?: FeatureSubPlan[]
}

interface PlanResponse {
  status: 'questions' | 'plan'
  questions?: PlanQuestion[]
  plan?: FactoryPlan
}

interface SetupTask {
  id: string
  factory_id: string
  category: string  // infrastructure, credentials, integration, configuration, compliance
  title: string
  description: string
  status: string  // pending, in_progress, completed, skipped, blocked
  task_type: string  // manual, automated, external
  action_url?: string
  action_command?: string
  required: boolean
  order_index: number
  metadata: Record<string, any>
  completed_at?: string
  completed_by?: string
  notes?: string
  created_at: string
}

interface SetupProgress {
  total: number
  completed: number
  required_total: number
  required_completed: number
  percent: number
  by_category: Record<string, { total: number; completed: number }>
}

interface SetupData {
  factory_id: string
  tasks: SetupTask[]
  progress: SetupProgress
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
  reviewCode: (code: string, fileName: string, assistants: string[], factoryId?: string, useAI?: boolean) => Promise<ReviewResult | null>
  generateFix: (code: string, finding: Finding) => Promise<{ fixed_code: string; explanation: string } | null>
  planFactory: (name: string, domain: string, description: string, answers?: Record<string, string>, designReferences?: DesignReference[]) => Promise<PlanResponse | null>

  // Setup task actions
  getFactorySetup: (factoryId: string) => Promise<SetupData | null>
  updateSetupTask: (factoryId: string, taskId: string, updates: { status?: string; notes?: string }) => Promise<SetupTask | null>
  generateSetupTasks: (factoryId: string, plan: FactoryPlan) => Promise<SetupTask[] | null>

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

      // Only add if factory is valid
      if (factory && factory.id) {
        set(state => ({
          factories: [factory, ...state.factories.filter(f => f?.id !== factory.id)],
          isLoading: false
        }))
      } else {
        set({ isLoading: false })
      }

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
  reviewCode: async (code, fileName, assistants, factoryId, useAI = false) => {
    set({ isLoading: true, error: null })

    const endpoint = useAI ? `${API_URL}/api/review/ai` : `${API_URL}/api/review`

    try {
      const res = await fetch(endpoint, {
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
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || 'Failed to review code'
        throw new Error(errorMsg)
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

  // Generate fix for a finding
  generateFix: async (code, finding) => {
    try {
      const res = await fetch(`${API_URL}/api/fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          finding_title: finding.title,
          finding_description: finding.description,
          recommendation: finding.recommendation || '',
          language: 'python'
        })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to generate fix')
      }

      const result = await res.json()
      return {
        fixed_code: result.fixed_code,
        explanation: result.explanation
      }
    } catch (error) {
      console.error('Failed to generate fix:', error)
      return null
    }
  },

  // Plan factory with AI interview
  planFactory: async (name, domain, description, answers, designReferences) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          domain,
          description,
          answers: answers || null,
          design_references: designReferences || null
        })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to plan factory')
      }

      return await res.json()
    } catch (error) {
      console.error('Failed to plan factory:', error)
      return null
    }
  },

  // Get setup tasks for a factory
  getFactorySetup: async (factoryId) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/${factoryId}/setup`)
      if (!res.ok) {
        throw new Error('Failed to fetch setup tasks')
      }
      return await res.json()
    } catch (error) {
      console.error('Failed to get factory setup:', error)
      return null
    }
  },

  // Update a setup task
  updateSetupTask: async (factoryId, taskId, updates) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/${factoryId}/setup/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })

      if (!res.ok) {
        throw new Error('Failed to update task')
      }

      return await res.json()
    } catch (error) {
      console.error('Failed to update setup task:', error)
      return null
    }
  },

  // Generate setup tasks from a plan
  generateSetupTasks: async (factoryId, plan) => {
    try {
      const res = await fetch(`${API_URL}/api/factories/${factoryId}/setup/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan })
      })

      if (!res.ok) {
        throw new Error('Failed to generate setup tasks')
      }

      const result = await res.json()
      return result.tasks
    } catch (error) {
      console.error('Failed to generate setup tasks:', error)
      return null
    }
  },

  setWsConnected: (connected) => set({ wsConnected: connected }),
  setOnlineUsers: (users) => set({ onlineUsers: users }),
}))

// Export types for use in components
export type { DesignReference, UIUXPreferences, FactoryPlan, PlanQuestion, PlanResponse, FeatureSubPlan }

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
