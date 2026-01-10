import { LayoutDashboard, ScanSearch, ShoppingCart, FileText, Settings, BarChart3, TrendingUp, TestTube } from 'lucide-react'
import { motion } from 'framer-motion'

interface SidebarProps {
  activeView: string
  setActiveView: (view: 'dashboard' | 'orders' | 'logs' | 'nifty50' | 'backtest') => void
}

const Sidebar = ({ activeView, setActiveView }: SidebarProps) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'nifty50', label: 'Nifty 50', icon: TrendingUp },
    { id: 'scanner', label: 'Scanner', icon: ScanSearch, disabled: true },
    { id: 'orders', label: 'Orders', icon: ShoppingCart },
    { id: 'backtest', label: 'Backtest', icon: TestTube },
    { id: 'positions', label: 'Positions', icon: BarChart3, disabled: true },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings, disabled: true },
  ]

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 bg-dark-surface/95 backdrop-blur-xl border-r border-dark-border">
      <nav className="p-4 space-y-1">
        {menuItems.map((item, index) => {
          const Icon = item.icon
          const isActive = activeView === item.id
          
          return (
            <motion.button
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => !item.disabled && setActiveView(item.id as any)}
              disabled={item.disabled}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all relative overflow-hidden
                ${isActive 
                  ? 'bg-accent-primary/10 text-accent-primary border border-accent-primary/30 shadow-lg shadow-accent-primary/10' 
                  : item.disabled
                    ? 'text-gray-600 cursor-not-allowed'
                    : 'text-gray-400 hover:bg-dark-elevated hover:text-gray-200 border border-transparent'
                }
              `}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-accent-primary/5"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              <Icon className="w-5 h-5 relative z-10" />
              <span className="font-medium text-sm relative z-10">{item.label}</span>
              {item.disabled && (
                <span className="ml-auto text-xs text-gray-600 relative z-10">Soon</span>
              )}
            </motion.button>
          )
        })}
      </nav>
    </aside>
  )
}

export default Sidebar
