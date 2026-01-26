'use client'

import { useState } from 'react'
import { X, Loader2, CheckCircle, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface CreateFactoryModalProps {
  isOpen: boolean
  onClose: () => void
}

const PRESET_DOMAINS = [
  { id: 'healthcare', name: 'Healthcare', description: 'FHIR, HIPAA, patient data' },
  { id: 'ecommerce', name: 'E-Commerce', description: 'Payments, inventory, orders' },
  { id: 'fintech', name: 'FinTech', description: 'Banking, payments, compliance' },
  { id: 'logistics', name: 'Logistics', description: 'Shipping, tracking, IoT' },
  { id: 'saas', name: 'SaaS Platform', description: 'Multi-tenant, subscriptions' },
  { id: 'custom', name: 'Custom', description: 'Describe your domain' },
]

export function CreateFactoryModal({ isOpen, onClose }: CreateFactoryModalProps) {
  const [step, setStep] = useState(1)
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [factoryName, setFactoryName] = useState('')
  const [description, setDescription] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  if (!isOpen) return null

  const handleCreate = async () => {
    setIsCreating(true)

    // Simulate factory creation
    await new Promise(resolve => setTimeout(resolve, 3000))

    setIsCreating(false)
    toast.success('Factory created successfully!')
    onClose()

    // Reset state
    setStep(1)
    setSelectedDomain(null)
    setFactoryName('')
    setDescription('')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Create New Factory</h2>
              <p className="text-sm text-slate-400">Step {step} of 2</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
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
                          ? 'bg-blue-600/20 border-blue-500 text-blue-400'
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
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Domain Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your domain in detail. What features do you need? What are the key entities? What integrations are required?"
                  rows={6}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none"
                />
                <p className="text-xs text-slate-500 mt-2">
                  The more detail you provide, the better the Genesis Engine can configure your factory.
                </p>
              </div>

              {/* Preview */}
              <div className="bg-slate-950 rounded-lg p-4">
                <p className="text-xs text-slate-500 mb-2">Factory Configuration Preview</p>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Name:</span>
                    <span>{factoryName || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Domain:</span>
                    <span className="capitalize">{selectedDomain || 'Not selected'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Assistants:</span>
                    <span>Auto-configured</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800">
          <button
            onClick={() => step > 1 ? setStep(step - 1) : onClose()}
            className="px-4 py-2 text-slate-400 hover:text-slate-300 transition-colors"
          >
            {step > 1 ? 'Back' : 'Cancel'}
          </button>

          {step < 2 ? (
            <button
              onClick={() => setStep(2)}
              disabled={!selectedDomain || !factoryName}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              Continue
            </button>
          ) : (
            <button
              onClick={handleCreate}
              disabled={isCreating || !description}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating Factory...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Create Factory
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
