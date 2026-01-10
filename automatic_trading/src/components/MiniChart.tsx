import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts'
import type { Stock } from '../types'

interface MiniChartProps {
  stock: Stock
}

const MiniChart = ({ stock }: MiniChartProps) => {
  // Generate mock intraday data showing the drop
  const generateChartData = () => {
    const data = []
    const startPrice = stock.previousClose
    const endPrice = stock.lastClose
    const points = 20
    
    for (let i = 0; i <= points; i++) {
      const progress = i / points
      // Add some volatility
      const volatility = (Math.random() - 0.5) * (startPrice * 0.01)
      const price = startPrice + (endPrice - startPrice) * progress + volatility
      data.push({ time: i, price })
    }
    
    return data
  }

  const data = generateChartData()

  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={data}>
        <YAxis domain={['dataMin', 'dataMax']} hide />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#ef4444"
          strokeWidth={2}
          dot={false}
          animationDuration={1000}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default MiniChart
