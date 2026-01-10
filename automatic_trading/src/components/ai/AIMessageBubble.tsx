import { User, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import type { AIMessage } from '../../types/ai'

interface AIMessageBubbleProps {
  message: AIMessage
}

const AIMessageBubble = ({ message }: AIMessageBubbleProps) => {
  const isUser = message.role === 'user'

  // Format AI response with markdown-like styling
  const formatContent = (content: string) => {
    const lines = content.split('\n')
    return lines.map((line, index) => {
      // Headers (lines starting with **)
      if (line.startsWith('**') && line.endsWith('**')) {
        const text = line.replace(/\*\*/g, '')
        return (
          <h4 key={index} className="font-bold text-gray-100 mt-3 mb-1 text-sm">
            {text}
          </h4>
        )
      }

      // Bold inline text
      if (line.includes('**')) {
        const parts = line.split('**')
        return (
          <p key={index} className="text-sm text-gray-300 mb-1 leading-relaxed">
            {parts.map((part, i) => 
              i % 2 === 1 ? <strong key={i} className="text-gray-100 font-semibold">{part}</strong> : part
            )}
          </p>
        )
      }

      // Bullet points
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return (
          <li key={index} className="text-sm text-gray-300 ml-4 mb-1 leading-relaxed">
            {line.substring(2)}
          </li>
        )
      }

      // Warning/Info markers
      if (line.startsWith('⚠️') || line.startsWith('🔴') || line.startsWith('🟡')) {
        return (
          <div key={index} className="px-3 py-2 rounded-lg bg-accent-warning/10 border border-accent-warning/30 text-sm text-accent-warning font-medium mb-2 mt-2">
            {line}
          </div>
        )
      }

      if (line.startsWith('✅') || line.startsWith('🟢')) {
        return (
          <div key={index} className="px-3 py-2 rounded-lg bg-accent-success/10 border border-accent-success/30 text-sm text-accent-success font-medium mb-2 mt-2">
            {line}
          </div>
        )
      }

      if (line.startsWith('💡') || line.startsWith('🔵')) {
        return (
          <div key={index} className="px-3 py-2 rounded-lg bg-accent-primary/10 border border-accent-primary/30 text-sm text-accent-primary font-medium mb-2 mt-2">
            {line}
          </div>
        )
      }

      // Table detection (simple)
      if (line.includes('|') && line.split('|').length > 2) {
        const cells = line.split('|').filter(cell => cell.trim())
        const isHeader = index > 0 && lines[index - 1].includes('|')
        
        return (
          <div key={index} className="flex gap-2 text-xs font-mono mb-1">
            {cells.map((cell, i) => (
              <span 
                key={i} 
                className={`flex-1 ${isHeader ? 'font-bold text-gray-100' : 'text-gray-400'}`}
              >
                {cell.trim()}
              </span>
            ))}
          </div>
        )
      }

      // Regular text
      if (line.trim()) {
        return (
          <p key={index} className="text-sm text-gray-300 mb-1 leading-relaxed">
            {line}
          </p>
        )
      }

      return <br key={index} />
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-accent-primary/10 border border-accent-primary/30' 
          : 'bg-dark-elevated border border-dark-border'
      }`}>
        {isUser ? (
          <User className="w-4 h-4 text-accent-primary" />
        ) : (
          <Sparkles className="w-4 h-4 text-accent-primary" />
        )}
      </div>

      {/* Message bubble */}
      <div className={`flex-1 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-xl px-4 py-3 ${
          isUser
            ? 'bg-accent-primary/10 border border-accent-primary/30'
            : 'glass border border-dark-border'
        }`}>
          {isUser ? (
            <p className="text-sm text-gray-200 font-medium">{message.content}</p>
          ) : (
            <div className="space-y-1">
              {formatContent(message.content)}
            </div>
          )}
        </div>
        <p className="text-xs text-gray-600 mt-1 px-1 font-mono">{message.timestamp}</p>
      </div>
    </motion.div>
  )
}

export default AIMessageBubble
