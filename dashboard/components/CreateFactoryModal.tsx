'use client'

import { useState } from 'react'
import { X, Loader2, CheckCircle, Zap, Sparkles, ChevronRight, MessageSquare, FileText, ArrowLeft, Link2, Palette, Plus, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import { useGenesisStore, type DesignReference } from '@/lib/store'

interface CreateFactoryModalProps {
  isOpen: boolean
  onClose: () => void
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

const PRESET_DOMAINS = [
  { id: 'healthcare', name: 'Healthcare', description: 'FHIR, HIPAA, patient data' },
  { id: 'ecommerce', name: 'E-Commerce', description: 'Payments, inventory, orders' },
  { id: 'fintech', name: 'FinTech', description: 'Banking, payments, compliance' },
  { id: 'logistics', name: 'Logistics', description: 'Shipping, tracking, IoT' },
  { id: 'saas', name: 'SaaS Platform', description: 'Multi-tenant, subscriptions' },
  { id: 'custom', name: 'Custom', description: 'Describe your domain' },
]

const STEP_LABELS = [
  'Domain',
  'Description',
  'Interview',
  'Review Plan',
  'Create'
]

const STYLE_PRESETS = [
  { id: 'modern', name: 'Modern & Clean', description: 'Minimal, whitespace, sharp edges' },
  { id: 'playful', name: 'Playful & Colorful', description: 'Rounded corners, gradients, fun' },
  { id: 'corporate', name: 'Corporate & Professional', description: 'Conservative, trustworthy, formal' },
  { id: 'minimal', name: 'Minimal & Elegant', description: 'Simple, refined, typography-focused' },
  { id: 'tech', name: 'Tech & Futuristic', description: 'Dark mode, neon accents, glassmorphism' },
  { id: 'custom', name: 'Custom', description: 'Describe your own style' },
]

export function CreateFactoryModal({ isOpen, onClose }: CreateFactoryModalProps) {
  const [step, setStep] = useState(1)
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [factoryName, setFactoryName] = useState('')
  const [description, setDescription] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [isPlanning, setIsPlanning] = useState(false)

  // Interview state
  const [questions, setQuestions] = useState<PlanQuestion[]>([])
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({})

  // Plan state
  const [plan, setPlan] = useState<FactoryPlan | null>(null)

  // Design reference state
  const [selectedStylePreset, setSelectedStylePreset] = useState<string | null>(null)
  const [designUrls, setDesignUrls] = useState<{ url: string; notes: string }[]>([])
  const [newUrl, setNewUrl] = useState('')
  const [newUrlNotes, setNewUrlNotes] = useState('')

  const { createFactory, planFactory, generateSetupTasks } = useGenesisStore()

  if (!isOpen) return null

  const resetModal = () => {
    setStep(1)
    setSelectedDomain(null)
    setFactoryName('')
    setDescription('')
    setQuestions([])
    setAnswers({})
    setPlan(null)
    setSelectedStylePreset(null)
    setDesignUrls([])
    setNewUrl('')
    setNewUrlNotes('')
  }

  const handleClose = () => {
    resetModal()
    onClose()
  }

  // Build design references array
  const buildDesignReferences = (): DesignReference[] => {
    const refs: DesignReference[] = []

    // Add style preset if selected
    if (selectedStylePreset && selectedStylePreset !== 'custom') {
      const preset = STYLE_PRESETS.find(p => p.id === selectedStylePreset)
      if (preset) {
        refs.push({
          type: 'style_preset',
          value: preset.name,
          notes: preset.description
        })
      }
    }

    // Add design URLs
    for (const item of designUrls) {
      refs.push({
        type: 'url',
        value: item.url,
        notes: item.notes
      })
    }

    return refs
  }

  // Add a design URL
  const handleAddUrl = () => {
    if (!newUrl.trim()) return

    // Basic URL validation
    try {
      new URL(newUrl)
    } catch {
      toast.error('Please enter a valid URL')
      return
    }

    setDesignUrls([...designUrls, { url: newUrl.trim(), notes: newUrlNotes.trim() }])
    setNewUrl('')
    setNewUrlNotes('')
    toast.success('Design reference added')
  }

  // Remove a design URL
  const handleRemoveUrl = (index: number) => {
    setDesignUrls(designUrls.filter((_, i) => i !== index))
  }

  // Step 2 → Step 3: Get interview questions from AI
  const handleStartInterview = async () => {
    setIsPlanning(true)

    try {
      const designRefs = buildDesignReferences()
      const result = await planFactory(factoryName, selectedDomain!, description, undefined, designRefs.length > 0 ? designRefs : undefined)

      if (result && result.status === 'questions' && result.questions) {
        setQuestions(result.questions)
        setStep(3)
      } else {
        toast.error('Failed to generate interview questions')
      }
    } catch (error) {
      toast.error('Failed to start interview')
    }

    setIsPlanning(false)
  }

  // Step 3 → Step 4: Submit answers and get plan
  const handleSubmitAnswers = async () => {
    // Check all questions are answered
    const unanswered = questions.filter(q => {
      const answer = answers[q.id]
      if (Array.isArray(answer)) return answer.length === 0
      return !answer || (typeof answer === 'string' && answer.trim() === '')
    })
    if (unanswered.length > 0) {
      toast.error('Please answer all questions')
      return
    }

    setIsPlanning(true)

    try {
      // Convert array answers to comma-separated strings for API
      const stringAnswers: Record<string, string> = {}
      for (const [key, value] of Object.entries(answers)) {
        stringAnswers[key] = Array.isArray(value) ? value.join(', ') : value
      }

      const designRefs = buildDesignReferences()
      const result = await planFactory(factoryName, selectedDomain!, description, stringAnswers, designRefs.length > 0 ? designRefs : undefined)

      if (result && result.status === 'plan' && result.plan) {
        setPlan(result.plan)
        setStep(4)
      } else {
        toast.error('Failed to generate plan')
      }
    } catch (error) {
      toast.error('Failed to generate plan')
    }

    setIsPlanning(false)
  }

  // Step 4 → Create: Create factory with plan
  const handleCreate = async () => {
    if (!plan) return

    setIsCreating(true)
    setStep(5) // Show creating state

    const result = await createFactory({
      name: plan.name,
      domain: plan.domain,
      description: plan.description,
      assistants: plan.assistants
    })

    if (result && result.id) {
      // Generate setup tasks from the plan
      const tasks = await generateSetupTasks(result.id, plan)

      setIsCreating(false)

      if (tasks && tasks.length > 0) {
        toast.success(`Factory created with ${tasks.length} setup tasks!`)
      } else {
        toast.success('Factory created successfully!')
      }

      handleClose()
    } else {
      setIsCreating(false)
      setStep(4) // Go back to review
      toast.error('Failed to create factory')
    }
  }

  const canProceedStep1 = selectedDomain && factoryName.trim().length > 0
  const canProceedStep2 = description.trim().length > 10
  const canProceedStep3 = questions.every(q => {
    const answer = answers[q.id]
    if (Array.isArray(answer)) {
      return answer.length > 0
    }
    return answer && typeof answer === 'string' && answer.trim().length > 0
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-3xl max-h-[90vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl animate-fade-in flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Create Factory with AI Planning</h2>
              <p className="text-sm text-slate-400">Step {step} of 5: {STEP_LABELS[step - 1]}</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-4">
          <div className="flex items-center gap-2">
            {STEP_LABELS.map((label, i) => (
              <div key={label} className="flex items-center flex-1">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                  i + 1 < step ? "bg-green-500 text-white" :
                  i + 1 === step ? "bg-purple-600 text-white" :
                  "bg-slate-800 text-slate-500"
                )}>
                  {i + 1 < step ? <CheckCircle className="w-4 h-4" /> : i + 1}
                </div>
                {i < STEP_LABELS.length - 1 && (
                  <div className={cn(
                    "flex-1 h-1 mx-2 rounded",
                    i + 1 < step ? "bg-green-500" : "bg-slate-800"
                  )} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2">
            {STEP_LABELS.map((label, i) => (
              <span key={label} className={cn(
                "text-xs",
                i + 1 === step ? "text-purple-400" : "text-slate-500"
              )}>
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Step 1: Domain & Name */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Domain</label>
                <div className="grid grid-cols-3 gap-3">
                  {PRESET_DOMAINS.map(domain => (
                    <button
                      key={domain.id}
                      onClick={() => setSelectedDomain(domain.id)}
                      className={cn(
                        'p-4 rounded-xl border text-left transition-all',
                        selectedDomain === domain.id
                          ? 'bg-purple-600/20 border-purple-500 text-purple-400'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      )}
                    >
                      <p className="font-medium">{domain.name}</p>
                      <p className="text-xs text-slate-500 mt-1">{domain.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Factory Name</label>
                <input
                  type="text"
                  value={factoryName}
                  onChange={(e) => setFactoryName(e.target.value)}
                  placeholder="e.g., My Healthcare Platform"
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                />
              </div>
            </div>
          )}

          {/* Step 2: Description & Design */}
          {step === 2 && (
            <div className="space-y-6">
              {/* Project Description */}
              <div>
                <label className="block text-sm font-medium mb-2">Describe Your Project</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your project in detail. What problem are you solving? What features do you need? Who are your users? What integrations are required?"
                  rows={5}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none"
                />
                <p className="text-xs text-slate-500 mt-2">
                  Be as detailed as possible - the AI will use this to generate tailored interview questions.
                </p>
              </div>

              {/* UI/UX Style Preset */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Palette className="w-4 h-4 text-purple-400" />
                  <label className="text-sm font-medium">UI/UX Style (Optional)</label>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {STYLE_PRESETS.map(preset => (
                    <button
                      key={preset.id}
                      onClick={() => setSelectedStylePreset(
                        selectedStylePreset === preset.id ? null : preset.id
                      )}
                      className={cn(
                        'p-3 rounded-lg border text-left transition-all text-sm',
                        selectedStylePreset === preset.id
                          ? 'bg-purple-600/20 border-purple-500 text-purple-300'
                          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                      )}
                    >
                      <p className="font-medium">{preset.name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{preset.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Design Reference URLs */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Link2 className="w-4 h-4 text-cyan-400" />
                  <label className="text-sm font-medium">Design References (Optional)</label>
                </div>
                <p className="text-xs text-slate-500 mb-3">
                  Add URLs to design inspirations: Figma files, Dribbble shots, Builder.io projects, or any website you like
                </p>

                {/* Existing URLs */}
                {designUrls.length > 0 && (
                  <div className="space-y-2 mb-3">
                    {designUrls.map((item, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-slate-800/50 border border-slate-700 rounded-lg">
                        <Link2 className="w-4 h-4 text-slate-500 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-cyan-400 truncate">{item.url}</p>
                          {item.notes && (
                            <p className="text-xs text-slate-500 truncate">{item.notes}</p>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemoveUrl(index)}
                          className="p-1 hover:bg-red-500/20 rounded"
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add new URL */}
                <div className="space-y-2">
                  <input
                    type="url"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    placeholder="https://figma.com/file/... or https://dribbble.com/..."
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500/50 text-sm"
                  />
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newUrlNotes}
                      onChange={(e) => setNewUrlNotes(e.target.value)}
                      placeholder="Notes (e.g., 'I like the color scheme')"
                      className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500/50 text-sm"
                    />
                    <button
                      onClick={handleAddUrl}
                      disabled={!newUrl.trim()}
                      className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg text-sm flex items-center gap-1"
                    >
                      <Plus className="w-4 h-4" />
                      Add
                    </button>
                  </div>
                </div>
              </div>

              {/* Info Box */}
              <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-medium text-purple-400">AI-Powered Planning</span>
                </div>
                <p className="text-sm text-slate-400">
                  After this step, Claude will interview you with targeted questions about your requirements
                  and UI/UX preferences, then generate a comprehensive factory plan for your review.
                </p>
              </div>
            </div>
          )}

          {/* Step 3: Interview */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <h3 className="font-medium">AI Interview</h3>
                <span className="text-sm text-slate-500">Please answer these questions to help us design your factory</span>
              </div>

              {questions.map((q, index) => (
                <div key={q.id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <div className="flex items-start gap-3 mb-3">
                    <span className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs font-medium">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="font-medium mb-1">{q.question}</p>
                      {q.context && (
                        <p className="text-sm text-slate-500">{q.context}</p>
                      )}
                    </div>
                  </div>

                  {q.options && q.options.length > 0 ? (
                    <div className="ml-9 space-y-2">
                      {q.multiselect ? (
                        // Multiselect: checkboxes
                        <>
                          <div className="grid grid-cols-2 gap-2">
                            {q.options.map(option => {
                              const selected = Array.isArray(answers[q.id]) && answers[q.id].includes(option)
                              return (
                                <button
                                  key={option}
                                  onClick={() => {
                                    setAnswers(prev => {
                                      const current = Array.isArray(prev[q.id]) ? prev[q.id] as string[] : []
                                      if (current.includes(option)) {
                                        return { ...prev, [q.id]: current.filter(o => o !== option) }
                                      } else {
                                        return { ...prev, [q.id]: [...current, option] }
                                      }
                                    })
                                  }}
                                  className={cn(
                                    "flex items-center gap-2 text-left px-3 py-2 rounded-lg border transition-colors text-sm",
                                    selected
                                      ? "bg-purple-600/20 border-purple-500 text-purple-300"
                                      : "bg-slate-900 border-slate-700 hover:border-slate-600"
                                  )}
                                >
                                  <span className={cn(
                                    "w-4 h-4 rounded border flex items-center justify-center",
                                    selected ? "bg-purple-600 border-purple-600" : "border-slate-500"
                                  )}>
                                    {selected && <CheckCircle className="w-3 h-3" />}
                                  </span>
                                  {option}
                                </button>
                              )
                            })}
                          </div>
                          <p className="text-xs text-slate-500">
                            {Array.isArray(answers[q.id]) && answers[q.id].length > 0
                              ? `${answers[q.id].length} selected`
                              : "Select all that apply"}
                          </p>
                        </>
                      ) : (
                        // Single select: radio buttons
                        <>
                          {q.options.map(option => (
                            <button
                              key={option}
                              onClick={() => setAnswers(prev => ({ ...prev, [q.id]: option }))}
                              className={cn(
                                "w-full text-left px-4 py-2 rounded-lg border transition-colors",
                                answers[q.id] === option
                                  ? "bg-purple-600/20 border-purple-500 text-purple-300"
                                  : "bg-slate-900 border-slate-700 hover:border-slate-600"
                              )}
                            >
                              {option}
                            </button>
                          ))}
                          <input
                            type="text"
                            value={typeof answers[q.id] === 'string' && !q.options.includes(answers[q.id] as string) ? answers[q.id] as string : ''}
                            onChange={(e) => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                            placeholder="Or type a custom answer..."
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/50 text-sm"
                          />
                        </>
                      )}
                    </div>
                  ) : (
                    <textarea
                      value={typeof answers[q.id] === 'string' ? answers[q.id] : ''}
                      onChange={(e) => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                      placeholder="Type your answer..."
                      rows={3}
                      className="ml-9 w-[calc(100%-2.25rem)] px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/50 text-sm resize-none"
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Step 4: Review Plan */}
          {step === 4 && plan && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-purple-400" />
                <h3 className="font-medium">Factory Plan</h3>
                <span className="text-sm text-slate-500">Review and confirm your factory configuration</span>
              </div>

              {/* Overview */}
              <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-lg p-4">
                <h4 className="font-semibold text-lg mb-2">{plan.name}</h4>
                <p className="text-slate-400 text-sm mb-3">{plan.description}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded capitalize">{plan.domain}</span>
                  <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded">{plan.estimated_complexity} Complexity</span>
                </div>
              </div>

              {/* Architecture */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-purple-400">Recommended Architecture</h4>
                <p className="text-sm text-slate-300">{plan.architecture}</p>
              </div>

              {/* Grid of details */}
              <div className="grid grid-cols-2 gap-4">
                {/* Assistants */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Assistants ({plan.assistants.length})</h4>
                  <div className="flex flex-wrap gap-1">
                    {plan.assistants.map(a => (
                      <span key={a} className="px-2 py-0.5 bg-slate-700 text-slate-300 rounded text-xs">{a}</span>
                    ))}
                  </div>
                </div>

                {/* Compliance */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Compliance ({plan.compliance.length})</h4>
                  <div className="flex flex-wrap gap-1">
                    {plan.compliance.map(c => (
                      <span key={c} className="px-2 py-0.5 bg-red-900/30 text-red-400 rounded text-xs">{c}</span>
                    ))}
                  </div>
                </div>

                {/* Features */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Features ({plan.features.length})</h4>
                  <ul className="text-xs text-slate-300 space-y-1 max-h-24 overflow-y-auto">
                    {plan.features.map(f => (
                      <li key={f} className="flex items-center gap-1">
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Integrations */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Integrations ({plan.integrations.length})</h4>
                  <ul className="text-xs text-slate-300 space-y-1 max-h-24 overflow-y-auto">
                    {plan.integrations.map(i => (
                      <li key={i} className="flex items-center gap-1">
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                        {i}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Data Models */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Data Models ({plan.data_models.length})</h4>
                  <ul className="text-xs text-slate-300 space-y-1 max-h-24 overflow-y-auto">
                    {plan.data_models.map(m => (
                      <li key={m} className="flex items-center gap-1">
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* API Endpoints */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-sm text-slate-400">API Endpoints ({plan.api_endpoints.length})</h4>
                  <ul className="text-xs text-slate-300 space-y-1 max-h-24 overflow-y-auto">
                    {plan.api_endpoints.map(e => (
                      <li key={e} className="flex items-center gap-1">
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Security */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-sm text-slate-400">Security Considerations</h4>
                <ul className="text-xs text-slate-300 space-y-1">
                  {plan.security_considerations.map(s => (
                    <li key={s} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-amber-500 rounded-full" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* UI/UX Preferences */}
              {plan.ui_ux && (
                <div className="bg-gradient-to-br from-cyan-900/20 to-purple-900/20 border border-cyan-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Palette className="w-4 h-4 text-cyan-400" />
                    <h4 className="font-medium text-cyan-400">UI/UX Design Plan</h4>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-slate-500 text-xs">Style</p>
                      <p className="text-slate-300 capitalize">{plan.ui_ux.style}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Color Scheme</p>
                      <p className="text-slate-300">{plan.ui_ux.color_scheme || 'To be determined'}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Target Audience</p>
                      <p className="text-slate-300">{plan.ui_ux.target_audience || 'General users'}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Component Library</p>
                      <p className="text-slate-300">{plan.ui_ux.component_library || 'TBD'}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Responsive Approach</p>
                      <p className="text-slate-300 capitalize">{plan.ui_ux.responsive_priority}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Accessibility Level</p>
                      <p className="text-slate-300">WCAG {plan.ui_ux.accessibility_level}</p>
                    </div>
                  </div>

                  {/* Key Pages */}
                  {plan.ui_ux.key_pages && plan.ui_ux.key_pages.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-slate-500 text-xs mb-2">Key Pages/Screens</p>
                      <div className="flex flex-wrap gap-1">
                        {plan.ui_ux.key_pages.map(page => (
                          <span key={page} className="px-2 py-0.5 bg-cyan-900/30 text-cyan-300 rounded text-xs">
                            {page}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Special Requirements */}
                  {plan.ui_ux.special_requirements && plan.ui_ux.special_requirements.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-slate-500 text-xs mb-2">Special Requirements</p>
                      <div className="flex flex-wrap gap-1">
                        {plan.ui_ux.special_requirements.map(req => (
                          <span key={req} className="px-2 py-0.5 bg-purple-900/30 text-purple-300 rounded text-xs">
                            {req}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Inspiration URLs */}
                  {plan.ui_ux.inspiration_urls && plan.ui_ux.inspiration_urls.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-slate-500 text-xs mb-2">Design References</p>
                      <div className="space-y-1">
                        {plan.ui_ux.inspiration_urls.map((url, i) => (
                          <a
                            key={i}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300"
                          >
                            <Link2 className="w-3 h-3" />
                            {url.length > 50 ? url.substring(0, 50) + '...' : url}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Feature Sub-Plans */}
              {plan.feature_plans && plan.feature_plans.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <h4 className="font-medium text-emerald-400">Detailed Feature Plans ({plan.feature_plans.length})</h4>
                  </div>

                  {plan.feature_plans.map((fp, index) => (
                    <div key={fp.feature} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 bg-emerald-600 rounded-full flex items-center justify-center text-xs font-medium">
                            {index + 1}
                          </span>
                          <h5 className="font-medium">{fp.feature}</h5>
                        </div>
                        <span className={cn(
                          "px-2 py-0.5 rounded text-xs",
                          fp.estimated_effort === 'low' ? "bg-green-900/30 text-green-400" :
                          fp.estimated_effort === 'high' ? "bg-red-900/30 text-red-400" :
                          "bg-amber-900/30 text-amber-400"
                        )}>
                          {fp.estimated_effort} effort
                        </span>
                      </div>

                      <p className="text-sm text-slate-400 mb-3">{fp.description}</p>

                      {/* Tasks */}
                      <div className="mb-3">
                        <p className="text-xs text-slate-500 mb-1">Implementation Tasks:</p>
                        <ul className="text-xs text-slate-300 space-y-1">
                          {fp.tasks.map((task, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 shrink-0" />
                              {task}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-xs">
                        {/* Components */}
                        {fp.components && fp.components.length > 0 && (
                          <div>
                            <p className="text-slate-500 mb-1">Components:</p>
                            <div className="flex flex-wrap gap-1">
                              {fp.components.map(c => (
                                <span key={c} className="px-1.5 py-0.5 bg-blue-900/30 text-blue-300 rounded">{c}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* API Routes */}
                        {fp.api_routes && fp.api_routes.length > 0 && (
                          <div>
                            <p className="text-slate-500 mb-1">API Routes:</p>
                            <div className="flex flex-wrap gap-1">
                              {fp.api_routes.map(r => (
                                <code key={r} className="px-1.5 py-0.5 bg-slate-900 text-cyan-300 rounded">{r}</code>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Data Models */}
                        {fp.data_models && fp.data_models.length > 0 && (
                          <div>
                            <p className="text-slate-500 mb-1">Data Models:</p>
                            <div className="flex flex-wrap gap-1">
                              {fp.data_models.map(m => (
                                <span key={m} className="px-1.5 py-0.5 bg-purple-900/30 text-purple-300 rounded">{m}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Assistant Tools */}
                        {fp.assistant_tools && fp.assistant_tools.length > 0 && (
                          <div>
                            <p className="text-slate-500 mb-1">Assistant Tools:</p>
                            <div className="flex flex-wrap gap-1">
                              {fp.assistant_tools.map(t => (
                                <span key={t} className="px-1.5 py-0.5 bg-amber-900/30 text-amber-300 rounded">{t}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Dependencies */}
                      {fp.dependencies && fp.dependencies.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700">
                          <p className="text-xs text-slate-500">
                            Depends on: {fp.dependencies.join(', ')}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 5: Creating */}
          {step === 5 && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
              <h3 className="font-medium text-lg mb-2">Creating Your Factory</h3>
              <p className="text-slate-500 text-sm">Setting up assistants and configuring your workspace...</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800">
          <button
            onClick={() => {
              if (step === 1) handleClose()
              else setStep(step - 1)
            }}
            disabled={isPlanning || isCreating}
            className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-slate-300 disabled:opacity-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            {step === 1 ? 'Cancel' : 'Back'}
          </button>

          {step === 1 && (
            <button
              onClick={() => setStep(2)}
              disabled={!canProceedStep1}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              Continue
              <ChevronRight className="w-4 h-4" />
            </button>
          )}

          {step === 2 && (
            <button
              onClick={handleStartInterview}
              disabled={!canProceedStep2 || isPlanning}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              {isPlanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Questions...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Start AI Interview
                </>
              )}
            </button>
          )}

          {step === 3 && (
            <button
              onClick={handleSubmitAnswers}
              disabled={!canProceedStep3 || isPlanning}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              {isPlanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Plan...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Plan
                </>
              )}
            </button>
          )}

          {step === 4 && (
            <button
              onClick={handleCreate}
              disabled={isCreating}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating Factory...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Confirm & Create Factory
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
