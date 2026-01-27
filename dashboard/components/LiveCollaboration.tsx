'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Users, Send, Video, Mic, MicOff, VideoOff,
  Share, MessageSquare, Code, Wifi, WifiOff, Copy, Check
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface User {
  id: string
  name: string
  status: 'online' | 'away' | 'busy'
  role?: 'owner' | 'editor' | 'viewer'
  cursorLine?: number
}

interface Message {
  id: string
  user: User
  content: string
  timestamp: string
  type: 'text' | 'code' | 'system'
}

interface CursorPosition {
  line: number
  column: number
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

function getUserColor(userId: string): string {
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return COLORS[hash % COLORS.length]
}

function generateUserId(): string {
  return `user-${Math.random().toString(36).substring(2, 10)}`
}

function generateRoomId(): string {
  return `room-${Math.random().toString(36).substring(2, 8)}`
}

export function LiveCollaboration() {
  const [connected, setConnected] = useState(false)
  const [roomId, setRoomId] = useState<string>('')
  const [joinRoomId, setJoinRoomId] = useState('')
  const [userId] = useState(() => generateUserId())
  const [userName, setUserName] = useState('Anonymous')
  const [users, setUsers] = useState<User[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isVideoOn, setIsVideoOn] = useState(false)
  const [isMicOn, setIsMicOn] = useState(true)
  const [copied, setCopied] = useState(false)
  const [codeContent, setCodeContent] = useState(`from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

app = FastAPI()

@app.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Secure parameterized query
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not bcrypt.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"token": generate_jwt_token(user.id)}`)
  const [cursors, setCursors] = useState<Record<string, CursorPosition>>({})

  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const connectToRoom = useCallback((room: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close()
    }

    const wsUrl = `ws://localhost:8000/ws/${room}?user_id=${userId}&name=${encodeURIComponent(userName)}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setConnected(true)
      setRoomId(room)
      setMessages(prev => [...prev, {
        id: `sys-${Date.now()}`,
        user: { id: 'system', name: 'System', status: 'online' },
        content: `Connected to room: ${room}`,
        timestamp: new Date().toISOString(),
        type: 'system'
      }])
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'room_state':
          setUsers(data.users.map((u: User) => ({ ...u, role: u.id === userId ? 'owner' : 'editor' })))
          break

        case 'user_join':
          setUsers(prev => {
            if (prev.find(u => u.id === data.user.id)) return prev
            return [...prev, { ...data.user, role: 'editor' }]
          })
          setMessages(prev => [...prev, {
            id: `sys-${Date.now()}`,
            user: { id: 'system', name: 'System', status: 'online' },
            content: `${data.user.name} joined the room`,
            timestamp: data.timestamp,
            type: 'system'
          }])
          break

        case 'user_leave':
          setUsers(prev => prev.filter(u => u.id !== data.user.id))
          setCursors(prev => {
            const next = { ...prev }
            delete next[data.user.id]
            return next
          })
          setMessages(prev => [...prev, {
            id: `sys-${Date.now()}`,
            user: { id: 'system', name: 'System', status: 'online' },
            content: `${data.user.name} left the room`,
            timestamp: data.timestamp,
            type: 'system'
          }])
          break

        case 'chat':
          setMessages(prev => [...prev, {
            id: `msg-${Date.now()}-${Math.random()}`,
            user: data.user,
            content: data.content,
            timestamp: data.timestamp,
            type: data.content.includes('\n') || data.content.startsWith('```') ? 'code' : 'text'
          }])
          break

        case 'code_change':
          setCodeContent(data.changes.content || codeContent)
          break

        case 'cursor_move':
          setCursors(prev => ({
            ...prev,
            [data.user_id]: data.position
          }))
          break
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Attempt reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        if (roomId) {
          connectToRoom(roomId)
        }
      }, 3000)
    }

    ws.onerror = () => {
      setConnected(false)
    }

    wsRef.current = ws
  }, [userId, userName, roomId, codeContent])

  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const createRoom = () => {
    const newRoom = generateRoomId()
    connectToRoom(newRoom)
  }

  const joinRoom = () => {
    if (joinRoomId.trim()) {
      connectToRoom(joinRoomId.trim())
    }
  }

  const copyRoomLink = () => {
    navigator.clipboard.writeText(roomId)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const sendMessage = () => {
    if (!newMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    wsRef.current.send(JSON.stringify({
      type: 'chat',
      content: newMessage
    }))

    // Add message locally (server will broadcast to others)
    setMessages(prev => [...prev, {
      id: `msg-${Date.now()}`,
      user: { id: userId, name: userName, status: 'online' },
      content: newMessage,
      timestamp: new Date().toISOString(),
      type: newMessage.includes('\n') || newMessage.startsWith('```') ? 'code' : 'text'
    }])

    setNewMessage('')
  }

  const handleCodeChange = (newCode: string) => {
    setCodeContent(newCode)
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'code_change',
        changes: { content: newCode }
      }))
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // Not connected - show join/create UI
  if (!connected) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-12rem)]">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md w-full">
          <h2 className="text-xl font-semibold mb-6 text-center">Live Collaboration</h2>

          <div className="space-y-6">
            {/* Set Name */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">Your Name</label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              />
            </div>

            {/* Create Room */}
            <div>
              <button
                onClick={createRoom}
                className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors"
              >
                Create New Room
              </button>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-slate-700" />
              <span className="text-sm text-slate-500">or</span>
              <div className="flex-1 h-px bg-slate-700" />
            </div>

            {/* Join Room */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">Join Existing Room</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={joinRoomId}
                  onChange={(e) => setJoinRoomId(e.target.value)}
                  placeholder="Enter room ID"
                  className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
                <button
                  onClick={joinRoom}
                  disabled={!joinRoomId.trim()}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors"
                >
                  Join
                </button>
              </div>
            </div>
          </div>

          <div className="mt-6 p-3 bg-slate-800/50 rounded-lg">
            <p className="text-xs text-slate-400 text-center">
              Share the room ID with collaborators to code together in real-time
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
      {/* Main Collaboration Area */}
      <div className="col-span-3 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <h2 className="font-medium">Live Code Review Session</h2>
            <span className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
              {connected ? (
                <>
                  <Wifi className="w-3 h-3 text-emerald-400" />
                  <span className="text-xs text-emerald-400">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3 h-3 text-red-400" />
                  <span className="text-xs text-red-400">Disconnected</span>
                </>
              )}
            </span>
            <button
              onClick={copyRoomLink}
              className="flex items-center gap-1.5 px-2 py-0.5 bg-slate-800 hover:bg-slate-700 rounded text-xs transition-colors"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {roomId}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMicOn(!isMicOn)}
              className={cn(
                'p-2 rounded-lg transition-colors',
                isMicOn ? 'bg-slate-800 text-slate-300' : 'bg-red-500/20 text-red-400'
              )}
            >
              {isMicOn ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setIsVideoOn(!isVideoOn)}
              className={cn(
                'p-2 rounded-lg transition-colors',
                isVideoOn ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-300'
              )}
            >
              {isVideoOn ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
            </button>
            <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              <Share className="w-4 h-4 text-slate-300" />
            </button>
          </div>
        </div>

        {/* Shared Code View */}
        <div className="flex-1 p-4 overflow-auto">
          <div className="bg-slate-950 rounded-lg p-4 h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4 text-slate-500" />
                <span className="text-sm text-slate-400">authentication.py</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">{users.length} viewer{users.length !== 1 ? 's' : ''}</span>
                <div className="flex -space-x-2">
                  {users.slice(0, 5).map(user => (
                    <div
                      key={user.id}
                      className="w-6 h-6 rounded-full border-2 border-slate-950 flex items-center justify-center text-xs font-medium"
                      style={{ backgroundColor: getUserColor(user.id) }}
                      title={user.name}
                    >
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                  ))}
                  {users.length > 5 && (
                    <div className="w-6 h-6 rounded-full bg-slate-700 border-2 border-slate-950 flex items-center justify-center text-xs">
                      +{users.length - 5}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex-1 relative">
              <textarea
                value={codeContent}
                onChange={(e) => handleCodeChange(e.target.value)}
                className="w-full h-full bg-transparent text-sm font-mono leading-relaxed text-slate-300 resize-none focus:outline-none"
                spellCheck={false}
              />

              {/* Remote cursors */}
              {Object.entries(cursors).map(([cursorUserId, pos]) => {
                if (cursorUserId === userId) return null
                const user = users.find(u => u.id === cursorUserId)
                return (
                  <div
                    key={cursorUserId}
                    className="absolute pointer-events-none"
                    style={{
                      top: `${pos.line * 1.5}rem`,
                      left: `${pos.column * 0.6}ch`
                    }}
                  >
                    <div
                      className="w-0.5 h-5 animate-pulse"
                      style={{ backgroundColor: getUserColor(cursorUserId) }}
                    />
                    <span
                      className="text-xs px-1 rounded"
                      style={{ backgroundColor: getUserColor(cursorUserId) }}
                    >
                      {user?.name || 'Unknown'}
                    </span>
                  </div>
                )
              })}
            </div>

            {/* Cursor indicators */}
            <div className="mt-4 flex items-center gap-4 flex-wrap">
              {users.filter(u => u.id !== userId).map(user => (
                <div key={user.id} className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: getUserColor(user.id) }}
                  />
                  <span className="text-xs text-slate-500">{user.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a message or paste code..."
              className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            />
            <button
              onClick={sendMessage}
              disabled={!newMessage.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar - Participants & Chat */}
      <div className="flex flex-col gap-4">
        {/* Participants */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Participants ({users.length})
          </h3>
          <div className="space-y-2">
            {users.map(user => (
              <div key={user.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                      style={{ backgroundColor: getUserColor(user.id) }}
                    >
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <span className={cn(
                      'absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-slate-900',
                      user.status === 'online' ? 'bg-emerald-500' :
                      user.status === 'away' ? 'bg-amber-500' : 'bg-red-500'
                    )} />
                  </div>
                  <div>
                    <p className="text-sm">{user.name} {user.id === userId && '(You)'}</p>
                    <p className="text-xs text-slate-500 capitalize">{user.role || 'viewer'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800">
            <h3 className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat
            </h3>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-4">
            {messages.length === 0 && (
              <p className="text-center text-sm text-slate-500 py-8">
                No messages yet. Start the conversation!
              </p>
            )}
            {messages.map(message => {
              const isSystem = message.type === 'system'
              const isOwn = message.user.id === userId

              if (isSystem) {
                return (
                  <div key={message.id} className="text-center">
                    <span className="text-xs text-slate-500">{message.content}</span>
                  </div>
                )
              }

              return (
                <div key={message.id} className={cn('flex gap-2', isOwn && 'flex-row-reverse')}>
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0"
                    style={{ backgroundColor: getUserColor(message.user.id) }}
                  >
                    {message.user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className={cn(
                    'max-w-[80%]',
                    isOwn ? 'text-right' : 'text-left'
                  )}>
                    <div className={cn('flex items-center gap-2 mb-1', isOwn && 'flex-row-reverse')}>
                      <span className="text-xs font-medium">{message.user.name}</span>
                      <span className="text-xs text-slate-500">{formatTime(message.timestamp)}</span>
                    </div>
                    {message.type === 'code' ? (
                      <pre className="text-xs bg-slate-950 p-2 rounded overflow-x-auto">
                        <code className="text-emerald-400">{message.content}</code>
                      </pre>
                    ) : (
                      <p className={cn(
                        'text-sm px-3 py-2 rounded-lg',
                        isOwn ? 'bg-blue-600' : 'bg-slate-800'
                      )}>
                        {message.content}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>
    </div>
  )
}
