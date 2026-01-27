'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import {
  Shield, AlertTriangle, CheckCircle, XCircle,
  Play, Copy, Download, RefreshCw, ChevronDown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useGenesisStore } from '@/lib/store'
import toast from 'react-hot-toast'

// Dynamic import for Monaco Editor (SSR disabled)
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

const SAMPLE_CODE = `# Example: User authentication endpoint
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random

app = FastAPI()
DEBUG = True  # TODO: disable in production

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # TODO: Add input validation
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate random token
    token = random.randint(100000, 999999)
    return {"token": token}
`

const ASSISTANTS = [
  { id: 'security', name: 'Security', icon: Shield, color: 'red' },
  { id: 'performance', name: 'Performance', icon: AlertTriangle, color: 'amber' },
  { id: 'accessibility', name: 'Accessibility', icon: CheckCircle, color: 'blue' },
]

interface Finding {
  id: string
  assistant: string
  severity: string
  title: string
  description: string
  line?: number
  code_snippet?: string
  recommendation?: string
}

export function CodeReviewPanel() {
  const [code, setCode] = useState(SAMPLE_CODE)
  const [fileName, setFileName] = useState('auth.py')
  const [selectedAssistants, setSelectedAssistants] = useState(['security', 'performance'])
  const [findings, setFindings] = useState<Finding[]>([])
  const [isReviewing, setIsReviewing] = useState(false)
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null)
  const [summary, setSummary] = useState<Record<string, number>>({})

  const { reviewCode } = useGenesisStore()

  const toggleAssistant = (id: string) => {
    setSelectedAssistants(prev =>
      prev.includes(id)
        ? prev.filter(a => a !== id)
        : [...prev, id]
    )
  }

  const runReview = async () => {
    if (selectedAssistants.length === 0) {
      toast.error('Please select at least one assistant')
      return
    }

    setIsReviewing(true)
    setFindings([])
    setSummary({})
    setSelectedFinding(null)

    try {
      const result = await reviewCode(code, fileName, selectedAssistants)

      if (result) {
        setFindings(result.findings)
        setSummary(result.summary)

        const totalIssues = result.findings.length
        if (totalIssues === 0) {
          toast.success('No issues found!')
        } else {
          const critical = result.summary.critical || 0
          const high = result.summary.high || 0
          if (critical > 0) {
            toast.error(`Found ${totalIssues} issues (${critical} critical!)`)
          } else if (high > 0) {
            toast('Found ' + totalIssues + ' issues (' + high + ' high severity)', { icon: '⚠️' })
          } else {
            toast.success(`Review complete! Found ${totalIssues} issues.`)
          }
        }
      }
    } catch (error) {
      toast.error('Failed to run review')
    }

    setIsReviewing(false)
  }

  const severityColors: Record<string, string> = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  }

  const severityBadgeColors: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-amber-500',
    low: 'bg-blue-500',
  }

  return (
    <div className="grid grid-cols-2 gap-6 h-[calc(100vh-12rem)]">
      {/* Code Editor Panel */}
      <div className="flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              className="bg-transparent text-sm font-medium border-b border-transparent hover:border-slate-600 focus:border-blue-500 focus:outline-none px-1"
            />
            <span className="text-xs text-slate-500">Python</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(code)
                toast.success('Copied to clipboard')
              }}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
              title="Copy code"
            >
              <Copy className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1">
          <MonacoEditor
            height="100%"
            language="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              padding: { top: 16 },
            }}
          />
        </div>

        {/* Assistant Selection */}
        <div className="p-4 border-t border-slate-800">
          <p className="text-xs text-slate-500 mb-2">Select Assistants</p>
          <div className="flex flex-wrap gap-2">
            {ASSISTANTS.map((assistant) => (
              <button
                key={assistant.id}
                onClick={() => toggleAssistant(assistant.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-all',
                  selectedAssistants.includes(assistant.id)
                    ? 'bg-blue-600/20 text-blue-400 border-blue-500/30'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
                )}
              >
                <assistant.icon className="w-4 h-4" />
                {assistant.name}
              </button>
            ))}
          </div>

          <button
            onClick={runReview}
            disabled={isReviewing || selectedAssistants.length === 0}
            className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
          >
            {isReviewing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Reviewing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Review
              </>
            )}
          </button>
        </div>
      </div>

      {/* Findings Panel */}
      <div className="flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium">Review Findings</span>
            {findings.length > 0 && (
              <span className="px-2 py-0.5 bg-slate-800 rounded-full text-xs">
                {findings.length} issues
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', severityBadgeColors.critical)} />
              <span className="text-xs text-slate-500">
                {summary.critical || 0}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', severityBadgeColors.high)} />
              <span className="text-xs text-slate-500">
                {summary.high || 0}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', severityBadgeColors.medium)} />
              <span className="text-xs text-slate-500">
                {summary.medium || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Findings List */}
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {findings.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Shield className="w-12 h-12 mb-4 opacity-50" />
              <p className="text-sm">No findings yet</p>
              <p className="text-xs">Run a review to see real results</p>
              <p className="text-xs text-slate-600 mt-2">Try the sample code - it has security issues!</p>
            </div>
          ) : (
            findings.map((finding, index) => (
              <div
                key={finding.id}
                onClick={() => setSelectedFinding(selectedFinding?.id === finding.id ? null : finding)}
                className={cn(
                  'p-4 rounded-lg border cursor-pointer transition-all animate-fade-in',
                  severityColors[finding.severity] || severityColors.medium,
                  selectedFinding?.id === finding.id && 'ring-2 ring-blue-500'
                )}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'px-2 py-0.5 rounded text-xs uppercase font-medium',
                      severityColors[finding.severity] || severityColors.medium
                    )}>
                      {finding.severity}
                    </span>
                    {finding.line && (
                      <span className="text-xs text-slate-500">Line {finding.line}</span>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 capitalize">{finding.assistant}</span>
                </div>
                <h4 className="font-medium mb-1">{finding.title}</h4>
                <p className="text-sm text-slate-400">{finding.description}</p>

                {selectedFinding?.id === finding.id && (
                  <>
                    {finding.code_snippet && (
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-xs text-slate-500 mb-2">Code Context:</p>
                        <pre className="text-xs bg-slate-950 p-2 rounded overflow-x-auto">
                          <code>{finding.code_snippet}</code>
                        </pre>
                      </div>
                    )}
                    {finding.recommendation && (
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-xs text-slate-500 mb-2">Recommendation:</p>
                        <p className="text-sm text-emerald-400">{finding.recommendation}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
