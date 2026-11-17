import { useState } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled: boolean
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <div className="chat-input">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask the agent… (use /overview, /review, /performance)"
        disabled={disabled}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault()
            submit()
          }
        }}
      />
      <button className="send-button" onClick={submit} disabled={disabled || !value.trim()}>
        Send
      </button>
    </div>
  )
}
