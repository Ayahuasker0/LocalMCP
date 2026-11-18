import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'
import AgentStatus from './components/AgentStatus'
import { sendChat } from './services/api'
import type { ChatMessage, AgentStatus as Status } from './types/chat'
import './App.css'

function makeId() {
  return Math.random().toString(36).slice(2, 10)
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<Status>({ state: 'idle' })
  const [error, setError] = useState<string | null>(null)

  const handleSend = async (input: string) => {
    const userMsg: ChatMessage = {
      id: makeId(),
      role: 'user',
      content: input,
      createdAt: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])
    setStatus({ state: 'thinking' })
    setError(null)

    try {
      const { messages: reply } = await sendChat(input)
      // The response tail starts with the user message we already appended.
      setMessages((prev) => [...prev, ...reply.slice(1)])
      setStatus({ state: 'idle' })
    } catch (e) {
      setStatus({ state: 'error' })
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="app-layout">
      <Sidebar onSend={handleSend} />
      <main className="chat-main">
        <header className="chat-header">
          <h1>Chat</h1>
          <AgentStatus status={status} />
        </header>
        <div className="chat-body">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Send a message or pick a command from the sidebar to start.</p>
            </div>
          ) : (
            <ChatWindow messages={messages} />
          )}
          {error && <div className="chat-error">{error}</div>}
        </div>
        <ChatInput onSend={handleSend} disabled={status.state !== 'idle'} />
      </main>
    </div>
  )
}
