'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Users, Send, Video, Mic, MicOff, VideoOff,
  Share, MessageSquare, Code, Eye, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface User {
  id: string
  name: string
  avatar: string
  status: 'online' | 'away' | 'busy'
  role: 'owner' | 'editor' | 'viewer'
}

interface Message {
  id: string
  userId: string
  content: string
  timestamp: Date
  type: 'text' | 'code' | 'system'
}

const DEMO_USERS: User[] = [
  { id: '1', name: 'You', avatar: '👤', status: 'online', role: 'owner' },
  { id: '2', name: 'Sarah Chen', avatar: '👩‍💻', status: 'online', role: 'editor' },
  { id: '3', name: 'Mike Johnson', avatar: '👨‍💻', status: 'online', role: 'viewer' },
]

const DEMO_MESSAGES: Message[] = [
  {
    id: '1',
    userId: '2',
    content: 'I noticed the SQL injection issue on line 10. Should we use an ORM instead?',
    timestamp: new Date(Date.now() - 300000),
    type: 'text'
  },
  {
    id: '2',
    userId: '1',
    content: 'Good catch! Let me update to use SQLAlchemy with parameterized queries.',
    timestamp: new Date(Date.now() - 240000),
    type: 'text'
  },
  {
    id: '3',
    userId: 'system',
    content: 'Sarah Chen started editing authentication.py',
    timestamp: new Date(Date.now() - 180000),
    type: 'system'
  },
  {
    id: '4',
    userId: '2',
    content: 'query = db.query(User).filter(User.username == username).first()',
    timestamp: new Date(Date.now() - 120000),
    type: 'code'
  },
]

export function LiveCollaboration() {
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES)
  const [newMessage, setNewMessage] = useState('')
  const [isVideoOn, setIsVideoOn] = useState(false)
  const [isMicOn, setIsMicOn] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = () => {
    if (!newMessage.trim()) return

    const isCode = newMessage.startsWith('```') || newMessage.includes('\n')

    setMessages(prev => [...prev, {
      id: String(Date.now()),
      userId: '1',
      content: newMessage,
      timestamp: new Date(),
      type: isCode ? 'code' : 'text'
    }])
    setNewMessage('')
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getUserById = (id: string) => DEMO_USERS.find(u => u.id === id)

  return (
    <div className="grid grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
      {/* Main Collaboration Area */}
      <div className="col-span-3 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <h2 className="font-medium">Live Code Review Session</h2>
            <span className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full pulse-dot" />
              <span className="text-xs text-emerald-400">Live</span>
            </span>
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
          <div className="bg-slate-950 rounded-lg p-4 h-full">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4 text-slate-500" />
                <span className="text-sm text-slate-400">authentication.py</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">3 viewers</span>
                <div className="flex -space-x-2">
                  {DEMO_USERS.map(user => (
                    <div
                      key={user.id}
                      className="w-6 h-6 rounded-full bg-slate-700 border-2 border-slate-950 flex items-center justify-center text-xs"
                      title={user.name}
                    >
                      {user.avatar}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <pre className="text-sm font-mono leading-relaxed">
              <code className="text-slate-300">
{`from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

app = FastAPI()

@app.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Secure parameterized query
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not bcrypt.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"token": generate_jwt_token(user.id)}`}
              </code>
            </pre>

            {/* Cursor indicators */}
            <div className="mt-4 flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full" />
                <span className="text-xs text-slate-500">Sarah editing line 9</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full" />
                <span className="text-xs text-slate-500">Mike viewing</span>
              </div>
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
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
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
            Participants
          </h3>
          <div className="space-y-2">
            {DEMO_USERS.map(user => (
              <div key={user.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <span className="text-lg">{user.avatar}</span>
                    <span className={cn(
                      'absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-slate-900',
                      user.status === 'online' ? 'bg-emerald-500' :
                      user.status === 'away' ? 'bg-amber-500' : 'bg-red-500'
                    )} />
                  </div>
                  <div>
                    <p className="text-sm">{user.name}</p>
                    <p className="text-xs text-slate-500 capitalize">{user.role}</p>
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
            {messages.map(message => {
              const user = getUserById(message.userId)
              const isSystem = message.type === 'system'
              const isOwn = message.userId === '1'

              if (isSystem) {
                return (
                  <div key={message.id} className="text-center">
                    <span className="text-xs text-slate-500">{message.content}</span>
                  </div>
                )
              }

              return (
                <div key={message.id} className={cn('flex gap-2', isOwn && 'flex-row-reverse')}>
                  <span className="text-lg">{user?.avatar || '👤'}</span>
                  <div className={cn(
                    'max-w-[80%]',
                    isOwn ? 'text-right' : 'text-left'
                  )}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium">{user?.name}</span>
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
