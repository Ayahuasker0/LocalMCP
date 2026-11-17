import type { AgentStatus as Status } from '../types/chat'

interface AgentStatusProps {
  status: Status
}

const LABELS: Record<Status['state'], string> = {
  idle: 'Idle',
  thinking: 'Thinking…',
  calling_tool: 'Calling tool…',
  error: 'Error',
}

export default function AgentStatus({ status }: AgentStatusProps) {
  return (
    <div className={`agent-status ${status.state}`}>
      <span className="status-dot" />
      <span className="status-label">{LABELS[status.state]}</span>
      {status.detail && <span className="status-detail">{status.detail}</span>}
    </div>
  )
}
