import { useRef } from 'react'
import CapitalOverview from './CapitalOverview'
import StrategyPanel from './StrategyPanel'
import StockTable from './StockTable'

const Dashboard = () => {
  const capitalOverviewRef = useRef<any>(null)

  return (
    <div className="space-y-6 animate-fade-in">
      <CapitalOverview ref={capitalOverviewRef} />
      <StrategyPanel />
      <StockTable capitalOverviewRef={capitalOverviewRef} />
    </div>
  )
}

export default Dashboard
