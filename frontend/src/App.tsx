import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'
import AgentStatus from './components/AgentStatus'
import type { ChatMessage, AgentStatus as Status } from './types/chat'
import './App.css'

function makeId() {
  return Math.random().toString(36).slice(2, 10)
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [status, setStatus] = useState<Status>({ state: 'idle' })

  const handleSend = (input: string) => {
    const userMsg: ChatMessage = {
      id: makeId(),
      role: 'user',
      content: input,
      createdAt: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])
    setStatus({ state: 'thinking' })

    // Placeholder: wire to the backend chat endpoint here.
    // The agent loop (agent/agent_loop.py) streams tool calls + final answer.
    setTimeout(() => {
      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: 'Hello! I am the local MCP agent. Connect me to the backend to run real tool calls.',
        createdAt: Date.now(),
      }
      setMessages((prev) => [...prev, assistantMsg])
      setStatus({ state: 'idle' })
    }, 600)
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
        </div>
        <ChatInput onSend={handleSend} disabled={status.state !== 'idle'} />
      </main>
    </div>
  )
}
