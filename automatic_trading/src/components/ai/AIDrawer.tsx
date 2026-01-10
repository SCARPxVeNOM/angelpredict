import { X, Send, Loader2, Trash2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useRef, useEffect } from 'react'
import { useAI } from '../../contexts/AIContext'
import AIMessageBubble from './AIMessageBubble'
import AISuggestedPrompts from './AISuggestedPrompts'

const AIDrawer = () => {
  const { isOpen, closeDrawer, messages, isLoading, sendMessage, clearChat } = useAI()
  const [input, setInput] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Focus input when drawer opens
  useEffect(() => {
    if (isOpen && !isLoading) {
      inputRef.current?.focus()
    }
  }, [isOpen, isLoading])

  const handleSend = () => {
    if (!input.trim() || isLoading) return
    sendMessage(input.trim())
    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handlePromptClick = (prompt: string) => {
    sendMessage(prompt)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeDrawer}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-[480px] bg-dark-surface border-l border-dark-border z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex-shrink-0 p-6 border-b border-dark-border bg-dark-elevated/50">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h2 className="text-xl font-bold text-gray-100">AI Market Analyst</h2>
                  <p className="text-xs text-gray-500 font-medium mt-1">Powered by simulation data</p>
                </div>
                <div className="flex items-center gap-2">
                  {messages.length > 0 && (
                    <button
                      onClick={clearChat}
                      className="w-9 h-9 rounded-lg bg-dark-surface hover:bg-dark-hover border border-dark-border transition-colors flex items-center justify-center group"
                      title="Clear chat"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 group-hover:text-accent-danger transition-colors" />
                    </button>
                  )}
                  <button
                    onClick={closeDrawer}
                    className="w-9 h-9 rounded-lg bg-dark-surface hover:bg-dark-hover border border-dark-border transition-colors flex items-center justify-center"
                  >
                    <X className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-accent-warning/10 border border-accent-warning/30">
                <div className="w-2 h-2 rounded-full bg-accent-warning animate-pulse-subtle" />
                <span className="text-xs font-bold text-accent-warning uppercase tracking-wider">Simulation Only</span>
              </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="space-y-6">
                  {/* Welcome message */}
                  <div className="glass rounded-xl p-4 border border-dark-border">
                    <h3 className="text-sm font-semibold text-gray-200 mb-2">👋 Welcome to AI Analyst</h3>
                    <p className="text-xs text-gray-400 leading-relaxed mb-3">
                      I can help you understand today's scan results, explain trading decisions, and analyze risk factors.
                    </p>
                    <div className="space-y-1 text-xs text-gray-500">
                      <p className="flex items-center gap-2">
                        <span className="text-accent-success">✓</span> Explain stock selections
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-accent-success">✓</span> Analyze risk factors
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-accent-success">✓</span> What-if scenarios
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-accent-danger">✗</span> Price predictions
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-accent-danger">✗</span> Trading advice
                      </p>
                    </div>
                  </div>

                  {/* Suggested prompts */}
                  <AISuggestedPrompts onPromptClick={handlePromptClick} disabled={isLoading} />
                </div>
              ) : (
                <>
                  {messages.map((message) => (
                    <AIMessageBubble key={message.id} message={message} />
                  ))}
                </>
              )}

              {/* Loading indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-dark-elevated border border-dark-border flex items-center justify-center">
                    <Loader2 className="w-4 h-4 text-accent-primary animate-spin" />
                  </div>
                  <div className="glass rounded-xl px-4 py-3 border border-dark-border">
                    <p className="text-sm text-gray-400 font-medium">Analyzing data...</p>
                  </div>
                </motion.div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 p-4 border-t border-dark-border bg-dark-elevated/50">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  placeholder="Ask about today's scan..."
                  className="flex-1 px-4 py-3 rounded-lg bg-dark-surface border border-dark-border text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-primary/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="w-12 h-12 rounded-lg bg-accent-primary/10 border border-accent-primary/30 hover:bg-accent-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center group"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 text-accent-primary animate-spin" />
                  ) : (
                    <Send className="w-5 h-5 text-accent-primary group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-600 mt-2 text-center font-medium">
                Press Enter to send • This is a simulation environment
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default AIDrawer
