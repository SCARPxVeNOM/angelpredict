import { useState } from 'react'
import { TrendingUp, TrendingDown, Search, ArrowUpDown, Filter, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'
import { nifty50Stocks, type Nifty50Stock } from '../data/nifty50Data'
import { formatCurrency } from '../utils/formatters'
import apiService from '../services/api'

const Nifty50Table = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [sectorFilter, setSectorFilter] = useState<string>('all')
  const [sortConfig, setSortConfig] = useState<{ key: keyof Nifty50Stock; direction: 'asc' | 'desc' }>({
    key: 'symbol',
    direction: 'asc'
  })
  const [stocks, setStocks] = useState<Nifty50Stock[]>(nifty50Stocks)
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  // Fetch real-time data from AngelOne API
  const fetchRealTimeData = async () => {
    setLoading(true)
    try {
      const realTimeData = await apiService.fetchNifty50RealTime()
      
      if (realTimeData && realTimeData.length > 0) {
        // Map the API data to our stock format
        const updatedStocks = realTimeData.map((stock: any) => ({
          id: stock.id || stock.symbol,
          symbol: stock.symbol,
          name: stock.name,
          sector: stock.sector || 'N/A',
          price: stock.price || 0,
          change: stock.change || 0,
          changePercent: stock.changePercent || 0,
          dayHigh: stock.dayHigh || stock.price || 0,
          dayLow: stock.dayLow || stock.price || 0,
          open: stock.open || stock.price || 0,
          previousClose: stock.previousClose || stock.price || 0,
          volume: stock.volume || 0,
          marketCap: stock.marketCap || 0,
          pe: stock.pe || 0,
        }))
        
        setStocks(updatedStocks)
        setLastUpdated(new Date().toLocaleTimeString())
      }
    } catch (error) {
      console.error('Error fetching real-time data:', error)
      alert('Failed to fetch real-time data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Get unique sectors
  const sectors = ['all', ...Array.from(new Set(stocks.map(stock => stock.sector)))]

  // Filter and sort stocks
  const filteredStocks = stocks
    .filter(stock => {
      const matchesSearch = stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           stock.name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesSector = sectorFilter === 'all' || stock.sector === sectorFilter
      return matchesSearch && matchesSector
    })
    .sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortConfig.direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }
      
      return 0
    })

  const handleSort = (key: keyof Nifty50Stock) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const formatMarketCap = (value: number) => {
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L Cr`
    return `₹${(value / 1000).toFixed(2)}K Cr`
  }

  const formatVolume = (value: number) => {
    if (value >= 10000000) return `${(value / 10000000).toFixed(2)}Cr`
    if (value >= 100000) return `${(value / 100000).toFixed(2)}L`
    return `${(value / 1000).toFixed(2)}K`
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Nifty 50 Companies</h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time market data for India's top 50 companies
            {lastUpdated && <span className="ml-2 text-accent-primary">• Updated: {lastUpdated}</span>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchRealTimeData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-primary hover:bg-accent-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Fetching...' : 'Fetch Data'}
          </button>
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-elevated border border-dark-border">
            <TrendingUp className="w-4 h-4 text-accent-success" />
            <span className="text-sm text-gray-400">Nifty 50: </span>
            <span className="text-sm font-bold text-accent-success font-mono">21,456.75</span>
            <span className="text-xs text-accent-success font-mono">+0.85%</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="glass rounded-2xl p-4 border border-dark-border">
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by symbol or company name..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-dark-surface border border-dark-border text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-primary/50 transition-colors"
            />
          </div>

          {/* Sector Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="pl-10 pr-8 py-2.5 rounded-lg bg-dark-surface border border-dark-border text-sm text-gray-200 focus:outline-none focus:border-accent-primary/50 transition-colors appearance-none cursor-pointer"
            >
              {sectors.map(sector => (
                <option key={sector} value={sector}>
                  {sector === 'all' ? 'All Sectors' : sector}
                </option>
              ))}
            </select>
          </div>

          {/* Results count */}
          <div className="px-4 py-2.5 rounded-lg bg-dark-elevated border border-dark-border">
            <span className="text-sm font-semibold text-gray-300 font-mono">
              {filteredStocks.length} / {stocks.length}
            </span>
          </div>
        </div>
      </div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl border border-dark-border overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-elevated/50 sticky top-0 backdrop-blur-sm">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">
                  <button 
                    onClick={() => handleSort('symbol')}
                    className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                  >
                    Symbol <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">Company</th>
                <th className="px-6 py-4 font-semibold">Sector</th>
                <th className="px-6 py-4 font-semibold">
                  <button 
                    onClick={() => handleSort('price')}
                    className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                  >
                    Price <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">
                  <button 
                    onClick={() => handleSort('changePercent')}
                    className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                  >
                    Change % <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">
                  <button 
                    onClick={() => handleSort('marketCap')}
                    className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                  >
                    Market Cap <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-6 py-4 font-semibold">Volume</th>
                <th className="px-6 py-4 font-semibold">P/E</th>
                <th className="px-6 py-4 font-semibold">Day Range</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {filteredStocks.map((stock, index) => (
                <motion.tr
                  key={stock.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: Math.min(index * 0.02, 0.5) }}
                  className="hover:bg-dark-elevated/50 transition-all group"
                >
                  <td className="px-6 py-4">
                    <span className="font-bold text-accent-primary font-mono text-sm">
                      {stock.symbol}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-300 font-medium">{stock.name}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 rounded-md text-xs font-semibold bg-dark-elevated border border-dark-border text-gray-400">
                      {stock.sector}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm font-bold text-gray-200">
                      {formatCurrency(stock.price)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {stock.changePercent >= 0 ? (
                        <TrendingUp className="w-4 h-4 text-accent-success" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-accent-danger" />
                      )}
                      <div className="flex flex-col">
                        <span className={`font-mono text-sm font-bold ${
                          stock.changePercent >= 0 ? 'text-accent-success' : 'text-accent-danger'
                        }`}>
                          {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                        </span>
                        <span className={`font-mono text-xs ${
                          stock.change >= 0 ? 'text-accent-success' : 'text-accent-danger'
                        }`}>
                          {stock.change >= 0 ? '+' : ''}{formatCurrency(stock.change)}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-300 font-medium">
                      {formatMarketCap(stock.marketCap)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-400">
                      {formatVolume(stock.volume)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-gray-300 font-medium">
                      {stock.pe.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">H:</span>
                        <span className="font-mono text-xs text-gray-300">{formatCurrency(stock.dayHigh)}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">L:</span>
                        <span className="font-mono text-xs text-gray-300">{formatCurrency(stock.dayLow)}</span>
                      </div>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredStocks.length === 0 && (
          <div className="p-12 text-center">
            <p className="text-gray-500 font-medium">No stocks found matching your criteria</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default Nifty50Table
