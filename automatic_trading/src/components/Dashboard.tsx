import CapitalOverview from './CapitalOverview'
import StrategyPanel from './StrategyPanel'
import StockTable from './StockTable'

const Dashboard = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <CapitalOverview />
      <StrategyPanel />
      <StockTable />
    </div>
  )
}

export default Dashboard
