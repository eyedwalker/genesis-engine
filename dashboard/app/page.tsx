'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Factory, Shield, Zap, Eye, FileCode, Settings,
  Plus, Play, Pause, Trash2, ExternalLink, Users,
  CheckCircle, XCircle, AlertTriangle, Clock,
  ChevronRight, Search, Filter, RefreshCw
} from 'lucide-react'
import { Sidebar } from '@/components/Sidebar'
import { FactoryCard } from '@/components/FactoryCard'
import { AssistantPanel } from '@/components/AssistantPanel'
import { CodeReviewPanel } from '@/components/CodeReviewPanel'
import { CreateFactoryModal } from '@/components/CreateFactoryModal'
import { LiveCollaboration } from '@/components/LiveCollaboration'
import { FactorySetupPanel } from '@/components/FactorySetupPanel'
import { SettingsPanel } from '@/components/SettingsPanel'
import { Terminal } from '@/components/Terminal'
import { useGenesisStore, formatRelativeTime } from '@/lib/store'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'factories' | 'review' | 'assistants' | 'live' | 'settings' | 'terminal'>('factories')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const { factories, assistants, stats, loadData, isLoading, error } = useGenesisStore()

  useEffect(() => {
    loadData()
  }, [loadData])

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold gradient-text">Genesis Engine</h1>
              <p className="text-sm text-slate-400 mt-1">
                Factory-as-a-Service Platform
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 w-64"
                />
              </div>

              {/* API Status */}
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                error ? 'bg-red-500/10 border border-red-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'
              }`}>
                <span className={`w-2 h-2 rounded-full ${error ? 'bg-red-500' : 'bg-emerald-500 pulse-dot'}`} />
                <span className={`text-xs ${error ? 'text-red-400' : 'text-emerald-400'}`}>
                  {error ? 'API Offline' : `${stats?.assistants?.loaded || 0} assistants loaded`}
                </span>
              </div>

              {/* Actions */}
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>New Factory</span>
              </button>
            </div>
          </div>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
            <p className="text-red-400/60 text-xs mt-1">Make sure the API server is running: ./start.sh</p>
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            {activeTab === 'factories' && (
              <motion.div
                key="factories"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <FactoriesView factories={factories} stats={stats} isLoading={isLoading} />
              </motion.div>
            )}

            {activeTab === 'review' && (
              <motion.div
                key="review"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <CodeReviewPanel />
              </motion.div>
            )}

            {activeTab === 'assistants' && (
              <motion.div
                key="assistants"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <AssistantPanel assistants={assistants} />
              </motion.div>
            )}

            {activeTab === 'live' && (
              <motion.div
                key="live"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <LiveCollaboration />
              </motion.div>
            )}

            {activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <SettingsPanel />
              </motion.div>
            )}

            {activeTab === 'terminal' && (
              <motion.div
                key="terminal"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="h-[calc(100vh-12rem)]"
              >
                <Terminal className="h-full" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Create Factory Modal */}
      <CreateFactoryModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  )
}

// Factories View Component
function FactoriesView({ factories, stats, isLoading }: { factories: any[]; stats: any; isLoading: boolean }) {
  const { loadData, deleteFactory } = useGenesisStore()
  const [selectedFactorySetup, setSelectedFactorySetup] = useState<{ id: string; name: string } | null>(null)

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          icon={<Factory className="w-5 h-5" />}
          label="Active Factories"
          value={String(stats?.factories?.active || factories.length)}
          change={`${stats?.factories?.total || 0} total`}
          color="blue"
        />
        <StatCard
          icon={<FileCode className="w-5 h-5" />}
          label="Features Built"
          value={String(stats?.features?.total || 0)}
          change="across all factories"
          color="purple"
        />
        <StatCard
          icon={<CheckCircle className="w-5 h-5" />}
          label="Code Reviews"
          value={String(stats?.reviews?.total || 0)}
          change={`${stats?.reviews?.findings?.critical || 0} critical found`}
          color="emerald"
        />
        <StatCard
          icon={<Shield className="w-5 h-5" />}
          label="Assistants Active"
          value={String(stats?.assistants?.loaded || 0)}
          change="18 available"
          color="amber"
        />
      </div>

      {/* Factory List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your Factories</h2>
          <button
            onClick={() => loadData()}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-300"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {isLoading && factories.length === 0 ? (
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-48 bg-slate-900 border border-slate-800 rounded-xl animate-pulse"
              />
            ))}
          </div>
        ) : factories.length === 0 ? (
          <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-xl">
            <Factory className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400">No factories yet</p>
            <p className="text-slate-500 text-sm mt-1">Create your first factory to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {factories.filter(f => f != null).map((factory) => (
              <FactoryCard
                key={factory.id}
                name={factory.name}
                domain={factory.domain}
                status={factory.status}
                featuresBuilt={factory.features_built}
                lastActivity={formatRelativeTime(factory.updated_at)}
                assistants={factory.assistants}
                onDelete={() => deleteFactory(factory.id)}
                onSetup={() => setSelectedFactorySetup({ id: factory.id, name: factory.name })}
              />
            ))}
          </div>
        )}
      </div>

      {/* Setup Panel */}
      {selectedFactorySetup && (
        <FactorySetupPanel
          factoryId={selectedFactorySetup.id}
          factoryName={selectedFactorySetup.name}
          isOpen={true}
          onClose={() => setSelectedFactorySetup(null)}
        />
      )}
    </div>
  )
}

// Stat Card Component
function StatCard({
  icon,
  label,
  value,
  change,
  color
}: {
  icon: React.ReactNode
  label: string
  value: string
  change: string
  color: 'blue' | 'purple' | 'emerald' | 'amber'
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 card-glow">
      <div className={`inline-flex p-2 rounded-lg ${colorClasses[color]} border mb-3`}>
        {icon}
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-xs mt-1 text-slate-500">
        {change}
      </p>
    </div>
  )
}
