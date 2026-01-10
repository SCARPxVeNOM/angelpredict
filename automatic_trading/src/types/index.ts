export interface Stock {
  id: string
  symbol: string
  name: string
  previousClose: number
  lastClose: number
  dropPercent: number
  rank: number
  allocatedAmount: number
  quantity: number
  orderStatus: 'pending' | 'simulated' | 'executed' | 'failed'
}

export interface Order {
  id: string
  timestamp: string
  symbol: string
  quantity: number
  price: number
  amount: number
  status: 'simulated' | 'executed' | 'failed'
  apiResponse?: string
}

export interface LogEntry {
  id: string
  timestamp: string
  message: string
  severity: 'info' | 'success' | 'warning' | 'error'
}

export interface CapitalInfo {
  total: number
  deployed: number
  available: number
  scanCount: number
}
