import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'
import { TrendingUp, Wallet, DollarSign, Activity, Sparkles } from 'lucide-react'
import { formatCurrency } from '../utils/formatters'
import { motion } from 'framer-motion'
import { useAI } from '../contexts/AIContext'
import { CapitalInfo, apiService } from '../services/api'

const CapitalOverview = forwardRef((_props, ref) => {
  const { openDrawer } = useAI()
  const [capital, setCapital] = useState<CapitalInfo>({
    total: 300000,
    deployed: 0,
    available: 300000,
    scanCount: 0
  })
  const [loading, setLoading] = useState(false)

  const fetchCapital = async () => {
    try {
      setLoading(true)
      const data = await apiService.fetchCapital()
      setCapital(data)
    } catch (error) {
      console.error('Error fetching capital:', error)
    } finally {
      setLoading(false)
    }
  }

  // Expose refresh function to parent components
  useImperativeHandle(ref, () => ({
    refresh: fetchCapital
  }))

  // Fetch capital on mount
  useEffect(() => {
    fetchCapital()
  }, [])

  const handleExplainClick = () => {
    openDrawer('Explain capital allocation', { capital })
  }
  
  const cards = [
    {
      title: 'Total Capital',
      value: capital.total,
      icon: Wallet,
      iconColor: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
      hoverBorder: 'hover:border-blue-500/40'
    },
    {
      title: 'Capital Deployed',
      value: capital.deployed,
      icon: TrendingUp,
      iconColor: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
      hoverBorder: 'hover:border-purple-500/40'
    },
    {
      title: 'Available Balance',
      value: capital.available,
      icon: DollarSign,
      iconColor: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
      hoverBorder: 'hover:border-emerald-500/40'
    },
    {
      title: "Today's Scan Count",
      value: capital.scanCount,
      icon: Activity,
      iconColor: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
      hoverBorder: 'hover:border-amber-500/40',
      isCount: true
    }
  ]

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Capital Overview</h3>
        <button
          onClick={handleExplainClick}
          className="text-xs text-accent-primary hover:text-accent-secondary font-medium flex items-center gap-1 transition-colors"
        >
          <Sparkles className="w-3 h-3" />
          Explain allocation
        </button>
      </div>
      <div className="grid grid-cols-4 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              delay: index * 0.08,
              duration: 0.4,
              ease: [0.4, 0, 0.2, 1]
            }}
            whileHover={{ y: -2 }}
            className={`glass rounded-2xl p-6 border ${card.borderColor} ${card.hoverBorder} transition-all cursor-default ${loading ? 'opacity-50' : ''}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl ${card.bgColor} flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${card.iconColor}`} />
              </div>
            </div>
            
            <p className="text-sm text-gray-400 mb-2 font-medium">{card.title}</p>
            <motion.p 
              className="text-3xl font-bold font-mono tracking-tight text-gray-100"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.08 + 0.2 }}
            >
              {card.isCount ? card.value : formatCurrency(card.value)}
            </motion.p>
          </motion.div>
        )
      })}
    </div>
    </div>
  )
})

CapitalOverview.displayName = 'CapitalOverview'

export default CapitalOverview
