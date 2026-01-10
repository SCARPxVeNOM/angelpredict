import { useState } from 'react'
import TopNavBar from './components/TopNavBar'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import OrdersPanel from './components/OrdersPanel'
import LogsPanel from './components/LogsPanel'
import Nifty50Table from './components/Nifty50Table'
import BacktestPanel from './components/BacktestPanel'
import AIFloatingButton from './components/ai/AIFloatingButton'
import AIDrawer from './components/ai/AIDrawer'
import { AIProvider } from './contexts/AIContext'

function App() {
  const [activeView, setActiveView] = useState<'dashboard' | 'orders' | 'logs' | 'nifty50' | 'backtest'>('dashboard')

  return (
    <AIProvider>
      <div className="min-h-screen bg-dark-bg text-gray-100">
        <TopNavBar />
        
        <div className="flex">
          <Sidebar activeView={activeView} setActiveView={setActiveView} />
          
          <main className="flex-1 ml-64 mt-16 p-6">
            {activeView === 'dashboard' && <Dashboard />}
            {activeView === 'nifty50' && <Nifty50Table />}
            {activeView === 'orders' && <OrdersPanel />}
            {activeView === 'logs' && <LogsPanel />}
            {activeView === 'backtest' && <BacktestPanel />}
          </main>
        </div>

        {/* AI Components */}
        <AIFloatingButton hasNewScan={true} />
        <AIDrawer />
      </div>
    </AIProvider>
  )
}

export default App
