'use client'

import {
  Factory, Shield, Zap, Eye, FileCode, Settings,
  Users, Activity, GitBranch, Terminal
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: any) => void
}

const navItems = [
  { id: 'factories', label: 'Factories', icon: Factory },
  { id: 'review', label: 'Code Review', icon: Eye },
  { id: 'assistants', label: 'Assistants', icon: Shield },
  { id: 'live', label: 'Live Collab', icon: Users },
]

const bottomItems = [
  { id: 'terminal', label: 'Terminal', icon: Terminal },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg">Genesis</h1>
            <p className="text-xs text-slate-400">Engine v2.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
          Main
        </p>
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={cn(
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
              activeTab === item.id
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            )}
          >
            <item.icon className="w-5 h-5" />
            <span className="text-sm font-medium">{item.label}</span>
            {item.id === 'live' && (
              <span className="ml-auto w-2 h-2 bg-emerald-500 rounded-full pulse-dot" />
            )}
          </button>
        ))}

        <div className="pt-6">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
            Quick Access
          </p>
          {bottomItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                activeTab === item.id
                  ? 'bg-slate-800 text-slate-200'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">API Status</span>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
              <span className="text-xs text-emerald-400">Connected</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">MCP Server</span>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
              <span className="text-xs text-emerald-400">Running</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
