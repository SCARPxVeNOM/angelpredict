import { motion } from 'framer-motion'

interface AISuggestedPromptsProps {
  onPromptClick: (prompt: string) => void
  disabled?: boolean
}

const AISuggestedPrompts = ({ onPromptClick, disabled }: AISuggestedPromptsProps) => {
  const prompts = [
    { text: 'Why were these stocks selected?', icon: '🎯' },
    { text: 'Why were some stocks rejected?', icon: '❌' },
    { text: 'Which trade is riskiest today?', icon: '⚠️' },
    { text: 'Explain capital allocation', icon: '💰' },
    { text: 'What if threshold was −4%?', icon: '🔄' },
    { text: 'Summarize today\'s trades', icon: '📊' }
  ]

  return (
    <div className="space-y-3">
      <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Suggested Questions</p>
      <div className="grid grid-cols-2 gap-2">
        {prompts.map((prompt, index) => (
          <motion.button
            key={prompt.text}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => !disabled && onPromptClick(prompt.text)}
            disabled={disabled}
            className="text-left px-3 py-2.5 rounded-lg bg-dark-elevated border border-dark-border hover:border-accent-primary/30 hover:bg-dark-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <div className="flex items-start gap-2">
              <span className="text-base flex-shrink-0">{prompt.icon}</span>
              <span className="text-xs text-gray-400 group-hover:text-gray-300 font-medium leading-relaxed">
                {prompt.text}
              </span>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}

export default AISuggestedPrompts
