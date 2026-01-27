'use client'

import { useState } from 'react'
import {
  Shield, Zap, Eye, Database, Cloud, FileCode,
  Lock, Globe, Heart, Server, CheckCircle, Search
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Assistant {
  id: string
  name: string
  domain: string
  tags: string[]
  description: string
}

const ASSISTANTS: Assistant[] = [
  {
    id: 'security',
    name: 'Security Reviewer',
    domain: 'security',
    tags: ['owasp', 'authentication', 'encryption'],
    description: 'OWASP Top 10, authentication, authorization, encryption, input validation'
  },
  {
    id: 'accessibility',
    name: 'Accessibility Auditor',
    domain: 'accessibility',
    tags: ['wcag', 'aria', 'a11y'],
    description: 'WCAG 2.2 AA/AAA, ARIA patterns, keyboard navigation, screen readers'
  },
  {
    id: 'performance',
    name: 'Performance Optimizer',
    domain: 'performance',
    tags: ['web-vitals', 'caching', 'optimization'],
    description: 'Core Web Vitals, database optimization, caching strategies, load testing'
  },
  {
    id: 'database',
    name: 'Database Expert',
    domain: 'architecture',
    tags: ['sql', 'normalization', 'indexing'],
    description: 'Schema design, normalization, indexing, query optimization, migrations'
  },
  {
    id: 'microservices',
    name: 'Microservices Architect',
    domain: 'architecture',
    tags: ['ddd', 'saga', 'cqrs'],
    description: 'DDD, service mesh, circuit breakers, saga patterns, distributed tracing'
  },
  {
    id: 'kubernetes',
    name: 'Kubernetes Advisor',
    domain: 'devops',
    tags: ['k8s', 'helm', 'security'],
    description: 'Pod security, RBAC, network policies, autoscaling, resource management'
  },
  {
    id: 'docker',
    name: 'Docker Optimizer',
    domain: 'devops',
    tags: ['containers', 'security', 'optimization'],
    description: 'Multi-stage builds, security scanning, distroless images, SBOM'
  },
  {
    id: 'gdpr',
    name: 'GDPR Compliance',
    domain: 'compliance',
    tags: ['privacy', 'data-protection', 'eu'],
    description: 'Lawful bases, data subject rights, breach notification, DPIA'
  },
  {
    id: 'pci_dss',
    name: 'PCI-DSS Compliance',
    domain: 'compliance',
    tags: ['payments', 'security', 'audit'],
    description: 'Card data protection, tokenization, logging, network segmentation'
  },
  {
    id: 'soc2',
    name: 'SOC 2 Compliance',
    domain: 'compliance',
    tags: ['audit', 'controls', 'trust'],
    description: 'Trust Service Criteria, evidence collection, control testing'
  },
  {
    id: 'fhir',
    name: 'FHIR Healthcare',
    domain: 'compliance',
    tags: ['healthcare', 'hl7', 'interoperability'],
    description: 'FHIR R4/R5, SMART on FHIR, CDS Hooks, bulk data export'
  },
  {
    id: 'react',
    name: 'React/Frontend',
    domain: 'frontend',
    tags: ['react', 'nextjs', 'performance'],
    description: 'React 18 patterns, Server Components, state management, optimization'
  },
]

const domainIcons: Record<string, any> = {
  security: Shield,
  accessibility: Eye,
  performance: Zap,
  architecture: Database,
  devops: Cloud,
  compliance: Lock,
  frontend: FileCode,
}

const domainColors: Record<string, string> = {
  security: 'from-red-500 to-orange-500',
  accessibility: 'from-blue-500 to-cyan-500',
  performance: 'from-amber-500 to-yellow-500',
  architecture: 'from-purple-500 to-pink-500',
  devops: 'from-emerald-500 to-teal-500',
  compliance: 'from-indigo-500 to-violet-500',
  frontend: 'from-rose-500 to-pink-500',
}

export function AssistantPanel({ assistants: _ }: { assistants: any[] }) {
  const [search, setSearch] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [selectedAssistant, setSelectedAssistant] = useState<Assistant | null>(null)

  const domains = Array.from(new Set(ASSISTANTS.map(a => a.domain)))

  const filtered = ASSISTANTS.filter(a => {
    const matchesSearch = search === '' ||
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
    const matchesDomain = !selectedDomain || a.domain === selectedDomain
    return matchesSearch && matchesDomain
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Code Review Assistants</h2>
          <p className="text-sm text-slate-400 mt-1">
            18 specialized assistants for comprehensive code review
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assistants..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedDomain(null)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors',
              !selectedDomain
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-slate-300'
            )}
          >
            All
          </button>
          {domains.map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm capitalize transition-colors',
                selectedDomain === domain
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-300'
              )}
            >
              {domain}
            </button>
          ))}
        </div>
      </div>

      {/* Assistant Grid */}
      <div className="grid grid-cols-3 gap-4">
        {filtered.map((assistant) => {
          const Icon = domainIcons[assistant.domain] || Shield
          return (
            <div
              key={assistant.id}
              onClick={() => setSelectedAssistant(assistant)}
              className={cn(
                'bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer transition-all hover:border-slate-700 card-glow',
                selectedAssistant?.id === assistant.id && 'ring-2 ring-blue-500 border-blue-500'
              )}
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-3">
                <div className={cn(
                  'p-2 rounded-lg bg-gradient-to-br',
                  domainColors[assistant.domain]
                )}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{assistant.name}</h3>
                  <p className="text-xs text-slate-500 capitalize">{assistant.domain}</p>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-slate-400 mb-3 line-clamp-2">
                {assistant.description}
              </p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {assistant.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Selected Assistant Details */}
      {selectedAssistant && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={cn(
                'p-3 rounded-xl bg-gradient-to-br',
                domainColors[selectedAssistant.domain]
              )}>
                {(() => {
                  const Icon = domainIcons[selectedAssistant.domain] || Shield
                  return <Icon className="w-6 h-6 text-white" />
                })()}
              </div>
              <div>
                <h3 className="text-lg font-semibold">{selectedAssistant.name}</h3>
                <p className="text-sm text-slate-400">{selectedAssistant.description}</p>
              </div>
            </div>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm transition-colors">
              Use in Review
            </button>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium mb-2">Capabilities</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  Pattern detection and best practices
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  Automated fix suggestions
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  Standards compliance checking
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  Integration with CI/CD pipelines
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-2">Supported Standards</h4>
              <div className="flex flex-wrap gap-2">
                {selectedAssistant.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-slate-800 rounded-lg text-sm text-slate-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
