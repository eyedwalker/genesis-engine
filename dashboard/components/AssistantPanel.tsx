'use client'

import { useState, useEffect } from 'react'
import {
  Shield, Zap, Eye, Database, Cloud, FileCode,
  Lock, Globe, Heart, Server, CheckCircle, Search,
  X, Edit, ChevronRight, Code, FileText, Settings
} from 'lucide-react'
import { cn } from '@/lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Assistant {
  id: string
  name: string
  domain: string
  tags: string[]
  description: string
  methods_count?: number
}

interface AssistantDetail extends Assistant {
  system_prompt: string
  methods: string[]
}

interface PatternDetail {
  name: string
  description: string
  patterns: string[]
  recommendations: string[]
  code_examples: string[]
}

const domainIcons: Record<string, any> = {
  security: Shield,
  accessibility: Eye,
  performance: Zap,
  architecture: Database,
  devops: Cloud,
  compliance: Lock,
  frontend: FileCode,
}

const domainColors: Record<string, string> = {
  security: 'from-red-500 to-orange-500',
  accessibility: 'from-blue-500 to-cyan-500',
  performance: 'from-amber-500 to-yellow-500',
  architecture: 'from-purple-500 to-pink-500',
  devops: 'from-emerald-500 to-teal-500',
  compliance: 'from-indigo-500 to-violet-500',
  frontend: 'from-rose-500 to-pink-500',
}

export function AssistantPanel({ assistants: initialAssistants }: { assistants: any[] }) {
  const [search, setSearch] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [selectedAssistant, setSelectedAssistant] = useState<Assistant | null>(null)
  const [assistants, setAssistants] = useState<Assistant[]>(initialAssistants || [])
  const [loading, setLoading] = useState(false)

  // Detail view state
  const [viewOpen, setViewOpen] = useState(false)
  const [viewDetail, setViewDetail] = useState<AssistantDetail | null>(null)
  const [selectedPattern, setSelectedPattern] = useState<PatternDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  // Edit mode state
  const [editMode, setEditMode] = useState(false)
  const [editedPrompt, setEditedPrompt] = useState('')

  // Fetch assistants from API
  useEffect(() => {
    const fetchAssistants = async () => {
      try {
        setLoading(true)
        const res = await fetch(`${API_URL}/api/assistants`)
        if (res.ok) {
          const data = await res.json()
          setAssistants(data)
        }
      } catch (err) {
        console.error('Failed to fetch assistants:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAssistants()
  }, [])

  const domains = Array.from(new Set(assistants.map(a => a.domain)))

  const filtered = assistants.filter(a => {
    const matchesSearch = search === '' ||
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
    const matchesDomain = !selectedDomain || a.domain === selectedDomain
    return matchesSearch && matchesDomain
  })

  // Fetch assistant detail
  const handleView = async (assistant: Assistant) => {
    setLoadingDetail(true)
    setViewOpen(true)
    setSelectedPattern(null)
    setEditMode(false)

    try {
      const res = await fetch(`${API_URL}/api/assistants/${assistant.id}`)
      if (res.ok) {
        const data = await res.json()
        setViewDetail(data)
        setEditedPrompt(data.system_prompt)
      }
    } catch (err) {
      console.error('Failed to fetch assistant detail:', err)
    } finally {
      setLoadingDetail(false)
    }
  }

  // Fetch pattern detail
  const handlePatternClick = async (patternName: string) => {
    if (!viewDetail) return

    try {
      const res = await fetch(`${API_URL}/api/assistants/${viewDetail.id}/patterns/${patternName}`)
      if (res.ok) {
        const data = await res.json()
        setSelectedPattern(data)
      }
    } catch (err) {
      console.error('Failed to fetch pattern:', err)
    }
  }

  // Handle edit
  const handleEdit = (assistant: Assistant) => {
    handleView(assistant)
    setTimeout(() => setEditMode(true), 100)
  }

  // Save changes
  const handleSave = async () => {
    if (!viewDetail) return

    try {
      const res = await fetch(`${API_URL}/api/assistants/${viewDetail.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system_prompt: editedPrompt })
      })

      if (res.ok) {
        setViewDetail({ ...viewDetail, system_prompt: editedPrompt })
        setEditMode(false)
      }
    } catch (err) {
      console.error('Failed to save:', err)
    }
  }

  const closeModal = () => {
    setViewOpen(false)
    setViewDetail(null)
    setSelectedPattern(null)
    setEditMode(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Code Review Assistants</h2>
          <p className="text-sm text-slate-400 mt-1">
            {assistants.length} specialized assistants for comprehensive code review
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assistants..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedDomain(null)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors',
              !selectedDomain
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-slate-300'
            )}
          >
            All
          </button>
          {domains.map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm capitalize transition-colors',
                selectedDomain === domain
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-300'
              )}
            >
              {domain}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8 text-slate-400">
          Loading assistants...
        </div>
      )}

      {/* Assistant Grid */}
      <div className="grid grid-cols-3 gap-4">
        {filtered.map((assistant) => {
          const Icon = domainIcons[assistant.domain] || Shield
          return (
            <div
              key={assistant.id}
              className={cn(
                'bg-slate-900 border border-slate-800 rounded-xl p-5 transition-all hover:border-slate-700 card-glow',
                selectedAssistant?.id === assistant.id && 'ring-2 ring-blue-500 border-blue-500'
              )}
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-3">
                <div className={cn(
                  'p-2 rounded-lg bg-gradient-to-br',
                  domainColors[assistant.domain]
                )}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{assistant.name}</h3>
                  <p className="text-xs text-slate-500 capitalize">{assistant.domain}</p>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-slate-400 mb-3 line-clamp-2">
                {assistant.description}
              </p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-4">
                {assistant.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Methods Count */}
              {assistant.methods_count !== undefined && (
                <p className="text-xs text-slate-500 mb-3">
                  {assistant.methods_count} review patterns
                </p>
              )}

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleView(assistant)}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  View
                </button>
                <button
                  onClick={() => handleEdit(assistant)}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition-colors"
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Detail Modal */}
      {viewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="bg-slate-900 border border-slate-700 rounded-xl w-[90vw] max-w-5xl max-h-[85vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                {viewDetail && (
                  <>
                    <div className={cn(
                      'p-2 rounded-lg bg-gradient-to-br',
                      domainColors[viewDetail.domain]
                    )}>
                      {(() => {
                        const Icon = domainIcons[viewDetail.domain] || Shield
                        return <Icon className="w-5 h-5 text-white" />
                      })()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{viewDetail.name}</h3>
                      <p className="text-sm text-slate-400">{viewDetail.description}</p>
                    </div>
                  </>
                )}
                {loadingDetail && <span className="text-slate-400">Loading...</span>}
              </div>
              <div className="flex items-center gap-2">
                {editMode ? (
                  <>
                    <button
                      onClick={() => setEditMode(false)}
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm transition-colors"
                    >
                      Save Changes
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setEditMode(true)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition-colors flex items-center gap-2"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                )}
                <button
                  onClick={closeModal}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            {viewDetail && (
              <div className="flex-1 overflow-hidden flex">
                {/* Left Panel - Methods/Patterns */}
                <div className="w-64 border-r border-slate-800 overflow-y-auto">
                  <div className="p-4">
                    <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                      <Code className="w-4 h-4" />
                      Review Patterns ({viewDetail.methods.length})
                    </h4>
                    <div className="space-y-1">
                      {viewDetail.methods.map((method) => (
                        <button
                          key={method}
                          onClick={() => handlePatternClick(method)}
                          className={cn(
                            'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between',
                            selectedPattern?.name === method
                              ? 'bg-blue-600 text-white'
                              : 'hover:bg-slate-800 text-slate-300'
                          )}
                        >
                          <span className="truncate">{method.replace(/_/g, ' ')}</span>
                          <ChevronRight className="w-4 h-4 flex-shrink-0" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Right Panel - Details */}
                <div className="flex-1 overflow-y-auto p-6">
                  {/* Configuration Section */}
                  <div className="mb-6">
                    <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                      <Settings className="w-4 h-4 text-slate-400" />
                      System Configuration
                    </h4>

                    {/* Tags */}
                    <div className="mb-4">
                      <label className="text-xs text-slate-500 block mb-2">Tags</label>
                      <div className="flex flex-wrap gap-2">
                        {viewDetail.tags.map(tag => (
                          <span
                            key={tag}
                            className="px-3 py-1 bg-slate-800 rounded-lg text-sm text-slate-300"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* System Prompt */}
                    <div>
                      <label className="text-xs text-slate-500 block mb-2">System Prompt</label>
                      {editMode ? (
                        <textarea
                          value={editedPrompt}
                          onChange={(e) => setEditedPrompt(e.target.value)}
                          className="w-full h-48 bg-slate-800 border border-slate-700 rounded-lg p-4 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                        />
                      ) : (
                        <div className="bg-slate-800 rounded-lg p-4 text-sm text-slate-300 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {viewDetail.system_prompt}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Selected Pattern Details */}
                  {selectedPattern && (
                    <div className="border-t border-slate-800 pt-6">
                      <h4 className="text-sm font-medium mb-4 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-400" />
                        Pattern: {selectedPattern.name.replace(/_/g, ' ')}
                      </h4>

                      <p className="text-sm text-slate-400 mb-4">
                        {selectedPattern.description}
                      </p>

                      {/* Detection Patterns */}
                      {selectedPattern.patterns.length > 0 && (
                        <div className="mb-4">
                          <label className="text-xs text-slate-500 block mb-2">Detection Patterns</label>
                          <ul className="space-y-1">
                            {selectedPattern.patterns.map((p, i) => (
                              <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                                <span className="text-blue-400">•</span>
                                {p}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommendations */}
                      {selectedPattern.recommendations.length > 0 && (
                        <div className="mb-4">
                          <label className="text-xs text-slate-500 block mb-2">Recommendations</label>
                          <ul className="space-y-1">
                            {selectedPattern.recommendations.map((r, i) => (
                              <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                                <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                                {r}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Code Examples */}
                      {selectedPattern.code_examples.length > 0 && (
                        <div>
                          <label className="text-xs text-slate-500 block mb-2">Code Examples</label>
                          {selectedPattern.code_examples.map((example, i) => (
                            <pre key={i} className="bg-slate-800 rounded-lg p-4 text-sm text-slate-300 font-mono overflow-x-auto mb-2">
                              {example}
                            </pre>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* No Pattern Selected */}
                  {!selectedPattern && (
                    <div className="border-t border-slate-800 pt-6">
                      <div className="text-center text-slate-500 py-8">
                        <Code className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>Select a pattern to view details</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
