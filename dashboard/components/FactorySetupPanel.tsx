'use client'

import { useState, useEffect } from 'react'
import {
  CheckCircle, Circle, Clock, ExternalLink, Terminal,
  ChevronDown, ChevronRight, AlertTriangle, Shield,
  Database, Key, Settings, Link2, Loader2, X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useGenesisStore } from '@/lib/store'
import toast from 'react-hot-toast'

interface SetupTask {
  id: string
  factory_id: string
  category: string
  title: string
  description: string
  status: string
  task_type: string
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

interface FactorySetupPanelProps {
  factoryId: string
  factoryName: string
  isOpen: boolean
  onClose: () => void
}

const CATEGORY_ICONS: Record<string, typeof Database> = {
  infrastructure: Database,
  credentials: Key,
  configuration: Settings,
  integration: Link2,
  compliance: Shield,
}

const CATEGORY_COLORS: Record<string, string> = {
  infrastructure: 'text-blue-400 bg-blue-500/20',
  credentials: 'text-amber-400 bg-amber-500/20',
  configuration: 'text-purple-400 bg-purple-500/20',
  integration: 'text-cyan-400 bg-cyan-500/20',
  compliance: 'text-red-400 bg-red-500/20',
}

const STATUS_ICONS: Record<string, { icon: typeof CheckCircle; color: string }> = {
  completed: { icon: CheckCircle, color: 'text-green-500' },
  in_progress: { icon: Clock, color: 'text-blue-500 animate-pulse' },
  pending: { icon: Circle, color: 'text-slate-500' },
  skipped: { icon: Circle, color: 'text-slate-600' },
  blocked: { icon: AlertTriangle, color: 'text-red-500' },
}

export function FactorySetupPanel({ factoryId, factoryName, isOpen, onClose }: FactorySetupPanelProps) {
  const [tasks, setTasks] = useState<SetupTask[]>([])
  const [progress, setProgress] = useState<SetupProgress | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['infrastructure', 'credentials']))
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null)

  const { getFactorySetup, updateSetupTask } = useGenesisStore()

  useEffect(() => {
    if (isOpen && factoryId) {
      loadSetupTasks()
    }
  }, [isOpen, factoryId])

  const loadSetupTasks = async () => {
    setIsLoading(true)
    const data = await getFactorySetup(factoryId)
    if (data) {
      setTasks(data.tasks)
      setProgress(data.progress)
    }
    setIsLoading(false)
  }

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  const handleToggleComplete = async (task: SetupTask) => {
    setUpdatingTaskId(task.id)

    const newStatus = task.status === 'completed' ? 'pending' : 'completed'
    const updated = await updateSetupTask(factoryId, task.id, { status: newStatus })

    if (updated) {
      setTasks(prev => prev.map(t => t.id === task.id ? updated : t))

      // Update progress
      if (newStatus === 'completed') {
        setProgress(prev => prev ? {
          ...prev,
          completed: prev.completed + 1,
          percent: Math.round((prev.completed + 1) / prev.total * 100)
        } : prev)
        toast.success(`Completed: ${task.title}`)
      } else {
        setProgress(prev => prev ? {
          ...prev,
          completed: prev.completed - 1,
          percent: Math.round((prev.completed - 1) / prev.total * 100)
        } : prev)
      }
    }

    setUpdatingTaskId(null)
  }

  const handleSkip = async (task: SetupTask) => {
    setUpdatingTaskId(task.id)
    const updated = await updateSetupTask(factoryId, task.id, { status: 'skipped' })
    if (updated) {
      setTasks(prev => prev.map(t => t.id === task.id ? updated : t))
      toast('Task skipped', { icon: '⏭️' })
    }
    setUpdatingTaskId(null)
  }

  if (!isOpen) return null

  // Group tasks by category
  const tasksByCategory = tasks.reduce((acc, task) => {
    if (!acc[task.category]) acc[task.category] = []
    acc[task.category].push(task)
    return acc
  }, {} as Record<string, SetupTask[]>)

  const categories = Object.keys(tasksByCategory)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative w-full max-w-2xl max-h-[85vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold">Setup Checklist</h2>
            <p className="text-sm text-slate-400">{factoryName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Progress Bar */}
        {progress && (
          <div className="px-6 py-4 border-b border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">
                {progress.completed} of {progress.total} tasks completed
              </span>
              <span className={cn(
                "text-sm font-bold",
                progress.percent === 100 ? "text-green-400" :
                progress.percent >= 50 ? "text-blue-400" : "text-amber-400"
              )}>
                {progress.percent}%
              </span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all duration-500",
                  progress.percent === 100 ? "bg-green-500" :
                  progress.percent >= 50 ? "bg-blue-500" : "bg-amber-500"
                )}
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            {progress.required_completed < progress.required_total && (
              <p className="text-xs text-amber-400 mt-2">
                {progress.required_total - progress.required_completed} required tasks remaining
              </p>
            )}
          </div>
        )}

        {/* Tasks List */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 mx-auto text-slate-600 mb-4" />
              <p className="text-slate-400">No setup tasks</p>
              <p className="text-slate-500 text-sm mt-1">This factory is ready to use</p>
            </div>
          ) : (
            <div className="space-y-4">
              {categories.map(category => {
                const categoryTasks = tasksByCategory[category]
                const completedInCategory = categoryTasks.filter(t => t.status === 'completed').length
                const CategoryIcon = CATEGORY_ICONS[category] || Settings
                const isExpanded = expandedCategories.has(category)

                return (
                  <div key={category} className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
                    {/* Category Header */}
                    <button
                      onClick={() => toggleCategory(category)}
                      className="w-full flex items-center justify-between p-4 hover:bg-slate-800/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className={cn("p-2 rounded-lg", CATEGORY_COLORS[category] || 'text-slate-400 bg-slate-700')}>
                          <CategoryIcon className="w-4 h-4" />
                        </div>
                        <div className="text-left">
                          <p className="font-medium capitalize">{category}</p>
                          <p className="text-xs text-slate-500">
                            {completedInCategory}/{categoryTasks.length} completed
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 transition-all"
                            style={{ width: `${categoryTasks.length > 0 ? (completedInCategory / categoryTasks.length * 100) : 0}%` }}
                          />
                        </div>
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5 text-slate-500" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-slate-500" />
                        )}
                      </div>
                    </button>

                    {/* Category Tasks */}
                    {isExpanded && (
                      <div className="border-t border-slate-700">
                        {categoryTasks.map((task, index) => {
                          const StatusInfo = STATUS_ICONS[task.status] || STATUS_ICONS.pending
                          const StatusIcon = StatusInfo.icon
                          const isUpdating = updatingTaskId === task.id

                          return (
                            <div
                              key={task.id}
                              className={cn(
                                "flex items-start gap-3 p-4 hover:bg-slate-800/30 transition-colors",
                                index < categoryTasks.length - 1 && "border-b border-slate-700/50"
                              )}
                            >
                              {/* Checkbox */}
                              <button
                                onClick={() => handleToggleComplete(task)}
                                disabled={isUpdating}
                                className={cn(
                                  "mt-0.5 transition-colors",
                                  StatusInfo.color,
                                  "hover:opacity-80 disabled:opacity-50"
                                )}
                              >
                                {isUpdating ? (
                                  <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                  <StatusIcon className="w-5 h-5" />
                                )}
                              </button>

                              {/* Task Content */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className={cn(
                                    "font-medium",
                                    task.status === 'completed' && "line-through text-slate-500"
                                  )}>
                                    {task.title}
                                  </span>
                                  {task.required && (
                                    <span className="px-1.5 py-0.5 text-[10px] bg-red-500/20 text-red-400 rounded">
                                      Required
                                    </span>
                                  )}
                                </div>
                                <p className={cn(
                                  "text-sm mt-1",
                                  task.status === 'completed' ? "text-slate-600" : "text-slate-400"
                                )}>
                                  {task.description}
                                </p>

                                {/* Metadata: env vars */}
                                {task.metadata?.env_vars && (
                                  <div className="flex flex-wrap gap-1 mt-2">
                                    {task.metadata.env_vars.map((v: string) => (
                                      <code key={v} className="px-1.5 py-0.5 text-xs bg-slate-900 text-amber-400 rounded">
                                        {v}
                                      </code>
                                    ))}
                                  </div>
                                )}

                                {/* Action buttons */}
                                <div className="flex items-center gap-2 mt-2">
                                  {task.task_type === 'external' && task.action_url && (
                                    <a
                                      href={task.action_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                                    >
                                      <ExternalLink className="w-3 h-3" />
                                      Open Dashboard
                                    </a>
                                  )}
                                  {task.task_type === 'automated' && task.action_command && (
                                    <button
                                      className="flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300"
                                      onClick={() => {
                                        navigator.clipboard.writeText(task.action_command!)
                                        toast.success('Command copied to clipboard')
                                      }}
                                    >
                                      <Terminal className="w-3 h-3" />
                                      {task.action_command}
                                    </button>
                                  )}
                                  {task.status === 'pending' && !task.required && (
                                    <button
                                      onClick={() => handleSkip(task)}
                                      className="text-xs text-slate-500 hover:text-slate-400"
                                    >
                                      Skip
                                    </button>
                                  )}
                                </div>

                                {/* Completed info */}
                                {task.completed_at && (
                                  <p className="text-xs text-slate-600 mt-2">
                                    Completed {new Date(task.completed_at).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Complete all required tasks to activate your factory
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
