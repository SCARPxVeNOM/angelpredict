import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import type { AIContextType, AIMessage } from '../types/ai'
import { apiService, AIContext as ApiAIContext } from '../services/api'

const AIContext = createContext<AIContextType | undefined>(undefined)

export const AIProvider = ({ children }: { children: ReactNode }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const openDrawer = useCallback((initialPrompt?: string, context?: AIMessage['context']) => {
    setIsOpen(true)
    if (initialPrompt) {
      sendMessage(initialPrompt, context)
    }
  }, [])

  const closeDrawer = useCallback(() => {
    setIsOpen(false)
  }, [])

  const sendMessage = useCallback(async (content: string, context?: AIMessage['context']) => {
    // Add user message
    const userMessage: AIMessage = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
      context
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Prepare context for API
      const apiContext: ApiAIContext = {}
      
      if (context) {
        if (context.stocks) {
          apiContext.stocks = context.stocks.map(s => ({
            symbol: s.symbol,
            name: s.name,
            current_price: s.lastClose,
            ema: s.previousClose, // Approximation
            fall_percentage: s.dropPercent
          } as any)) // Type assertion for API compatibility
        }
        if (context.orders) {
          apiContext.orders = context.orders.map(o => ({
            symbol: o.symbol,
            quantity: o.quantity,
            price: o.price,
            amount: o.amount
          } as any)) // Type assertion for API compatibility
        }
        if (context.capital) {
          apiContext.capital = {
            total: context.capital.total,
            deployed: context.capital.deployed,
            available: context.capital.available,
            scanCount: context.capital.scanCount || 0
          }
        }
        if (context.stock_context) {
          apiContext.stock_context = {
            symbol: context.stock_context.symbol,
            name: context.stock_context.name || '',
            current_price: context.stock_context.current_price || 0,
            ema: context.stock_context.ema || 0,
            fall_percentage: context.stock_context.fall_percentage || 0
          }
        }
      }

      // Call Gemini API through Flask backend
      const aiResponse = await apiService.sendAIMessage(content, apiContext)
      
      const aiMessage: AIMessage = {
        id: `msg_${Date.now()}_ai`,
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending AI message:', error)
      const errorMessage: AIMessage = {
        id: `msg_${Date.now()}_ai`,
        role: 'assistant',
        content: 'I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearChat = useCallback(() => {
    setMessages([])
  }, [])

  return (
    <AIContext.Provider value={{
      isOpen,
      messages,
      isLoading,
      openDrawer,
      closeDrawer,
      sendMessage,
      clearChat
    }}>
      {children}
    </AIContext.Provider>
  )
}

export const useAI = () => {
  const context = useContext(AIContext)
  if (!context) {
    throw new Error('useAI must be used within AIProvider')
  }
  return context
}
