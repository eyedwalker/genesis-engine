'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = API_URL.replace('http://', 'ws://').replace('https://', 'wss://')
import { Terminal as XTerm } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebLinksAddon } from '@xterm/addon-web-links'
import { RotateCcw, Maximize2, Minimize2, Copy, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import '@xterm/xterm/css/xterm.css'

interface TerminalProps {
  className?: string
}

function generateSessionId(): string {
  return `term-${Math.random().toString(36).substring(2, 10)}`
}

export function Terminal({ className }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<XTerm | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [sessionId] = useState(() => generateSessionId())
  const [connected, setConnected] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(`${WS_URL}/ws/terminal/${sessionId}`)

    ws.onopen = () => {
      setConnected(true)
      // Send initial terminal size
      if (xtermRef.current) {
        ws.send(JSON.stringify({
          type: 'init',
          rows: xtermRef.current.rows,
          cols: xtermRef.current.cols
        }))
      }
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'output' && xtermRef.current) {
        xtermRef.current.write(data.data)
      } else if (data.type === 'error') {
        xtermRef.current?.write(`\r\n\x1b[1;31mError: ${data.message}\x1b[0m\r\n`)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Attempt reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, 3000)
    }

    ws.onerror = () => {
      setConnected(false)
    }

    wsRef.current = ws
  }, [sessionId])

  useEffect(() => {
    if (!terminalRef.current) return

    // Create terminal
    const xterm = new XTerm({
      cursorBlink: true,
      cursorStyle: 'bar',
      fontSize: 14,
      fontFamily: 'JetBrains Mono, Menlo, Monaco, Consolas, monospace',
      theme: {
        background: '#0f172a',
        foreground: '#e2e8f0',
        cursor: '#3b82f6',
        cursorAccent: '#0f172a',
        selectionBackground: '#334155',
        black: '#1e293b',
        red: '#ef4444',
        green: '#22c55e',
        yellow: '#eab308',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: '#f1f5f9',
        brightBlack: '#475569',
        brightRed: '#f87171',
        brightGreen: '#4ade80',
        brightYellow: '#facc15',
        brightBlue: '#60a5fa',
        brightMagenta: '#c084fc',
        brightCyan: '#22d3ee',
        brightWhite: '#ffffff'
      },
      allowProposedApi: true
    })

    const fitAddon = new FitAddon()
    const webLinksAddon = new WebLinksAddon()

    xterm.loadAddon(fitAddon)
    xterm.loadAddon(webLinksAddon)

    xterm.open(terminalRef.current)
    fitAddon.fit()

    xtermRef.current = xterm
    fitAddonRef.current = fitAddon

    // Handle terminal input
    xterm.onData((data) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'input',
          data: data
        }))
      }
    })

    // Handle resize
    const handleResize = () => {
      fitAddon.fit()
      if (wsRef.current?.readyState === WebSocket.OPEN && xtermRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'resize',
          rows: xtermRef.current.rows,
          cols: xtermRef.current.cols
        }))
      }
    }

    window.addEventListener('resize', handleResize)

    // Connect to backend
    connect()

    return () => {
      window.removeEventListener('resize', handleResize)
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
      xterm.dispose()
    }
  }, [connect])

  // Refit on fullscreen change
  useEffect(() => {
    setTimeout(() => {
      fitAddonRef.current?.fit()
      if (wsRef.current?.readyState === WebSocket.OPEN && xtermRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'resize',
          rows: xtermRef.current.rows,
          cols: xtermRef.current.cols
        }))
      }
    }, 100)
  }, [isFullscreen])

  const handleReconnect = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }
    xtermRef.current?.clear()
    xtermRef.current?.write('\x1b[1;33mReconnecting...\x1b[0m\r\n')
    connect()
  }

  const handleCopy = () => {
    const selection = xtermRef.current?.getSelection()
    if (selection) {
      navigator.clipboard.writeText(selection)
    }
  }

  const handleClear = () => {
    xtermRef.current?.clear()
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'input',
        data: 'clear\n'
      }))
    }
  }

  return (
    <div className={cn(
      'flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden',
      isFullscreen && 'fixed inset-4 z-50',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-950">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="w-3 h-3 rounded-full bg-green-500" />
          </div>
          <span className="text-sm text-slate-400 font-mono">genesis-terminal</span>
          <span className={cn(
            'text-xs px-2 py-0.5 rounded-full',
            connected
              ? 'bg-emerald-500/20 text-emerald-400'
              : 'bg-red-500/20 text-red-400'
          )}>
            {connected ? 'connected' : 'disconnected'}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-slate-800 rounded transition-colors"
            title="Copy selection"
          >
            <Copy className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={handleClear}
            className="p-1.5 hover:bg-slate-800 rounded transition-colors"
            title="Clear terminal"
          >
            <X className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={handleReconnect}
            className="p-1.5 hover:bg-slate-800 rounded transition-colors"
            title="Reconnect"
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 hover:bg-slate-800 rounded transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4 text-slate-400" />
            ) : (
              <Maximize2 className="w-4 h-4 text-slate-400" />
            )}
          </button>
        </div>
      </div>

      {/* Terminal */}
      <div
        ref={terminalRef}
        className="flex-1 p-2"
        style={{ minHeight: isFullscreen ? 'calc(100% - 44px)' : '500px' }}
      />
    </div>
  )
}
