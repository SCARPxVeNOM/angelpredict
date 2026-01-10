import { Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAI } from '../../contexts/AIContext'

interface AIFloatingButtonProps {
  hasNewScan?: boolean
}

const AIFloatingButton = ({ hasNewScan = false }: AIFloatingButtonProps) => {
  const { openDrawer, isOpen } = useAI()

  if (isOpen) return null

  return (
    <motion.button
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.5, type: 'spring', stiffness: 260, damping: 20 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => openDrawer()}
      className="fixed bottom-6 right-6 z-40 group"
    >
      <div className="relative">
        {/* Pulse effect when new scan */}
        {hasNewScan && (
          <motion.div
            animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 rounded-2xl bg-accent-primary"
          />
        )}
        
        {/* Main button */}
        <div className="relative glass rounded-2xl px-5 py-4 border border-accent-primary/30 bg-accent-primary/10 hover:bg-accent-primary/20 transition-all shadow-lg shadow-accent-primary/20">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Sparkles className="w-6 h-6 text-accent-primary" />
              {hasNewScan && (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="absolute -top-1 -right-1 w-3 h-3 bg-accent-warning rounded-full border-2 border-dark-surface"
                />
              )}
            </div>
            <div className="text-left">
              <p className="text-sm font-bold text-accent-primary">AI Analyst</p>
              <p className="text-xs text-gray-400 font-medium">Ask me anything</p>
            </div>
          </div>
        </div>
      </div>
    </motion.button>
  )
}

export default AIFloatingButton
