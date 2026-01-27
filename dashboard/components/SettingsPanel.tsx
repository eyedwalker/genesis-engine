'use client'

import { useState, useEffect } from 'react'
import {
  Settings, Key, Plug, Palette, Sliders, Save, RefreshCw,
  CheckCircle, XCircle, AlertTriangle, Eye, EyeOff, TestTube,
  Cloud, Database, Mail, CreditCard, Lock, Sparkles
} from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Setting {
  key: string
  value: string
  display_value: string
  category: string
  label: string
  description: string
  value_type: string
  is_required: boolean
  is_configured: boolean
  updated_at: string
}

interface SettingsStatus {
  total: number
  configured: number
  required_total: number
  required_configured: number
  is_ready: boolean
  missing_required: { key: string; label: string }[]
}

const CATEGORY_INFO: Record<string, { label: string; icon: any; description: string }> = {
  ai: {
    label: 'AI Configuration',
    icon: Sparkles,
    description: 'Configure AI providers for planning, code review, and suggestions'
  },
  integrations: {
    label: 'Integrations',
    icon: Plug,
    description: 'API keys and credentials for external services'
  },
  defaults: {
    label: 'Default Settings',
    icon: Sliders,
    description: 'Default configuration for new factories'
  },
  ui: {
    label: 'Interface',
    icon: Palette,
    description: 'Dashboard appearance and behavior'
  }
}

const INTEGRATION_ICONS: Record<string, any> = {
  stripe_api_key: CreditCard,
  stripe_webhook_secret: CreditCard,
  sendgrid_api_key: Mail,
  auth0_domain: Lock,
  auth0_client_id: Lock,
  auth0_client_secret: Lock,
  aws_access_key: Cloud,
  aws_secret_key: Cloud,
  aws_region: Cloud,
  github_token: Cloud,
  database_url: Database,
}

export function SettingsPanel() {
  const [settings, setSettings] = useState<Record<string, Setting[]>>({})
  const [status, setStatus] = useState<SettingsStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [editedValues, setEditedValues] = useState<Record<string, string>>({})
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set())
  const [activeCategory, setActiveCategory] = useState('ai')
  const [testingConnection, setTestingConnection] = useState(false)

  // Load settings
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setIsLoading(true)
    try {
      const [settingsRes, statusRes] = await Promise.all([
        fetch(`${API_URL}/api/settings`),
        fetch(`${API_URL}/api/settings/status`)
      ])

      if (settingsRes.ok && statusRes.ok) {
        const settingsData = await settingsRes.json()
        const statusData = await statusRes.json()
        setSettings(settingsData)
        setStatus(statusData)
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
      toast.error('Failed to load settings')
    }
    setIsLoading(false)
  }

  const handleSave = async () => {
    if (Object.keys(editedValues).length === 0) {
      toast('No changes to save', { icon: 'ℹ️' })
      return
    }

    setIsSaving(true)
    try {
      const res = await fetch(`${API_URL}/api/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: editedValues })
      })

      if (res.ok) {
        toast.success(`Saved ${Object.keys(editedValues).length} settings`)
        setEditedValues({})
        await loadSettings()
      } else {
        toast.error('Failed to save settings')
      }
    } catch (error) {
      toast.error('Failed to save settings')
    }
    setIsSaving(false)
  }

  const handleTestAI = async () => {
    setTestingConnection(true)
    try {
      // Save any pending AI key changes first
      if (editedValues['anthropic_api_key']) {
        await fetch(`${API_URL}/api/settings/anthropic_api_key`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ value: editedValues['anthropic_api_key'] })
        })
      }

      const res = await fetch(`${API_URL}/api/settings/test/ai`)
      const result = await res.json()

      if (result.status === 'ok') {
        toast.success('AI connection successful!')
        await loadSettings()
        setEditedValues(prev => {
          const newValues = { ...prev }
          delete newValues['anthropic_api_key']
          return newValues
        })
      } else {
        toast.error(result.message || 'AI connection failed')
      }
    } catch (error) {
      toast.error('Failed to test AI connection')
    }
    setTestingConnection(false)
  }

  const toggleSecretVisibility = (key: string) => {
    setVisibleSecrets(prev => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const getValue = (setting: Setting): string => {
    return editedValues[setting.key] ?? setting.value
  }

  const hasChanges = Object.keys(editedValues).length > 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Settings className="w-6 h-6 text-blue-400" />
            Settings
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Configure Genesis Engine for your environment
          </p>
        </div>

        <div className="flex items-center gap-3">
          {hasChanges && (
            <span className="text-sm text-amber-400">
              {Object.keys(editedValues).length} unsaved changes
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
              hasChanges
                ? "bg-blue-600 hover:bg-blue-500"
                : "bg-slate-700 text-slate-400 cursor-not-allowed"
            )}
          >
            {isSaving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>

      {/* Status Banner */}
      {status && !status.is_ready && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5" />
            <div>
              <p className="font-medium text-amber-400">Configuration Required</p>
              <p className="text-sm text-amber-400/70 mt-1">
                {status.missing_required.length} required setting{status.missing_required.length !== 1 ? 's' : ''} not configured:
              </p>
              <ul className="mt-2 space-y-1">
                {status.missing_required.map(item => (
                  <li key={item.key} className="text-sm text-amber-300 flex items-center gap-2">
                    <XCircle className="w-3 h-3" />
                    {item.label}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Progress */}
      {status && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <p className="text-sm text-slate-400">Configuration Progress</p>
            <div className="flex items-center gap-3 mt-2">
              <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className={cn(
                    "h-full transition-all",
                    status.is_ready ? "bg-emerald-500" : "bg-amber-500"
                  )}
                  style={{ width: `${Math.round((status.configured / status.total) * 100)}%` }}
                />
              </div>
              <span className="text-sm font-medium">
                {status.configured}/{status.total}
              </span>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <p className="text-sm text-slate-400">Required Settings</p>
            <div className="flex items-center gap-3 mt-2">
              <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className={cn(
                    "h-full transition-all",
                    status.is_ready ? "bg-emerald-500" : "bg-red-500"
                  )}
                  style={{ width: `${Math.round((status.required_configured / status.required_total) * 100)}%` }}
                />
              </div>
              <span className="text-sm font-medium">
                {status.required_configured}/{status.required_total}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Category Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-4">
        {Object.entries(CATEGORY_INFO).map(([key, info]) => (
          <button
            key={key}
            onClick={() => setActiveCategory(key)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
              activeCategory === key
                ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            )}
          >
            <info.icon className="w-4 h-4" />
            {info.label}
          </button>
        ))}
      </div>

      {/* Active Category Settings */}
      <div className="space-y-4">
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-4">
            {CATEGORY_INFO[activeCategory] && (
              <>
                {(() => {
                  const Icon = CATEGORY_INFO[activeCategory].icon
                  return <Icon className="w-5 h-5 text-blue-400" />
                })()}
                <div>
                  <h3 className="font-medium">{CATEGORY_INFO[activeCategory]?.label}</h3>
                  <p className="text-sm text-slate-400">{CATEGORY_INFO[activeCategory]?.description}</p>
                </div>
              </>
            )}
          </div>

          <div className="space-y-4">
            {settings[activeCategory]?.map(setting => (
              <div key={setting.key} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {INTEGRATION_ICONS[setting.key] && (
                      (() => {
                        const Icon = INTEGRATION_ICONS[setting.key]
                        return <Icon className="w-4 h-4 text-slate-400" />
                      })()
                    )}
                    <label className="font-medium">{setting.label}</label>
                    {setting.is_required && (
                      <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">Required</span>
                    )}
                    {setting.is_configured && (
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    )}
                  </div>

                  {/* Test button for AI key */}
                  {setting.key === 'anthropic_api_key' && (
                    <button
                      onClick={handleTestAI}
                      disabled={testingConnection}
                      className="flex items-center gap-1.5 px-3 py-1 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 rounded text-xs"
                    >
                      {testingConnection ? (
                        <>
                          <RefreshCw className="w-3 h-3 animate-spin" />
                          Testing...
                        </>
                      ) : (
                        <>
                          <TestTube className="w-3 h-3" />
                          Test Connection
                        </>
                      )}
                    </button>
                  )}
                </div>

                <p className="text-sm text-slate-400 mb-3">{setting.description}</p>

                <div className="flex gap-2">
                  {setting.value_type === 'secret' ? (
                    <>
                      <input
                        type={visibleSecrets.has(setting.key) ? 'text' : 'password'}
                        value={getValue(setting)}
                        onChange={(e) => setEditedValues(prev => ({
                          ...prev,
                          [setting.key]: e.target.value
                        }))}
                        placeholder={setting.is_configured ? '••••••••' : 'Enter value...'}
                        className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm font-mono"
                      />
                      <button
                        onClick={() => toggleSecretVisibility(setting.key)}
                        className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                        title={visibleSecrets.has(setting.key) ? 'Hide' : 'Show'}
                      >
                        {visibleSecrets.has(setting.key) ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </>
                  ) : setting.value_type === 'boolean' ? (
                    <button
                      onClick={() => setEditedValues(prev => ({
                        ...prev,
                        [setting.key]: getValue(setting) === 'true' ? 'false' : 'true'
                      }))}
                      className={cn(
                        "relative w-11 h-6 rounded-full transition-colors",
                        getValue(setting) === 'true' ? "bg-blue-600" : "bg-slate-600"
                      )}
                    >
                      <span
                        className={cn(
                          "absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform",
                          getValue(setting) === 'true' && "translate-x-5"
                        )}
                      />
                    </button>
                  ) : setting.value_type === 'json' ? (
                    <textarea
                      value={getValue(setting)}
                      onChange={(e) => setEditedValues(prev => ({
                        ...prev,
                        [setting.key]: e.target.value
                      }))}
                      rows={3}
                      className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm font-mono resize-none"
                      placeholder="Enter JSON..."
                    />
                  ) : (
                    <input
                      type="text"
                      value={getValue(setting)}
                      onChange={(e) => setEditedValues(prev => ({
                        ...prev,
                        [setting.key]: e.target.value
                      }))}
                      placeholder="Enter value..."
                      className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm"
                    />
                  )}
                </div>

                {editedValues[setting.key] !== undefined && (
                  <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Unsaved changes
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
        <h4 className="font-medium mb-2">Need Help?</h4>
        <div className="text-sm text-slate-400 space-y-2">
          <p>
            <strong className="text-slate-300">Anthropic API Key:</strong> Get one from{' '}
            <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
              console.anthropic.com
            </a>
          </p>
          <p>
            <strong className="text-slate-300">Integration Keys:</strong> Only configure the integrations you plan to use in your factories.
          </p>
          <p>
            <strong className="text-slate-300">Default Settings:</strong> These are applied to new factories but can be overridden per-factory.
          </p>
        </div>
      </div>
    </div>
  )
}
