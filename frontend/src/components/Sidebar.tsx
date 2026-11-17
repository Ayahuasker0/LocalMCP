import { useState } from 'react'

interface SidebarProps {
  onSend: (message: string) => void
}

const COMMANDS = [
  { label: '/overview', description: 'Analyze project overview' },
  { label: '/review <path>', description: 'Review a Java class' },
  { label: '/performance <module>', description: 'Analyze module performance' },
]

export default function Sidebar({ onSend }: SidebarProps) {
  const [active, setActive] = useState<string | null>(null)

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Local MCP Agent</h2>
      </div>

      <div className="sidebar-section">
        <h3>Commands</h3>
        <ul className="command-list">
          {COMMANDS.map((cmd) => (
            <li
              key={cmd.label}
              className={active === cmd.label ? 'active' : ''}
              onClick={() => {
                setActive(cmd.label)
                onSend(cmd.label)
              }}
            >
              <code>{cmd.label}</code>
              <span className="command-desc">{cmd.description}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-footer">
        <p>Connected to Ollama + MCP servers</p>
      </div>
    </aside>
  )
}
