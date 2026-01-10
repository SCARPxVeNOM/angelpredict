/**
 * API Service Layer
 * Centralized service for all backend API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface Stock {
  id: string;
  symbol: string;
  name: string;
  previousClose: number;
  lastClose: number;
  dropPercent: number;
  rank: number;
  allocatedAmount: number;
  quantity: number;
  orderStatus: 'pending' | 'simulated' | 'executed' | 'failed';
}

export interface Order {
  id: string;
  timestamp: string;
  symbol: string;
  quantity: number;
  price: number;
  amount: number;
  status: 'simulated' | 'executed' | 'failed';
  apiResponse?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  severity: 'info' | 'success' | 'warning' | 'error';
}

export interface CapitalInfo {
  total: number;
  deployed: number;
  available: number;
  scanCount: number;
}

export interface AIContext {
  stocks?: Stock[];
  orders?: Order[];
  capital?: CapitalInfo;
  stock_context?: {
    symbol: string;
    name: string;
    current_price: number;
    ema: number;
    fall_percentage: number;
  };
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(error.error || 'Request failed');
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Fetch eligible stocks (manual scan)
   * This calls POST /api/stocks/scan which actually fetches from market
   */
  async fetchStocks(): Promise<Stock[]> {
    try {
      const response = await this.request<{ success: boolean; stocks: Stock[] }>(
        '/api/stocks/scan',
        {
          method: 'POST'
        }
      );
      return response.stocks || [];
    } catch (error) {
      console.error('Error fetching stocks:', error);
      return [];
    }
  }

  /**
   * Fetch order history (includes simulated orders and backtest orders)
   */
  async fetchOrders(): Promise<Order[]> {
    try {
      const response = await this.request<{
        success: boolean;
        today_orders: any[];
        simulated_orders?: any[];
        backtest_orders?: any[];
        history: any;
        paper_trading?: boolean;
      }>('/api/orders');

      // Transform backend orders to frontend format
      const orders: Order[] = [];
      
      // Add backtest orders first (they have complete data with dates)
      if (response.backtest_orders && response.backtest_orders.length > 0) {
        response.backtest_orders.forEach((order: any) => {
          orders.push({
            id: order.id || order.order_id || `backtest_${Date.now()}`,
            timestamp: order.timestamp || new Date().toISOString(),
            symbol: order.symbol || 'N/A',
            quantity: order.quantity || 0,
            price: order.price || 0,
            amount: order.amount || 0,
            status: 'simulated',  // Display as simulated in UI
            apiResponse: `BACKTEST: ${order.date || 'N/A'}`,
          });
        });
      }
      
      // Add simulated orders (excluding backtest orders already added)
      if (response.simulated_orders && response.simulated_orders.length > 0) {
        response.simulated_orders.forEach((order: any) => {
          // Skip if it's a backtest order (already added above)
          if (order.status === 'backtest' || (order.id && order.id.startsWith('backtest_'))) {
            return;
          }
          
          // Skip if already in orders
          const exists = orders.some(o => o.id === (order.id || order.order_id));
          if (!exists) {
            orders.push({
              id: order.id || order.order_id || `ord_${Date.now()}`,
              timestamp: order.timestamp || new Date().toISOString(),
              symbol: order.symbol || 'N/A',
              quantity: order.quantity || 0,
              price: order.price || 0,
              amount: order.amount || 0,
              status: 'simulated',
              apiResponse: order.apiResponse || 'ORDER_SUCCESS',
            });
          }
        });
      }
      
      // Add today's orders from allocation tracker (if not already in simulated orders)
      if (response.today_orders) {
        response.today_orders.forEach((order: any, index: number) => {
          // Skip if already in orders
          const exists = orders.some(o => o.id === (order.order_id || `ord_${index + 1}`));
          if (!exists) {
            // Try to calculate quantity from amount if price is available
            const price = order.price || 0;
            const amount = order.amount || 0;
            const quantity = price > 0 ? Math.floor(amount / price) : 0;
            
            orders.push({
              id: order.order_id || `ord_${index + 1}`,
              timestamp: order.timestamp || new Date().toISOString(),
              symbol: order.symbol || 'N/A',
              quantity: quantity,
              price: price,
              amount: amount,
              status: 'simulated',
              apiResponse: 'ORDER_SUCCESS',
            });
          }
        });
      }

      // Sort by timestamp (newest first)
      orders.sort((a, b) => {
        const timeA = new Date(a.timestamp).getTime();
        const timeB = new Date(b.timestamp).getTime();
        return timeB - timeA;
      });

      return orders;
    } catch (error) {
      console.error('Error fetching orders:', error);
      return [];
    }
  }

  /**
   * Fetch system logs
   */
  async fetchLogs(): Promise<LogEntry[]> {
    try {
      const response = await this.request<{
        success: boolean;
        logs: LogEntry[];
      }>('/api/logs');
      return response.logs || [];
    } catch (error) {
      console.error('Error fetching logs:', error);
      return [];
    }
  }

  /**
   * Fetch capital overview
   */
  async fetchCapital(): Promise<CapitalInfo> {
    try {
      const response = await this.request<{
        success: boolean;
        capital: CapitalInfo;
      }>('/api/capital');
      return response.capital || {
        total: 300000,
        deployed: 0,
        available: 300000,
        scanCount: 0,
      };
    } catch (error) {
      console.error('Error fetching capital:', error);
      return {
        total: 300000,
        deployed: 0,
        available: 300000,
        scanCount: 0,
      };
    }
  }

  /**
   * Send AI chat message
   */
  async sendAIMessage(
    prompt: string,
    context?: AIContext
  ): Promise<string> {
    try {
      const response = await this.request<{
        success: boolean;
        response: string;
      }>('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          prompt,
          context: context || {},
        }),
      });
      return response.response || 'No response received';
    } catch (error) {
      console.error('Error sending AI message:', error);
      return 'I encountered an error. Please try again.';
    }
  }

  /**
   * Get system status
   */
  async getStatus(): Promise<any> {
    try {
      const response = await this.request<{
        success: boolean;
        authenticated: boolean;
        scheduler_status: any;
        last_execution: string | null;
      }>('/api/status');
      return response;
    } catch (error) {
      console.error('Error fetching status:', error);
      return {
        success: false,
        authenticated: false,
        scheduler_status: null,
        last_execution: null,
      };
    }
  }

  /**
   * Trigger algorithm manually
   */
  async triggerAlgorithm(): Promise<boolean> {
    try {
      const response = await this.request<{
        success: boolean;
        message: string;
      }>('/api/run-now', {
        method: 'POST',
      });
      return response.success;
    } catch (error) {
      console.error('Error triggering algorithm:', error);
      return false;
    }
  }

  /**
   * Run backtest simulation
   */
  async runBacktest(days: number = 7, startDate?: string): Promise<any> {
    try {
      const response = await this.request<{
        success: boolean;
        results: any;
        saved_to?: string;
        error?: string;
      }>('/api/backtest', {
        method: 'POST',
        body: JSON.stringify({
          days,
          start_date: startDate,
        }),
      });
      
      if (!response.success) {
        throw new Error(response.error || 'Backtest failed');
      }
      
      return response.results || response;
    } catch (error: any) {
      console.error('Error running backtest:', error);
      const errorMessage = error?.message || error?.error || 'Failed to run backtest. Please check backend logs.';
      throw new Error(errorMessage);
    }
  }

  /**
   * Get latest backtest results
   */
  async getBacktestResults(): Promise<any> {
    try {
      const response = await this.request<{
        success: boolean;
        results: any;
        file?: string;
        error?: string;
      }>('/api/backtest/results');
      
      if (!response.success) {
        throw new Error(response.error || 'No backtest results found');
      }
      
      return response.results || response;
    } catch (error: any) {
      console.error('Error getting backtest results:', error);
      const errorMessage = error?.message || error?.error || 'No previous backtest results found. Run a backtest first.';
      throw new Error(errorMessage);
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
