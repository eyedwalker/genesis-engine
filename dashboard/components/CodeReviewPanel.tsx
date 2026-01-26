'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import {
  Shield, AlertTriangle, CheckCircle, XCircle,
  Play, Copy, Download, RefreshCw, ChevronDown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

// Dynamic import for Monaco Editor (SSR disabled)
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

const SAMPLE_CODE = `# Example: User authentication endpoint
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # TODO: Add input validation
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"token": generate_token(user.id)}
`

const ASSISTANTS = [
  { id: 'security', name: 'Security', icon: Shield, color: 'red' },
  { id: 'performance', name: 'Performance', icon: AlertTriangle, color: 'amber' },
  { id: 'accessibility', name: 'Accessibility', icon: CheckCircle, color: 'blue' },
  { id: 'code_review', name: 'Code Review', icon: RefreshCw, color: 'purple' },
]

interface Finding {
  id: string
  assistant: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  description: string
  line: number
  fix?: string
}

const SAMPLE_FINDINGS: Finding[] = [
  {
    id: '1',
    assistant: 'security',
    severity: 'critical',
    title: 'SQL Injection Vulnerability',
    description: 'String interpolation in SQL query allows SQL injection attacks. Use parameterized queries instead.',
    line: 10,
    fix: 'query = "SELECT * FROM users WHERE username=:username AND password=:password"\\nuser = db.execute(query, {"username": username, "password": password}).fetchone()'
  },
  {
    id: '2',
    assistant: 'security',
    severity: 'high',
    title: 'Plain Text Password Storage',
    description: 'Passwords should never be stored or compared in plain text. Use bcrypt or argon2.',
    line: 10,
    fix: 'from passlib.hash import bcrypt\\n# When storing: bcrypt.hash(password)\\n# When verifying: bcrypt.verify(password, hashed)'
  },
  {
    id: '3',
    assistant: 'performance',
    severity: 'medium',
    title: 'Missing Database Index',
    description: 'Query on username column may be slow without an index.',
    line: 10,
  },
  {
    id: '4',
    assistant: 'code_review',
    severity: 'low',
    title: 'Missing Input Validation',
    description: 'Add Pydantic model for request validation.',
    line: 7,
    fix: 'from pydantic import BaseModel\\n\\nclass LoginRequest(BaseModel):\\n    username: str\\n    password: str'
  },
]

export function CodeReviewPanel() {
  const [code, setCode] = useState(SAMPLE_CODE)
  const [selectedAssistants, setSelectedAssistants] = useState(['security', 'performance'])
  const [findings, setFindings] = useState<Finding[]>([])
  const [isReviewing, setIsReviewing] = useState(false)
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null)

  const toggleAssistant = (id: string) => {
    setSelectedAssistants(prev =>
      prev.includes(id)
        ? prev.filter(a => a !== id)
        : [...prev, id]
    )
  }

  const runReview = async () => {
    setIsReviewing(true)
    setFindings([])

    // Simulate streaming findings
    for (let i = 0; i < SAMPLE_FINDINGS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 500))
      setFindings(prev => [...prev, SAMPLE_FINDINGS[i]])
    }

    setIsReviewing(false)
    toast.success('Review complete! Found 4 issues.')
  }

  const severityColors = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  }

  const severityBadgeColors = {
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
            <span className="text-sm font-medium">Code Editor</span>
            <span className="text-xs text-slate-500">Python</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigator.clipboard.writeText(code)}
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
                {findings.filter(f => f.severity === 'critical').length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', severityBadgeColors.high)} />
              <span className="text-xs text-slate-500">
                {findings.filter(f => f.severity === 'high').length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', severityBadgeColors.medium)} />
              <span className="text-xs text-slate-500">
                {findings.filter(f => f.severity === 'medium').length}
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
              <p className="text-xs">Run a review to see results</p>
            </div>
          ) : (
            findings.map((finding, index) => (
              <div
                key={finding.id}
                onClick={() => setSelectedFinding(finding)}
                className={cn(
                  'p-4 rounded-lg border cursor-pointer transition-all animate-fade-in',
                  severityColors[finding.severity],
                  selectedFinding?.id === finding.id && 'ring-2 ring-blue-500'
                )}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'px-2 py-0.5 rounded text-xs uppercase font-medium',
                      severityColors[finding.severity]
                    )}>
                      {finding.severity}
                    </span>
                    <span className="text-xs text-slate-500">Line {finding.line}</span>
                  </div>
                  <span className="text-xs text-slate-500 capitalize">{finding.assistant}</span>
                </div>
                <h4 className="font-medium mb-1">{finding.title}</h4>
                <p className="text-sm text-slate-400">{finding.description}</p>

                {finding.fix && selectedFinding?.id === finding.id && (
                  <div className="mt-3 pt-3 border-t border-slate-700">
                    <p className="text-xs text-slate-500 mb-2">Suggested Fix:</p>
                    <pre className="text-xs bg-slate-950 p-2 rounded overflow-x-auto">
                      <code>{finding.fix}</code>
                    </pre>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
