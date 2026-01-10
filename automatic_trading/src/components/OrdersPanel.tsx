import { useState } from 'react'
import { Clock, CheckCircle, XCircle, Sparkles } from 'lucide-react'
import { formatCurrency } from '../utils/formatters'
import { useAI } from '../contexts/AIContext'
import { Order } from '../services/api'

const OrdersPanel = () => {
  const { openDrawer } = useAI()
  const [orders] = useState<Order[]>([])
  const [loading] = useState(true)

  // Don't auto-fetch orders - only load from backtest or manual trigger
  // Remove automatic fetching to prevent unnecessary API calls

  const handleSummarize = () => {
    openDrawer('Summarize today\'s trades', { orders })
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'simulated':
      case 'executed':
        return <CheckCircle className="w-5 h-5 text-accent-success" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-accent-danger" />
      default:
        return <Clock className="w-5 h-5 text-accent-warning" />
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Order History</h1>
          <p className="text-sm text-gray-500 mt-1">All simulated orders from today's scan</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSummarize}
            className="px-4 py-2 rounded-lg bg-accent-primary/10 border border-accent-primary/30 hover:bg-accent-primary/20 transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-accent-primary" />
            <span className="text-sm font-semibold text-accent-primary">Summarize trades</span>
          </button>
          <div className="px-4 py-2 rounded-lg bg-dark-elevated border border-dark-border">
            <span className="text-sm text-gray-400">Total Orders: </span>
            <span className="text-sm font-semibold text-gray-200">{orders.length}</span>
          </div>
        </div>
      </div>

      <div className="glass rounded-2xl border border-dark-border p-6">
        <div className="space-y-4">
          {loading ? (
            <div className="text-center text-gray-500 py-8">Loading orders...</div>
          ) : orders.length === 0 ? (
            <div className="text-center text-gray-500 py-8">No orders found</div>
          ) : (
            orders.map((order, index) => (
            <div
              key={order.id}
              className="flex items-start gap-4 p-4 rounded-xl bg-dark-elevated border border-dark-border hover:border-accent-primary/30 transition-all"
            >
              {/* Timeline dot */}
              <div className="relative">
                <div className="w-10 h-10 rounded-lg bg-dark-surface border border-dark-border flex items-center justify-center">
                  {getStatusIcon(order.status)}
                </div>
                {index < orders.length - 1 && (
                  <div className="absolute top-10 left-1/2 -translate-x-1/2 w-px h-8 bg-dark-border" />
                )}
              </div>

              {/* Order details */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-200">{order.symbol}</h3>
                    <p className="text-xs text-gray-500 font-mono">{order.timestamp}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-md text-xs font-semibold border ${
                    order.status === 'simulated' 
                      ? 'bg-accent-success/10 text-accent-success border-accent-success/30'
                      : 'bg-accent-warning/10 text-accent-warning border-accent-warning/30'
                  }`}>
                    {order.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-4 mt-3">
                  <div>
                    <p className="text-xs text-gray-500">Quantity</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">{order.quantity}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Price</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">{formatCurrency(order.price)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Amount</p>
                    <p className="font-mono text-sm font-semibold text-gray-200">{formatCurrency(order.amount)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">API Response</p>
                    <p className="text-xs font-mono text-accent-success">{order.apiResponse || 'Success'}</p>
                  </div>
                </div>
              </div>
            </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default OrdersPanel
