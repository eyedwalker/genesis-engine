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
import { useGenesisStore } from '@/lib/store'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'factories' | 'review' | 'assistants' | 'live'>('factories')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const { factories, assistants, loadData, isLoading } = useGenesisStore()

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

              {/* Live indicator */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                <span className="w-2 h-2 bg-emerald-500 rounded-full pulse-dot" />
                <span className="text-xs text-emerald-400">3 users online</span>
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
                <FactoriesView factories={factories} isLoading={isLoading} />
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
function FactoriesView({ factories, isLoading }: { factories: any[]; isLoading: boolean }) {
  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          icon={<Factory className="w-5 h-5" />}
          label="Active Factories"
          value="5"
          change="+2 this week"
          color="blue"
        />
        <StatCard
          icon={<FileCode className="w-5 h-5" />}
          label="Features Built"
          value="127"
          change="+23 this week"
          color="purple"
        />
        <StatCard
          icon={<CheckCircle className="w-5 h-5" />}
          label="Success Rate"
          value="94.2%"
          change="+1.5%"
          color="emerald"
        />
        <StatCard
          icon={<AlertTriangle className="w-5 h-5" />}
          label="Pending Escalations"
          value="3"
          change="-2 resolved"
          color="amber"
        />
      </div>

      {/* Factory List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your Factories</h2>
          <button className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-300">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-48 bg-slate-900 border border-slate-800 rounded-xl animate-pulse"
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {/* Demo factories */}
            <FactoryCard
              name="Healthcare Platform"
              domain="healthcare"
              status="active"
              featuresBuilt={45}
              lastActivity="2 minutes ago"
              assistants={['security', 'fhir', 'accessibility']}
            />
            <FactoryCard
              name="E-Commerce Engine"
              domain="e-commerce"
              status="active"
              featuresBuilt={32}
              lastActivity="15 minutes ago"
              assistants={['security', 'pci_dss', 'performance']}
            />
            <FactoryCard
              name="Logistics Platform"
              domain="logistics"
              status="building"
              featuresBuilt={18}
              lastActivity="Just now"
              assistants={['security', 'microservices', 'docker']}
            />
            <FactoryCard
              name="FinTech API"
              domain="fintech"
              status="paused"
              featuresBuilt={27}
              lastActivity="2 days ago"
              assistants={['security', 'pci_dss', 'soc2', 'gdpr']}
            />
          </div>
        )}
      </div>
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
      <p className={`text-xs mt-1 ${color === 'amber' ? 'text-amber-400' : 'text-emerald-400'}`}>
        {change}
      </p>
    </div>
  )
}
