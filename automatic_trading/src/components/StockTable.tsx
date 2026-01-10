import { useState } from 'react'
import { ArrowUpDown, TrendingDown, ChevronRight, Sparkles } from 'lucide-react'
import { formatCurrency, formatPercent } from '../utils/formatters'
import StockDetailDrawer from './StockDetailDrawer'
import { motion } from 'framer-motion'
import { useAI } from '../contexts/AIContext'
import type { Stock } from '../types'
import { apiService } from '../services/api'

const StockTable = () => {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(false)
  const { openDrawer } = useAI()

  // Don't auto-fetch stocks - only load from manual trigger or backtest
  // Remove automatic fetching to prevent unnecessary API calls
  
  const fetchStocks = async () => {
    try {
      setLoading(true)
      const data = await apiService.fetchStocks()
      setStocks(data)
    } catch (error) {
      console.error('Error fetching stocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      simulated: 'bg-accent-success/10 text-accent-success border-accent-success/30',
      pending: 'bg-accent-warning/10 text-accent-warning border-accent-warning/30',
      failed: 'bg-accent-danger/10 text-accent-danger border-accent-danger/30'
    }
    return styles[status as keyof typeof styles] || styles.pending
  }

  const handleExplainStock = (e: React.MouseEvent, stock: Stock) => {
    e.stopPropagation()
    openDrawer(
      `Explain why ${stock.symbol} was selected`,
      {
        stockSymbol: stock.symbol,
        type: 'stock',
        dropPercent: stock.dropPercent,
        rank: stock.rank,
        quantity: stock.quantity,
        price: stock.lastClose
      }
    )
  }

  return (
    <>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-2xl border border-dark-border overflow-hidden"
      >
        <div className="p-6 border-b border-dark-border bg-dark-elevated/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-accent-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-100">Stock Scanner Results</h2>
                <p className="text-xs text-gray-500 font-medium">Top 5 stocks with ≤ −5% drop • Click row for details</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={fetchStocks}
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-accent-primary/10 border border-accent-primary/30 hover:bg-accent-primary/20 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-accent-primary" />
                <span className="text-sm font-semibold text-accent-primary">
                  {loading ? 'Scanning...' : 'Scan Now'}
                </span>
              </button>
              <div className="px-3 py-1.5 rounded-lg bg-dark-surface border border-dark-border">
                <span className="text-xs text-gray-500 font-medium">Total: </span>
                <span className="text-xs font-bold text-accent-primary">{stocks.length} stocks</span>
              </div>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-elevated/50 sticky top-0 backdrop-blur-sm">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">Rank</th>
                <th className="px-6 py-4 font-semibold">Stock</th>
                <th className="px-6 py-4 font-semibold">
                  <button className="flex items-center gap-1 hover:text-gray-300 transition-colors">
                    Prev Close <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">Last Close</th>
                <th className="px-6 py-4 font-semibold">
                  <button className="flex items-center gap-1 hover:text-gray-300 transition-colors">
                    % Drop <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">Allocated</th>
                <th className="px-6 py-4 font-semibold">Quantity</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                    Scanning stocks...
                  </td>
                </tr>
              ) : stocks.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                    <div className="flex flex-col items-center gap-2">
                      <p>No stocks loaded</p>
                      <p className="text-xs">Click "Scan Now" to find eligible stocks</p>
                    </div>
                  </td>
                </tr>
              ) : (
                stocks.map((stock, index) => (
                <motion.tr
                  key={stock.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.05 }}
                  onClick={() => setSelectedStock(stock)}
                  className="hover:bg-dark-elevated/50 transition-all cursor-pointer group"
                >
                  <td className="px-6 py-4">
                    <div className="w-8 h-8 rounded-lg bg-accent-primary/10 flex items-center justify-center border border-accent-primary/20">
                      <span className="text-sm font-bold text-accent-primary">{stock.rank}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold text-gray-200 group-hover:text-accent-primary transition-colors">
                        {stock.symbol}
                      </p>
                      <p className="text-xs text-gray-500 font-medium">{stock.name}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-300 font-medium">{formatCurrency(stock.previousClose)}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-300 font-medium">{formatCurrency(stock.lastClose)}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`font-mono text-sm font-bold ${
                      stock.dropPercent < 0 ? 'text-accent-danger' : 'text-accent-success'
                    }`}>
                      {formatPercent(stock.dropPercent)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-300 font-medium">{formatCurrency(stock.allocatedAmount)}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm font-bold text-gray-200">{stock.quantity}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-md text-xs font-bold border ${getStatusBadge(stock.orderStatus)}`}>
                        {stock.orderStatus.toUpperCase()}
                      </span>
                      <button
                        onClick={(e) => handleExplainStock(e, stock)}
                        className="text-xs text-accent-primary hover:text-accent-secondary font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Sparkles className="w-3 h-3" />
                        Explain
                      </button>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-accent-primary transition-colors" />
                  </td>
                </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      {selectedStock && (
        <StockDetailDrawer
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </>
  )
}

export default StockTable
