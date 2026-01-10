import type { Stock, Order, CapitalInfo } from './index'

export interface AIMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  context?: {
    stockSymbol?: string
    type?: 'stock' | 'allocation' | 'summary' | 'general'
    dropPercent?: number
    rank?: number
    quantity?: number
    price?: number
    stocks?: Stock[]
    orders?: Order[]
    capital?: CapitalInfo
    stock_context?: {
      symbol: string
      name?: string
      current_price?: number
      ema?: number
      fall_percentage?: number
    }
  }
}

export interface AIContextType {
  isOpen: boolean
  messages: AIMessage[]
  isLoading: boolean
  openDrawer: (initialPrompt?: string, context?: AIMessage['context']) => void
  closeDrawer: () => void
  sendMessage: (message: string, context?: AIMessage['context']) => void
  clearChat: () => void
}
