'use client'

import {
  Factory, Play, Pause, Trash2, ExternalLink,
  ChevronRight, Clock, FileCode, Shield, ListChecks
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface FactoryCardProps {
  name: string
  domain: string
  status: string
  featuresBuilt: number
  lastActivity: string
  assistants: string[]
  onDelete?: () => void
  onSetup?: () => void
}

export function FactoryCard({
  name,
  domain,
  status,
  featuresBuilt,
  lastActivity,
  assistants,
  onDelete,
  onSetup
}: FactoryCardProps) {
  const statusColors: Record<string, string> = {
    active: 'bg-emerald-500',
    building: 'bg-blue-500 animate-pulse',
    provisioning: 'bg-blue-500 animate-pulse',
    paused: 'bg-amber-500',
    error: 'bg-red-500',
  }

  const statusLabels: Record<string, string> = {
    active: 'Active',
    building: 'Building...',
    provisioning: 'Provisioning...',
    paused: 'Paused',
    error: 'Error',
  }

  const domainColors: Record<string, string> = {
    healthcare: 'from-emerald-500 to-teal-500',
    'e-commerce': 'from-purple-500 to-pink-500',
    logistics: 'from-blue-500 to-cyan-500',
    fintech: 'from-amber-500 to-orange-500',
  }

  return (
    <div className="group bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-all card-glow">
      {/* Header */}
      <div className={cn(
        'h-2 bg-gradient-to-r',
        domainColors[domain] || 'from-blue-500 to-purple-500'
      )} />

      <div className="p-5">
        {/* Title Row */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg mb-1 group-hover:text-blue-400 transition-colors">
              {name}
            </h3>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 capitalize">{domain}</span>
              <span className="text-slate-600">•</span>
              <div className="flex items-center gap-1.5">
                <span className={cn('w-1.5 h-1.5 rounded-full', statusColors[status])} />
                <span className="text-xs text-slate-400">{statusLabels[status]}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onSetup && (
              <button
                onClick={(e) => { e.stopPropagation(); onSetup(); }}
                className="p-1.5 hover:bg-purple-500/20 rounded-lg"
                title="Setup Checklist"
              >
                <ListChecks className="w-4 h-4 text-purple-400" />
              </button>
            )}
            {status === 'active' ? (
              <button className="p-1.5 hover:bg-slate-800 rounded-lg" title="Pause">
                <Pause className="w-4 h-4 text-slate-400" />
              </button>
            ) : status !== 'building' && (
              <button className="p-1.5 hover:bg-slate-800 rounded-lg" title="Resume">
                <Play className="w-4 h-4 text-slate-400" />
              </button>
            )}
            <button className="p-1.5 hover:bg-slate-800 rounded-lg" title="Open">
              <ExternalLink className="w-4 h-4 text-slate-400" />
            </button>
            {onDelete && (
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
                className="p-1.5 hover:bg-red-500/20 rounded-lg"
                title="Delete"
              >
                <Trash2 className="w-4 h-4 text-red-400" />
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-slate-500" />
            <div>
              <p className="text-sm font-medium">{featuresBuilt}</p>
              <p className="text-xs text-slate-500">Features built</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500" />
            <div>
              <p className="text-sm font-medium">{lastActivity}</p>
              <p className="text-xs text-slate-500">Last activity</p>
            </div>
          </div>
        </div>

        {/* Assistants */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div className="flex items-center gap-1">
            <Shield className="w-4 h-4 text-slate-500 mr-1" />
            {assistants.slice(0, 3).map((assistant, i) => (
              <span
                key={assistant}
                className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400"
              >
                {assistant}
              </span>
            ))}
            {assistants.length > 3 && (
              <span className="text-xs text-slate-500">+{assistants.length - 3}</span>
            )}
          </div>

          <button className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300">
            Open <ChevronRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  )
}
