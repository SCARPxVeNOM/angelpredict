import { TrendingUp, Circle, User } from 'lucide-react'
import { formatCurrency } from '../utils/formatters'

const TopNavBar = () => {
  const lastScanTime = '15:45:33'
  const currentDate = new Date().toLocaleDateString('en-IN', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric' 
  })

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-dark-surface/95 backdrop-blur-xl border-b border-dark-border z-50">
      <div className="h-full px-6 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-lg flex items-center justify-center shadow-lg shadow-accent-primary/20">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-gray-100">NSE Simulator</h1>
            <p className="text-xs text-gray-500 font-medium">Angel One SmartAPI</p>
          </div>
        </div>

        {/* Center Info */}
        <div className="flex items-center gap-6">
          {/* Market Status */}
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-elevated/80 border border-dark-border">
            <Circle className="w-2 h-2 fill-red-500 text-red-500 animate-pulse-subtle" />
            <span className="text-sm font-medium text-gray-300">Market Closed</span>
          </div>

          {/* Date & Time */}
          <div className="text-right">
            <p className="text-xs text-gray-500 font-medium">Last Scan</p>
            <p className="text-sm font-mono font-semibold text-gray-300">{currentDate} • {lastScanTime}</p>
          </div>

          {/* Capital Summary */}
          <div className="flex items-center gap-4 px-4 py-2 rounded-lg bg-dark-elevated/80 border border-dark-border">
            <div>
              <p className="text-xs text-gray-500 font-medium">Total Capital</p>
              <p className="text-sm font-mono font-bold text-accent-primary">{formatCurrency(300000)}</p>
            </div>
            <div className="w-px h-8 bg-dark-border" />
            <div>
              <p className="text-xs text-gray-500 font-medium">Available</p>
              <p className="text-sm font-mono font-bold text-accent-success">{formatCurrency(225783.45)}</p>
            </div>
          </div>

          {/* Mode Badge */}
          <div className="px-3 py-1.5 rounded-md bg-accent-warning/10 border border-accent-warning/30">
            <span className="text-xs font-bold text-accent-warning uppercase tracking-wider">Paper Trading</span>
          </div>
        </div>

        {/* Profile */}
        <button className="w-9 h-9 rounded-lg bg-dark-elevated border border-dark-border hover:border-accent-primary hover:bg-dark-hover transition-all flex items-center justify-center group">
          <User className="w-5 h-5 text-gray-400 group-hover:text-accent-primary transition-colors" />
        </button>
      </div>
    </nav>
  )
}

export default TopNavBar
