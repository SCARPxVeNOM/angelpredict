import { X, TrendingDown, DollarSign, Package, CheckCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency, formatPercent } from '../utils/formatters'
import type { Stock } from '../types'
import MiniChart from './MiniChart'

interface StockDetailDrawerProps {
  stock: Stock
  onClose: () => void
}

const StockDetailDrawer = ({ stock, onClose }: StockDetailDrawerProps) => {
  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-end">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />

        {/* Drawer */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="relative w-[480px] h-full bg-dark-surface border-l border-dark-border overflow-y-auto"
        >
          {/* Header */}
          <div className="sticky top-0 bg-dark-surface border-b border-dark-border p-6 z-10">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-100">{stock.symbol}</h2>
                <p className="text-sm text-gray-500">{stock.name}</p>
              </div>
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-lg bg-dark-elevated hover:bg-dark-hover border border-dark-border transition-colors flex items-center justify-center"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold font-mono text-gray-100">
                {formatCurrency(stock.lastClose)}
              </span>
              <span className={`text-lg font-semibold font-mono ${
                stock.dropPercent < 0 ? 'text-accent-danger' : 'text-accent-success'
              }`}>
                {formatPercent(stock.dropPercent)}
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Mini Chart */}
            <div className="glass rounded-xl p-4 border border-dark-border">
              <h3 className="text-sm font-semibold text-gray-400 mb-4">Price Movement (1D)</h3>
              <MiniChart stock={stock} />
            </div>

            {/* Price Details */}
            <div className="glass rounded-xl p-4 border border-dark-border">
              <h3 className="text-sm font-semibold text-gray-400 mb-4">Price Details</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Previous Close</span>
                  <span className="font-mono text-sm font-semibold text-gray-200">
                    {formatCurrency(stock.previousClose)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Last Close</span>
                  <span className="font-mono text-sm font-semibold text-gray-200">
                    {formatCurrency(stock.lastClose)}
                  </span>
                </div>
                <div className="flex justify-between items-center pt-3 border-t border-dark-border">
                  <span className="text-sm text-gray-500">Drop Amount</span>
                  <span className="font-mono text-sm font-semibold text-accent-danger">
                    {formatCurrency(stock.lastClose - stock.previousClose)}
                  </span>
                </div>
              </div>
            </div>

            {/* Order Simulation */}
            <div className="glass rounded-xl p-4 border border-dark-border">
              <h3 className="text-sm font-semibold text-gray-400 mb-4">Order Simulation</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated">
                  <DollarSign className="w-5 h-5 text-accent-primary" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-500">Allocated Amount</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">
                      {formatCurrency(stock.allocatedAmount)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated">
                  <Package className="w-5 h-5 text-accent-primary" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-500">Quantity</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">
                      {stock.quantity} shares
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-elevated">
                  <TrendingDown className="w-5 h-5 text-accent-primary" />
                  <div className="flex-1">
                    <p className="text-xs text-gray-500">Rank</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">
                      #{stock.rank} of 5
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Status */}
            <div className={`rounded-xl p-4 border ${
              stock.orderStatus === 'simulated' 
                ? 'bg-accent-success/10 border-accent-success/30' 
                : 'bg-accent-warning/10 border-accent-warning/30'
            }`}>
              <div className="flex items-center gap-3">
                <CheckCircle className={`w-5 h-5 ${
                  stock.orderStatus === 'simulated' ? 'text-accent-success' : 'text-accent-warning'
                }`} />
                <div>
                  <p className="text-sm font-semibold text-gray-200">
                    {stock.orderStatus === 'simulated' ? 'Order Simulated' : 'Order Pending'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {stock.orderStatus === 'simulated' 
                      ? 'Successfully placed in paper trading mode' 
                      : 'Waiting for market open'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

export default StockDetailDrawer
