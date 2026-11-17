export type Role = 'user' | 'assistant' | 'tool' | 'system'

export interface ToolCall {
  name: string
  arguments: Record<string, unknown>
}

export interface ToolResult {
  name: string
  content: string
  isError: boolean
}

export interface ChatMessage {
  id: string
  role: Role
  content: string
  toolCalls?: ToolCall[]
  toolName?: string
  createdAt: number
}

export interface AgentStatus {
  state: 'idle' | 'thinking' | 'calling_tool' | 'error'
  detail?: string
}

export interface ChatResponse {
  messages: ChatMessage[]
  status: AgentStatus
}
