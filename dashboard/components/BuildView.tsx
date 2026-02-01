'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Play, CheckCircle, XCircle, Clock, Shield, Zap,
  AlertTriangle, ChevronRight, RefreshCw, Send,
  ThumbsUp, ThumbsDown, MessageSquare, Activity,
  FileCode, ExternalLink, Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = API_URL.replace('http', 'ws')

interface Stage {
  name: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  milestone: string
}

interface FindingSummary {
  vibe_score: number
  grade: string
  summary: string
  by_severity: { critical: number; high: number; medium: number; low: number }
  by_assistant: Record<string, { count: number; worst_severity: string }>
  top_issues: { title: string; severity: string; assistant: string }[]
  recommendations: string[]
}

interface BuildRun {
  id: string
  factory_id: string
  status: string
  feature_request: string
  stages: Stage[]
  vibe_score: number | null
  findings_summary: FindingSummary | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

interface Factory {
  id: string
  name: string
  domain: string
}

export function BuildView() {
  const [builds, setBuilds] = useState<BuildRun[]>([])
  const [factories, setFactories] = useState<Factory[]>([])
  const [selectedBuild, setSelectedBuild] = useState<BuildRun | null>(null)
  const [selectedFactory, setSelectedFactory] = useState<string>('')
  const [featureRequest, setFeatureRequest] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [approvalFeedback, setApprovalFeedback] = useState('')
  const wsRef = useRef<WebSocket | null>(null)

  // Load builds and factories
  const loadData = useCallback(async () => {
    try {
      const [buildsRes, factoriesRes] = await Promise.all([
        fetch(`${API_URL}/api/builds`),
        fetch(`${API_URL}/api/factories`)
      ])
      if (buildsRes.ok) setBuilds(await buildsRes.json())
      if (factoriesRes.ok) {
        const f = await factoriesRes.json()
        setFactories(f)
        if (!selectedFactory && f.length > 0) setSelectedFactory(f[0].id)
      }
    } catch (e) {
      console.error('Failed to load data:', e)
    }
  }, [selectedFactory])

  useEffect(() => { loadData() }, [loadData])

  // WebSocket for live build updates
  useEffect(() => {
    if (!selectedBuild?.id) return
    const ws = new WebSocket(`${WS_URL}/ws/builds/${selectedBuild.id}`)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'build_state') {
        setSelectedBuild(data.build)
      } else if (data.type === 'build_update') {
        setSelectedBuild(prev => prev ? {
          ...prev,
          status: data.status,
          stages: data.stages || prev.stages,
          vibe_score: data.vibe_score ?? prev.vibe_score,
          findings_summary: data.findings_summary ?? prev.findings_summary,
        } : null)
        loadData()
      }
    }

    return () => { ws.close() }
  }, [selectedBuild?.id, loadData])

  // Start a new build
  const startBuild = async () => {
    if (!selectedFactory || !featureRequest.trim()) return
    setIsSubmitting(true)
    try {
      const res = await fetch(`${API_URL}/api/builds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ factory_id: selectedFactory, feature_request: featureRequest })
      })
      if (res.ok) {
        const build = await res.json()
        setSelectedBuild(build)
        setFeatureRequest('')
        loadData()
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  // Approve or reject
  const handleApproval = async (action: 'approve' | 'reject') => {
    if (!selectedBuild) return
    const res = await fetch(`${API_URL}/api/builds/${selectedBuild.id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, feedback: approvalFeedback || null })
    })
    if (res.ok) {
      const updated = await res.json()
      setSelectedBuild(updated)
      setApprovalFeedback('')
      loadData()
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Build View</h2>
          <p className="text-sm text-slate-400 mt-1">Outcome-driven pipeline for product teams</p>
        </div>
        <button onClick={loadData} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* New Build Request */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">New Build Request</h3>
        <div className="flex gap-3">
          <select
            value={selectedFactory}
            onChange={(e) => setSelectedFactory(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white min-w-[180px] focus:ring-2 focus:ring-blue-500/50 focus:outline-none"
          >
            {factories.map(f => (
              <option key={f.id} value={f.id}>{f.name} ({f.domain})</option>
            ))}
          </select>
          <input
            value={featureRequest}
            onChange={(e) => setFeatureRequest(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && startBuild()}
            placeholder="Describe the feature you want to build..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none"
          />
          <button
            onClick={startBuild}
            disabled={isSubmitting || !featureRequest.trim()}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-colors"
          >
            {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Build
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left: Build List */}
        <div className="col-span-12 lg:col-span-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recent Builds</h3>
          {builds.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center">
              <Activity className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-500">No builds yet. Start one above.</p>
            </div>
          ) : (
            builds.map(build => (
              <button
                key={build.id}
                onClick={() => setSelectedBuild(build)}
                className={cn(
                  "w-full text-left bg-slate-900 border rounded-xl p-4 transition-all",
                  selectedBuild?.id === build.id
                    ? "border-blue-500/50 ring-1 ring-blue-500/20"
                    : "border-slate-800 hover:border-slate-700"
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <StatusBadge status={build.status} />
                  {build.vibe_score !== null && (
                    <VibeScoreBadge score={build.vibe_score} size="sm" />
                  )}
                </div>
                <p className="text-sm text-white font-medium truncate">{build.feature_request}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {new Date(build.created_at).toLocaleString()}
                </p>
              </button>
            ))
          )}
        </div>

        {/* Right: Build Detail */}
        <div className="col-span-12 lg:col-span-8">
          {selectedBuild ? (
            <BuildDetail
              build={selectedBuild}
              approvalFeedback={approvalFeedback}
              setApprovalFeedback={setApprovalFeedback}
              onApprove={() => handleApproval('approve')}
              onReject={() => handleApproval('reject')}
            />
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <FileCode className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">Select a build or start a new one to see the pipeline</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ---- Sub-components ----

function BuildDetail({
  build,
  approvalFeedback,
  setApprovalFeedback,
  onApprove,
  onReject
}: {
  build: BuildRun
  approvalFeedback: string
  setApprovalFeedback: (v: string) => void
  onApprove: () => void
  onReject: () => void
}) {
  return (
    <div className="space-y-4">
      {/* Build Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold text-white">{build.feature_request}</h3>
            <p className="text-xs text-slate-500 mt-1">Build {build.id}</p>
          </div>
          <StatusBadge status={build.status} />
        </div>

        {/* Vibe Score */}
        {build.vibe_score !== null && (
          <div className="flex items-center gap-4 mt-4 p-4 bg-slate-800/50 rounded-lg">
            <VibeScoreBadge score={build.vibe_score} size="lg" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Agent Vibe Score</p>
              <p className="text-xs text-slate-400 mt-0.5">
                Based on code quality, security posture, and architecture compliance
              </p>
              {build.findings_summary && (
                <p className="text-xs text-slate-300 mt-1">{build.findings_summary.summary}</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Plan Tracer */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Plan Tracer</h4>
        <div className="space-y-1">
          {build.stages.map((stage, i) => (
            <StageRow key={stage.name} stage={stage} isLast={i === build.stages.length - 1} />
          ))}
        </div>
      </div>

      {/* Findings Summary */}
      {build.findings_summary && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Review Findings</h4>

          {/* Severity Counts */}
          <div className="grid grid-cols-4 gap-3 mb-4">
            {(['critical', 'high', 'medium', 'low'] as const).map(sev => (
              <div key={sev} className={cn(
                "rounded-lg p-3 text-center",
                sev === 'critical' ? 'bg-red-500/10 border border-red-500/20' :
                sev === 'high' ? 'bg-orange-500/10 border border-orange-500/20' :
                sev === 'medium' ? 'bg-yellow-500/10 border border-yellow-500/20' :
                'bg-blue-500/10 border border-blue-500/20'
              )}>
                <div className={cn(
                  "text-2xl font-bold",
                  sev === 'critical' ? 'text-red-400' :
                  sev === 'high' ? 'text-orange-400' :
                  sev === 'medium' ? 'text-yellow-400' : 'text-blue-400'
                )}>
                  {build.findings_summary.by_severity[sev]}
                </div>
                <div className="text-xs text-slate-400 capitalize mt-1">{sev}</div>
              </div>
            ))}
          </div>

          {/* Top Issues */}
          {build.findings_summary.top_issues.length > 0 && (
            <div className="space-y-2 mb-4">
              <p className="text-xs font-semibold text-slate-400 uppercase">Top Issues</p>
              {build.findings_summary.top_issues.map((issue, i) => (
                <div key={i} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded-lg">
                  <SeverityDot severity={issue.severity} />
                  <span className="text-sm text-white flex-1">{issue.title}</span>
                  <span className="text-xs text-slate-500">{issue.assistant}</span>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase">Recommendations</p>
            {build.findings_summary.recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <ChevronRight className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approval Gate */}
      {build.status === 'pending_approval' && (
        <div className="bg-gradient-to-br from-blue-500/5 to-purple-500/5 border border-blue-500/20 rounded-xl p-5">
          <h4 className="text-sm font-semibold text-blue-300 uppercase tracking-wider mb-3">Approval Gate</h4>
          <p className="text-sm text-slate-300 mb-4">
            This build is ready for stakeholder review. Approve to hand off to engineering or request refinements.
          </p>
          <div className="flex gap-3 mb-3">
            <input
              value={approvalFeedback}
              onChange={(e) => setApprovalFeedback(e.target.value)}
              placeholder="Optional feedback..."
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:outline-none"
            />
          </div>
          <div className="flex gap-3 justify-end">
            <button
              onClick={onReject}
              className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-sm font-semibold text-slate-300 transition-colors"
            >
              <ThumbsDown className="w-4 h-4" />
              Request Refinement
            </button>
            <button
              onClick={onApprove}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-colors"
            >
              <ThumbsUp className="w-4 h-4" />
              Approve &amp; Handoff
            </button>
          </div>
        </div>
      )}

      {/* Final status */}
      {build.status === 'approved' && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-5 text-center">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-300 font-semibold">Build Approved</p>
          <p className="text-xs text-slate-400 mt-1">Handed off to engineering at {build.completed_at ? new Date(build.completed_at).toLocaleString() : ''}</p>
        </div>
      )}

      {build.status === 'rejected' && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-5 text-center">
          <XCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
          <p className="text-red-300 font-semibold">Refinement Requested</p>
          <p className="text-xs text-slate-400 mt-1">Feedback sent back to the agent pipeline</p>
        </div>
      )}
    </div>
  )
}

function StageRow({ stage, isLast }: { stage: Stage; isLast: boolean }) {
  const icon = stage.status === 'completed' ? <CheckCircle className="w-4 h-4 text-emerald-400" /> :
    stage.status === 'active' ? <Loader2 className="w-4 h-4 text-blue-400 animate-spin" /> :
    stage.status === 'failed' ? <XCircle className="w-4 h-4 text-red-400" /> :
    <Clock className="w-4 h-4 text-slate-600" />

  return (
    <div className={cn(
      "flex items-center gap-3 p-3 rounded-lg transition-all",
      stage.status === 'active' ? "bg-blue-500/10 border border-blue-500/20" :
      stage.status === 'completed' ? "bg-slate-800/30" :
      stage.status === 'failed' ? "bg-red-500/5 border border-red-500/10" :
      "opacity-50"
    )}>
      {icon}
      <div className="flex-1 min-w-0">
        <span className={cn(
          "text-sm font-medium",
          stage.status === 'active' ? "text-blue-300" :
          stage.status === 'completed' ? "text-emerald-300" :
          stage.status === 'failed' ? "text-red-300" :
          "text-slate-500"
        )}>{stage.name}</span>
        <p className={cn(
          "text-xs truncate",
          stage.status === 'active' ? "text-blue-400/70" :
          stage.status === 'completed' ? "text-slate-500" :
          "text-slate-600"
        )}>{stage.milestone}</p>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { color: string; label: string }> = {
    queued: { color: 'bg-slate-500/10 text-slate-400 border-slate-500/20', label: 'Queued' },
    designing: { color: 'bg-purple-500/10 text-purple-400 border-purple-500/20', label: 'Designing' },
    building: { color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', label: 'Building' },
    testing: { color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20', label: 'Testing' },
    reviewing: { color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20', label: 'Reviewing' },
    pending_approval: { color: 'bg-amber-500/10 text-amber-400 border-amber-500/20', label: 'Awaiting Approval' },
    approved: { color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', label: 'Approved' },
    rejected: { color: 'bg-red-500/10 text-red-400 border-red-500/20', label: 'Refinement Needed' },
    failed: { color: 'bg-red-500/10 text-red-400 border-red-500/20', label: 'Failed' },
  }
  const c = config[status] || config.queued
  return (
    <span className={cn("text-xs font-medium px-2.5 py-1 rounded-full border", c.color)}>
      {c.label}
    </span>
  )
}

function VibeScoreBadge({ score, size = 'sm' }: { score: number; size?: 'sm' | 'lg' }) {
  const color = score >= 90 ? 'text-emerald-400' :
    score >= 70 ? 'text-yellow-400' :
    score >= 50 ? 'text-orange-400' : 'text-red-400'

  if (size === 'lg') {
    return (
      <div className="flex flex-col items-center justify-center w-16 h-16 rounded-xl bg-slate-800 border border-slate-700">
        <span className={cn("text-2xl font-black", color)}>{score}</span>
        <span className="text-[10px] text-slate-500">/ 100</span>
      </div>
    )
  }

  return (
    <span className={cn("text-sm font-bold", color)}>{score}/100</span>
  )
}

function SeverityDot({ severity }: { severity: string }) {
  const color = severity === 'critical' ? 'bg-red-500' :
    severity === 'high' ? 'bg-orange-500' :
    severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
  return <span className={cn("w-2 h-2 rounded-full flex-shrink-0", color)} />
}
