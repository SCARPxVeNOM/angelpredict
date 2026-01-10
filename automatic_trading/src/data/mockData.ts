import type { Stock, Order, LogEntry } from '../types'

export const mockStocks: Stock[] = [
  {
    id: '1',
    symbol: 'TATASTEEL',
    name: 'Tata Steel Limited',
    previousClose: 142.50,
    lastClose: 134.85,
    dropPercent: -5.37,
    rank: 1,
    allocatedAmount: 15000,
    quantity: 111,
    orderStatus: 'simulated'
  },
  {
    id: '2',
    symbol: 'HINDALCO',
    name: 'Hindalco Industries Ltd',
    previousClose: 628.30,
    lastClose: 597.45,
    dropPercent: -4.91,
    rank: 2,
    allocatedAmount: 15000,
    quantity: 25,
    orderStatus: 'simulated'
  },
  {
    id: '3',
    symbol: 'JSWSTEEL',
    name: 'JSW Steel Limited',
    previousClose: 895.60,
    lastClose: 852.10,
    dropPercent: -4.86,
    rank: 3,
    allocatedAmount: 15000,
    quantity: 17,
    orderStatus: 'simulated'
  },
  {
    id: '4',
    symbol: 'VEDL',
    name: 'Vedanta Limited',
    previousClose: 445.80,
    lastClose: 424.95,
    dropPercent: -4.68,
    rank: 4,
    allocatedAmount: 15000,
    quantity: 35,
    orderStatus: 'simulated'
  },
  {
    id: '5',
    symbol: 'COALINDIA',
    name: 'Coal India Limited',
    previousClose: 412.25,
    lastClose: 393.50,
    dropPercent: -4.55,
    rank: 5,
    allocatedAmount: 15000,
    quantity: 38,
    orderStatus: 'pending'
  }
]

export const mockOrders: Order[] = [
  {
    id: 'ord_001',
    timestamp: '2025-01-10 15:45:23',
    symbol: 'TATASTEEL',
    quantity: 111,
    price: 134.85,
    amount: 14968.35,
    status: 'simulated',
    apiResponse: 'ORDER_SUCCESS'
  },
  {
    id: 'ord_002',
    timestamp: '2025-01-10 15:45:25',
    symbol: 'HINDALCO',
    quantity: 25,
    price: 597.45,
    amount: 14936.25,
    status: 'simulated',
    apiResponse: 'ORDER_SUCCESS'
  },
  {
    id: 'ord_003',
    timestamp: '2025-01-10 15:45:27',
    symbol: 'JSWSTEEL',
    quantity: 17,
    price: 852.10,
    amount: 14485.70,
    status: 'simulated',
    apiResponse: 'ORDER_SUCCESS'
  },
  {
    id: 'ord_004',
    timestamp: '2025-01-10 15:45:29',
    symbol: 'VEDL',
    quantity: 35,
    price: 424.95,
    amount: 14873.25,
    status: 'simulated',
    apiResponse: 'ORDER_SUCCESS'
  },
  {
    id: 'ord_005',
    timestamp: '2025-01-10 15:45:31',
    symbol: 'COALINDIA',
    quantity: 38,
    price: 393.50,
    amount: 14953.00,
    status: 'simulated',
    apiResponse: 'ORDER_SUCCESS'
  }
]

export const mockLogs: LogEntry[] = [
  {
    id: 'log_001',
    timestamp: '15:45:15',
    message: 'Market scan initiated for NSE stocks',
    severity: 'info'
  },
  {
    id: 'log_002',
    timestamp: '15:45:17',
    message: 'Connected to Angel One SmartAPI successfully',
    severity: 'success'
  },
  {
    id: 'log_003',
    timestamp: '15:45:18',
    message: 'Fetching previous close and last close data...',
    severity: 'info'
  },
  {
    id: 'log_004',
    timestamp: '15:45:19',
    message: 'Retrieved 2,847 stock records from NSE',
    severity: 'success'
  },
  {
    id: 'log_005',
    timestamp: '15:45:20',
    message: 'Applying filter: Drop ≤ -5%',
    severity: 'info'
  },
  {
    id: 'log_006',
    timestamp: '15:45:21',
    message: 'Found 47 stocks matching criteria',
    severity: 'success'
  },
  {
    id: 'log_007',
    timestamp: '15:45:21',
    message: 'Sorting by ascending drop percentage',
    severity: 'info'
  },
  {
    id: 'log_008',
    timestamp: '15:45:22',
    message: 'Selected top 5 stocks for trading',
    severity: 'success'
  },
  {
    id: 'log_009',
    timestamp: '15:45:22',
    message: 'Calculating order quantities (₹15,000 per stock)',
    severity: 'info'
  },
  {
    id: 'log_010',
    timestamp: '15:45:23',
    message: 'Placing simulated order: TATASTEEL x111 @ ₹134.85',
    severity: 'info'
  },
  {
    id: 'log_011',
    timestamp: '15:45:23',
    message: 'Order confirmed: TATASTEEL (ORDER_SUCCESS)',
    severity: 'success'
  },
  {
    id: 'log_012',
    timestamp: '15:45:25',
    message: 'Placing simulated order: HINDALCO x25 @ ₹597.45',
    severity: 'info'
  },
  {
    id: 'log_013',
    timestamp: '15:45:25',
    message: 'Order confirmed: HINDALCO (ORDER_SUCCESS)',
    severity: 'success'
  },
  {
    id: 'log_014',
    timestamp: '15:45:27',
    message: 'Placing simulated order: JSWSTEEL x17 @ ₹852.10',
    severity: 'info'
  },
  {
    id: 'log_015',
    timestamp: '15:45:27',
    message: 'Order confirmed: JSWSTEEL (ORDER_SUCCESS)',
    severity: 'success'
  },
  {
    id: 'log_016',
    timestamp: '15:45:29',
    message: 'Placing simulated order: VEDL x35 @ ₹424.95',
    severity: 'info'
  },
  {
    id: 'log_017',
    timestamp: '15:45:29',
    message: 'Order confirmed: VEDL (ORDER_SUCCESS)',
    severity: 'success'
  },
  {
    id: 'log_018',
    timestamp: '15:45:31',
    message: 'Placing simulated order: COALINDIA x38 @ ₹393.50',
    severity: 'info'
  },
  {
    id: 'log_019',
    timestamp: '15:45:31',
    message: 'Order confirmed: COALINDIA (ORDER_SUCCESS)',
    severity: 'success'
  },
  {
    id: 'log_020',
    timestamp: '15:45:32',
    message: 'Total capital deployed: ₹74,216.55',
    severity: 'success'
  },
  {
    id: 'log_021',
    timestamp: '15:45:32',
    message: 'Available balance: ₹2,25,783.45',
    severity: 'info'
  },
  {
    id: 'log_022',
    timestamp: '15:45:33',
    message: 'Scan completed successfully. All orders placed.',
    severity: 'success'
  }
]
