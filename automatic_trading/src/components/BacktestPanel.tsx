import { useState } from 'react'
import { Play, TrendingUp, DollarSign, BarChart3, Calendar, Loader } from 'lucide-react'
import { formatCurrency } from '../utils/formatters'
import { apiService } from '../services/api'
import { motion } from 'framer-motion'

interface BacktestResult {
  date: string
  eligible_stocks: number
  selected_stocks: number
  orders: Array<{
    symbol: string
    name: string
    price: number
    quantity: number
    amount: number
    fall_percentage: number
  }>
  total_allocated: number
  capital_utilization: number
}

interface BacktestSummary {
  period: string
  total_days: number
  simulated_days: number
  total_orders: number
  total_allocated: number
  average_daily_allocation: number
  unique_stocks: number
  average_orders_per_day: number
  results: BacktestResult[]
}

const BacktestPanel = () => {
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<BacktestSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runBacktest = async () => {
    try {
      setLoading(true)
      setError(null)
      setResults(null)
      const data = await apiService.runBacktest(days)
      
      // Check if response contains error
      if (data && data.error) {
        setError(data.error)
        return
      }
      
      setResults(data)
    } catch (err: any) {
      const errorMsg = err?.message || err?.error || 'Failed to run backtest. Please check backend configuration and logs.'
      setError(errorMsg)
      console.error('Backtest error:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadLatestResults = async () => {
    try {
      setLoading(true)
      setError(null)
      setResults(null)
      const data = await apiService.getBacktestResults()
      
      // Check if response contains error
      if (data && data.error) {
        setError(data.error)
        return
      }
      
      setResults(data)
    } catch (err: any) {
      const errorMsg = err?.message || err?.error || 'No previous backtest results found. Run a backtest first.'
      setError(errorMsg)
      console.error('Load results error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Backtest Simulation</h1>
          <p className="text-sm text-gray-500 mt-1">Simulate trading algorithm performance for past days</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadLatestResults}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-dark-elevated border border-dark-border hover:bg-dark-surface transition-all disabled:opacity-50"
          >
            Load Latest Results
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="glass rounded-2xl border border-dark-border p-6">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="text-sm text-gray-400 mb-2 block">Number of Days</label>
            <input
              type="number"
              min="1"
              max="30"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value) || 7)}
              className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-gray-100 focus:outline-none focus:border-accent-primary"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={runBacktest}
              disabled={loading}
              className="px-6 py-2 rounded-lg bg-accent-primary/10 border border-accent-primary/30 hover:bg-accent-primary/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin text-accent-primary" />
                  <span className="text-sm font-semibold text-accent-primary">Running...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 text-accent-primary" />
                  <span className="text-sm font-semibold text-accent-primary">Run Backtest</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="glass rounded-2xl border border-accent-danger/30 bg-accent-danger/10 p-4">
          <p className="text-sm text-accent-danger">{error}</p>
        </div>
      )}

      {/* Results Summary */}
      {results && (
        <>
          <div className="grid grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl border border-dark-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Period</p>
                  <p className="text-sm font-semibold text-gray-200">{results.period}</p>
                </div>
              </div>
              <p className="text-2xl font-bold font-mono text-gray-100">
                {results.simulated_days}/{results.total_days} days
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl border border-dark-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Orders</p>
                  <p className="text-sm font-semibold text-gray-200">{results.total_orders}</p>
                </div>
              </div>
              <p className="text-2xl font-bold font-mono text-gray-100">
                {results.average_orders_per_day.toFixed(1)}/day
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl border border-dark-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Allocated</p>
                  <p className="text-sm font-semibold text-gray-200">{formatCurrency(results.total_allocated)}</p>
                </div>
              </div>
              <p className="text-2xl font-bold font-mono text-gray-100">
                {formatCurrency(results.average_daily_allocation)}
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-2xl border border-dark-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Unique Stocks</p>
                  <p className="text-sm font-semibold text-gray-200">{results.unique_stocks}</p>
                </div>
              </div>
              <p className="text-2xl font-bold font-mono text-gray-100">
                {results.unique_stocks}
              </p>
            </motion.div>
          </div>

          {/* Daily Results */}
          <div className="glass rounded-2xl border border-dark-border overflow-hidden">
            <div className="p-6 border-b border-dark-border bg-dark-elevated/30">
              <h2 className="text-lg font-semibold text-gray-100">Daily Breakdown</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-dark-elevated/50">
                  <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                    <th className="px-6 py-4 font-semibold">Date</th>
                    <th className="px-6 py-4 font-semibold">Eligible</th>
                    <th className="px-6 py-4 font-semibold">Selected</th>
                    <th className="px-6 py-4 font-semibold">Orders</th>
                    <th className="px-6 py-4 font-semibold">Allocated</th>
                    <th className="px-6 py-4 font-semibold">Utilization</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-border">
                  {results.results.map((result: BacktestResult, index: number) => (
                    <motion.tr
                      key={result.date}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="hover:bg-dark-elevated/50 transition-all"
                    >
                      <td className="px-6 py-4 font-mono text-sm text-gray-200">{result.date}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{result.eligible_stocks}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-accent-primary">{result.selected_stocks}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{result.orders.length}</td>
                      <td className="px-6 py-4 font-mono text-sm text-gray-200">{formatCurrency(result.total_allocated)}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{result.capital_utilization.toFixed(1)}%</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Stock Details */}
          <div className="glass rounded-2xl border border-dark-border p-6">
            <h2 className="text-lg font-semibold text-gray-100 mb-4">Selected Stocks by Date</h2>
            <div className="space-y-4">
              {results.results.map((result: BacktestResult) => (
                <div key={result.date} className="bg-dark-elevated rounded-xl p-4 border border-dark-border">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-200">{result.date}</h3>
                    <span className="text-xs text-gray-500">{result.orders.length} orders</span>
                  </div>
                  <div className="grid grid-cols-5 gap-3">
                    {result.orders.map((order, idx) => (
                      <div key={idx} className="bg-dark-surface rounded-lg p-3 border border-dark-border">
                        <p className="text-sm font-semibold text-gray-200">{order.symbol}</p>
                        <p className="text-xs text-gray-500">{order.name}</p>
                        <p className="text-xs text-gray-400 mt-1">Qty: {order.quantity}</p>
                        <p className="text-xs font-mono text-accent-primary mt-1">{formatCurrency(order.amount)}</p>
                        <p className="text-xs text-accent-danger mt-1">{order.fall_percentage.toFixed(2)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default BacktestPanel




