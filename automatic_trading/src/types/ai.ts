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
