"""
Order Manager
Manages order placement with ₹15,000 allocation per company
Supports paper trading (simulation) mode
"""
import math
import json
import os
from datetime import datetime
from logzero import logger
from config import config
from src.allocation_tracker import AllocationTracker
from src.nifty50_fetcher import Nifty50Fetcher


class OrderManager:
    """Manages order placement and allocation"""
    
    def __init__(self, angelone_client, allocation_tracker=None, nifty50_fetcher=None):
        """
        Initialize order manager
        
        Args:
            angelone_client: AngelOneClient instance
            allocation_tracker: AllocationTracker instance (optional)
            nifty50_fetcher: Nifty50Fetcher instance (optional)
        """
        self.client = angelone_client
        self.allocation_tracker = allocation_tracker or AllocationTracker()
        self.nifty50_fetcher = nifty50_fetcher or Nifty50Fetcher()
        self.allocation_per_company = config.ALLOCATION_PER_COMPANY
    
    def calculate_quantity(self, price, allocation_amount=None):
        """
        Calculate quantity of shares to buy based on allocation amount
        
        Args:
            price: Current price per share
            allocation_amount: Amount to allocate (defaults to config value)
        
        Returns:
            int: Quantity of shares (rounded down)
        """
        if allocation_amount is None:
            allocation_amount = self.allocation_per_company
        
        if price <= 0:
            logger.error(f"Invalid price: {price}")
            return 0
        
        quantity = math.floor(allocation_amount / price)
        return max(1, quantity)  # At least 1 share
    
    def place_order_for_stock(self, stock_data):
        """
        Place order for a single stock
        
        Args:
            stock_data: Dictionary containing stock information:
                - symbol: Trading symbol
                - token: Symbol token ID
                - exchange: Exchange (NSE, BSE)
                - current_price: Current market price
        
        Returns:
            dict: Order response or None if failed
        """
        symbol = stock_data.get('symbol')
        token = stock_data.get('token')
        exchange = stock_data.get('exchange', 'NSE')
        current_price = stock_data.get('current_price')
        
        if not all([symbol, token, current_price]):
            logger.error(f"Missing required stock data: {stock_data}")
            return None
        
        # Check if already allocated today
        if self.allocation_tracker.is_allocated_today(symbol):
            logger.info(f"{symbol} already allocated today, skipping")
            return None
        
        # Calculate quantity
        quantity = self.calculate_quantity(current_price, self.allocation_per_company)
        
        # Get full trading symbol (e.g., "SBIN-EQ")
        trading_symbol = self.nifty50_fetcher.get_trading_symbol(symbol)
        if not trading_symbol:
            trading_symbol = f"{symbol}-EQ"
        
        # Prepare order parameters
        order_params = {
            "variety": config.ORDER_VARIETY,
            "tradingsymbol": trading_symbol,
            "symboltoken": str(token),
            "transactiontype": "BUY",
            "exchange": exchange,
            "ordertype": config.ORDER_TYPE,
            "producttype": config.ORDER_PRODUCT_TYPE,
            "duration": config.ORDER_DURATION,
            "price": str(round(current_price, 2)),  # Round to 2 decimal places
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        
        logger.info(
            f"Placing order for {symbol}: "
            f"Price={current_price:.2f}, Quantity={quantity}, "
            f"Total={quantity * current_price:.2f}"
        )
        
        # Check if paper trading mode is enabled
        if config.PAPER_TRADING or config.SIMULATE_ORDERS:
            # Simulate order (paper trading)
            return self._simulate_order(symbol, token, exchange, current_price, quantity, order_params)
        else:
            # Place real order on AngelOne
            order_response = self.client.place_order(order_params)
            
            if order_response:
                # Extract order ID
                order_id = None
                if 'data' in order_response:
                    if 'orderid' in order_response['data']:
                        order_id = order_response['data']['orderid']
                    elif isinstance(order_response['data'], dict):
                        order_id = order_response['data'].get('orderid')
                
                # Mark as allocated
                self.allocation_tracker.mark_allocated(
                    symbol=symbol,
                    order_id=order_id,
                    amount=self.allocation_per_company
                )
                
                logger.info(f"Order placed successfully for {symbol}, Order ID: {order_id}")
                return {
                    'success': True,
                    'symbol': symbol,
                    'order_id': order_id,
                    'quantity': quantity,
                    'price': current_price,
                    'total_amount': quantity * current_price,
                    'response': order_response,
                    'simulated': False
                }
            else:
                logger.error(f"Failed to place order for {symbol}")
                return {
                    'success': False,
                    'symbol': symbol,
                    'error': 'Order placement failed'
                }
    
    def _simulate_order(self, symbol, token, exchange, price, quantity, order_params):
        """
        Simulate an order (paper trading mode)
        
        Args:
            symbol: Stock symbol
            token: Symbol token
            exchange: Exchange
            price: Order price
            quantity: Order quantity
            order_params: Order parameters (for logging)
        
        Returns:
            dict: Simulated order response
        """
        # Generate simulated order ID
        order_id = f"SIM_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        total_amount = quantity * price
        
        # Create simulated order response
        simulated_order = {
            'id': order_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'name': self.nifty50_fetcher.get_company_by_symbol(symbol).get('name', symbol) if self.nifty50_fetcher.get_company_by_symbol(symbol) else symbol,
            'quantity': quantity,
            'price': round(price, 2),
            'amount': round(total_amount, 2),
            'status': 'simulated',
            'apiResponse': 'ORDER_SUCCESS',
            'simulated': True,
            'exchange': exchange,
            'token': token
        }
        
        # Save to order history
        self._save_simulated_order(simulated_order)
        
        # Mark as allocated
        self.allocation_tracker.mark_allocated(
            symbol=symbol,
            order_id=order_id,
            amount=total_amount
        )
        
        logger.info(f"Simulated order placed for {symbol}: {quantity} shares @ ₹{price:.2f} = ₹{total_amount:.2f}")
        
        return {
            'success': True,
            'symbol': symbol,
            'order_id': order_id,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount,
            'response': {'status': True, 'message': 'Simulated order', 'data': {'orderid': order_id}},
            'simulated': True,
            'order_data': simulated_order
        }
    
    def _save_simulated_order(self, order_data):
        """
        Save simulated order to history file
        
        Args:
            order_data: Order data dictionary
        """
        try:
            order_file = config.ORDER_HISTORY_FILE
            os.makedirs(os.path.dirname(order_file), exist_ok=True)
            
            # Load existing orders
            orders = []
            if os.path.exists(order_file):
                with open(order_file, 'r') as f:
                    orders = json.load(f)
            
            # Add new order
            orders.append(order_data)
            
            # Keep only last 1000 orders
            if len(orders) > 1000:
                orders = orders[-1000:]
            
            # Save back
            with open(order_file, 'w') as f:
                json.dump(orders, f, indent=2, default=str)
                
        except Exception as e:
            logger.exception(f"Error saving simulated order: {e}")
    
    def place_orders_for_stocks(self, stocks_list, max_stocks=None):
        """
        Place orders for multiple stocks
        
        Args:
            stocks_list: List of stock data dictionaries
            max_stocks: Maximum number of stocks to process (default: config.MAX_COMPANIES)
        
        Returns:
            list: List of order results
        """
        if max_stocks is None:
            max_stocks = config.MAX_COMPANIES
        
        # Filter out already allocated stocks
        eligible_stocks = [
            stock for stock in stocks_list
            if not self.allocation_tracker.is_allocated_today(stock.get('symbol'))
        ]
        
        # Limit to max_stocks
        stocks_to_process = eligible_stocks[:max_stocks]
        
        logger.info(
            f"Placing orders for {len(stocks_to_process)} stocks "
            f"(out of {len(stocks_list)} eligible, "
            f"{len(eligible_stocks)} not yet allocated)"
        )
        
        order_results = []
        
        for stock in stocks_to_process:
            try:
                result = self.place_order_for_stock(stock)
                if result:
                    order_results.append(result)
            except Exception as e:
                logger.exception(f"Error placing order for {stock.get('symbol')}: {e}")
                order_results.append({
                    'success': False,
                    'symbol': stock.get('symbol'),
                    'error': str(e)
                })
        
        logger.info(f"Placed {len([r for r in order_results if r.get('success')])} orders successfully")
        
        return order_results
    
    def get_order_summary(self, order_results):
        """
        Get summary of order placement results
        
        Args:
            order_results: List of order results
        
        Returns:
            dict: Summary statistics
        """
        successful = [r for r in order_results if r.get('success')]
        failed = [r for r in order_results if not r.get('success')]
        
        total_amount = sum(
            r.get('total_amount', 0) for r in successful
        )
        
        return {
            'total_orders': len(order_results),
            'successful': len(successful),
            'failed': len(failed),
            'total_amount': total_amount,
            'successful_orders': successful,
            'failed_orders': failed
        }

