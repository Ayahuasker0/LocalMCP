import { useState } from 'react'

interface ToolExecutionProps {
  name: string
  content: string
  isError?: boolean
}

export default function ToolExecution({ name, content, isError = false }: ToolExecutionProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`tool-execution ${isError ? 'error' : ''}`}>
      <div className="tool-header">
        <span className="tool-name">{name}</span>
        <button
          className="tool-toggle"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? 'Hide' : 'Show'}
        </button>
      </div>
      {expanded && (
        <pre className="tool-content">{content}</pre>
      )}
    </div>
  )
}
