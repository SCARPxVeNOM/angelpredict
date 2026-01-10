import { Settings2, Database, Clock, TrendingDown, Target, DollarSign } from 'lucide-react'

const StrategyPanel = () => {
  const rules = [
    { icon: Database, label: 'Data Source', value: 'Angel One SmartAPI' },
    { icon: Clock, label: 'Scan Time', value: 'After Market Close' },
    { icon: TrendingDown, label: 'Drop Filter', value: '≤ −5%' },
    { icon: Target, label: 'Sort Logic', value: 'Ascending Drop' },
    { icon: Settings2, label: 'Picks', value: 'Top 5 Stocks' },
    { icon: DollarSign, label: 'Order Size', value: '₹15,000 per stock' }
  ]

  return (
    <div className="glass rounded-2xl p-6 border border-dark-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
          <Settings2 className="w-5 h-5 text-accent-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold">Strategy Logic</h2>
          <p className="text-xs text-gray-500">Automated scanning rules (Read-only)</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {rules.map((rule) => {
          const Icon = rule.icon
          return (
            <div key={rule.label} className="flex items-start gap-3 p-4 rounded-xl bg-dark-elevated border border-dark-border">
              <div className="w-8 h-8 rounded-lg bg-dark-surface flex items-center justify-center flex-shrink-0">
                <Icon className="w-4 h-4 text-accent-primary" />
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">{rule.label}</p>
                <p className="text-sm font-semibold text-gray-200">{rule.value}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default StrategyPanel
