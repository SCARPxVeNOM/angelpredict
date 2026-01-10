"""
Flask REST API
Provides endpoints for frontend to display eligible companies, allocations, and order history
"""
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from logzero import logger
from config import config
from src.stock_analyzer import StockAnalyzer
from src.allocation_tracker import AllocationTracker
from src.nifty50_fetcher import Nifty50Fetcher
from src.gemini_client import GeminiClient
from src.backtester import Backtester
import json
import os
import pytz
from datetime import datetime


class TradingAPI:
    """Flask API for trading bot frontend"""
    
    def __init__(self, angelone_client, scheduler=None):
        """
        Initialize Flask API
        
        Args:
            angelone_client: AngelOneClient instance
            scheduler: TradingScheduler instance (optional)
        """
        self.app = Flask(__name__)
        # Configure CORS with frontend URL
        # Allow frontend URL and localhost for development
        allowed_origins = [
            config.FRONTEND_URL,
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev port
        ]
        # Filter out None values if FRONTEND_URL is not set
        allowed_origins = [origin for origin in allowed_origins if origin]
        CORS(self.app, origins=allowed_origins, supports_credentials=True)
        
        self.client = angelone_client
        self.scheduler = scheduler
        self.allocation_tracker = AllocationTracker()
        self.nifty50_fetcher = Nifty50Fetcher()
        self.stock_analyzer = StockAnalyzer(
            angelone_client=self.client,
            nifty50_fetcher=self.nifty50_fetcher
        )
        self.gemini_client = GeminiClient()
        self.backtester = Backtester(self.client)
        
        # Register routes
        self._register_routes()
        self._register_static_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'Trading Bot API'
            })
        
        @self.app.route('/api/eligible-companies', methods=['GET'])
        def get_eligible_companies():
            """
            Get list of companies currently eligible (5% below EMA)
            
            Returns:
                JSON: List of eligible companies sorted by fall percentage
            """
            try:
                eligible_stocks = self.stock_analyzer.analyze_all_stocks()
                
                # Format response
                companies = []
                for stock in eligible_stocks:
                    companies.append({
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'current_price': round(stock['current_price'], 2),
                        'ema': round(stock['ema'], 2),
                        'fall_percentage': round(stock['fall_percentage'], 2),
                        'token': stock['token'],
                        'exchange': stock['exchange']
                    })
                
                return jsonify({
                    'success': True,
                    'count': len(companies),
                    'companies': companies
                })
                
            except Exception as e:
                logger.exception(f"Error getting eligible companies: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/allocated-today', methods=['GET'])
        def get_allocated_today():
            """
            Get companies allocated today
            
            Returns:
                JSON: List of companies allocated today with order details
            """
            try:
                allocated_symbols = self.allocation_tracker.get_allocated_today()
                orders = self.allocation_tracker.get_today_orders()
                
                # Get company details
                allocated_companies = []
                for symbol in allocated_symbols:
                    company = self.nifty50_fetcher.get_company_by_symbol(symbol)
                    if company:
                        # Find order for this symbol
                        order_info = next(
                            (o for o in orders if o.get('symbol') == symbol),
                            None
                        )
                        
                        allocated_companies.append({
                            'symbol': symbol,
                            'name': company.get('name'),
                            'order_id': order_info.get('order_id') if order_info else None,
                            'allocated_at': order_info.get('timestamp') if order_info else None,
                            'amount': order_info.get('amount') if order_info else None
                        })
                
                return jsonify({
                    'success': True,
                    'count': len(allocated_companies),
                    'companies': allocated_companies
                })
                
            except Exception as e:
                logger.exception(f"Error getting allocated companies: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/orders', methods=['GET'])
        def get_orders():
            """
            Get order history (includes simulated orders)
            
            Returns:
                JSON: Order history
            """
            try:
                # Get today's orders from allocation tracker
                today_orders = self.allocation_tracker.get_today_orders()
                
                # Also load simulated orders from file
                simulated_orders = []
                if os.path.exists(config.ORDER_HISTORY_FILE):
                    try:
                        with open(config.ORDER_HISTORY_FILE, 'r') as f:
                            simulated_orders = json.load(f)
                    except:
                        pass
                
                # Get allocation history (last 7 days)
                history = self.allocation_tracker.get_allocation_history(days=7)
                
                return jsonify({
                    'success': True,
                    'today_orders': today_orders,
                    'simulated_orders': simulated_orders[-50:],  # Last 50 simulated orders
                    'history': history,
                    'paper_trading': config.PAPER_TRADING
                })
                
            except Exception as e:
                logger.exception(f"Error getting orders: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """
            Get system status and last execution time
            
            Returns:
                JSON: System status information
            """
            try:
                status = {
                    'success': True,
                    'authenticated': self.client.authenticated if self.client else False,
                    'scheduler_status': None,
                    'last_execution': None
                }
                
                if self.scheduler:
                    scheduler_status = self.scheduler.get_status()
                    status['scheduler_status'] = scheduler_status
                    status['last_execution'] = scheduler_status.get('last_execution_time')
                
                return jsonify(status)
                
            except Exception as e:
                logger.exception(f"Error getting status: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/top-stocks', methods=['GET'])
        def get_top_stocks():
            """
            Get top N stocks eligible for allocation (default: 5)
            
            Query params:
                limit: Number of stocks to return (default: 5)
            
            Returns:
                JSON: Top N eligible stocks
            """
            try:
                from flask import request
                limit = request.args.get('limit', default=5, type=int)
                
                top_stocks = self.stock_analyzer.get_top_n_stocks(n=limit)
                
                # Format response
                stocks = []
                for stock in top_stocks:
                    is_allocated = self.allocation_tracker.is_allocated_today(
                        stock['symbol']
                    )
                    
                    stocks.append({
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'current_price': round(stock['current_price'], 2),
                        'ema': round(stock['ema'], 2),
                        'fall_percentage': round(stock['fall_percentage'], 2),
                        'token': stock['token'],
                        'exchange': stock['exchange'],
                        'is_allocated_today': is_allocated
                    })
                
                return jsonify({
                    'success': True,
                    'count': len(stocks),
                    'stocks': stocks
                })
                
            except Exception as e:
                logger.exception(f"Error getting top stocks: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/run-now', methods=['POST'])
        def run_algorithm_now():
            """
            Manually trigger the trading algorithm (for testing)
            
            Returns:
                JSON: Execution result
            """
            try:
                if not self.scheduler:
                    return jsonify({
                        'success': False,
                        'error': 'Scheduler not available'
                    }), 400
                
                self.scheduler.run_now()
                
                return jsonify({
                    'success': True,
                    'message': 'Algorithm execution triggered'
                })
                
            except Exception as e:
                logger.exception(f"Error running algorithm: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        # New endpoints matching frontend expectations
        @self.app.route('/api/stocks', methods=['GET'])
        def get_stocks():
            """
            Get eligible stocks in frontend Stock format
            
            Returns:
                JSON: List of stocks matching frontend Stock interface
            """
            try:
                top_stocks = self.stock_analyzer.get_top_n_stocks(n=config.MAX_COMPANIES)
                
                logger.info(f"API /api/stocks: Found {len(top_stocks)} top stocks")
                
                # Format to match frontend Stock interface
                stocks = []
                for idx, stock in enumerate(top_stocks, 1):
                    # Calculate previous close from EMA (approximation)
                    # In real scenario, fetch from historical data
                    previous_close = stock['ema']  # Approximation
                    last_close = stock['current_price']
                    
                    # Calculate quantity
                    quantity = int(config.ALLOCATION_PER_COMPANY / last_close) if last_close > 0 else 0
                    
                    is_allocated = self.allocation_tracker.is_allocated_today(stock['symbol'])
                    
                    stocks.append({
                        'id': str(idx),
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'previousClose': round(previous_close, 2),
                        'lastClose': round(last_close, 2),
                        'dropPercent': round(stock['fall_percentage'], 2),
                        'rank': idx,
                        'allocatedAmount': config.ALLOCATION_PER_COMPANY,
                        'quantity': quantity,
                        'orderStatus': 'simulated' if is_allocated else 'pending'
                    })
                
                logger.info(f"API /api/stocks: Returning {len(stocks)} stocks to frontend")
                
                if len(stocks) == 0:
                    logger.warning("API /api/stocks: No eligible stocks found (empty array being returned)")
                else:
                    logger.info(f"API /api/stocks: Eligible stocks: {[s['symbol'] for s in stocks]}")
                
                return jsonify({
                    'success': True,
                    'stocks': stocks
                })
                
            except Exception as e:
                logger.exception(f"Error getting stocks: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'stocks': []
                }), 500
        
        @self.app.route('/api/capital', methods=['GET'])
        def get_capital():
            """
            Get capital overview
            
            Returns:
                JSON: Capital information matching frontend CapitalInfo interface
            """
            try:
                orders = self.allocation_tracker.get_today_orders()
                deployed = sum(order.get('amount', 0) for order in orders)
                available = config.TOTAL_CAPITAL - deployed
                
                # Count unique scan dates
                history = self.allocation_tracker.get_allocation_history(days=30)
                scan_count = len(history)
                
                return jsonify({
                    'success': True,
                    'capital': {
                        'total': config.TOTAL_CAPITAL,
                        'deployed': round(deployed, 2),
                        'available': round(available, 2),
                        'scanCount': scan_count
                    }
                })
                
            except Exception as e:
                logger.exception(f"Error getting capital: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'capital': {
                        'total': config.TOTAL_CAPITAL,
                        'deployed': 0,
                        'available': config.TOTAL_CAPITAL,
                        'scanCount': 0
                    }
                }), 500
        
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """
            Get system logs
            
            Returns:
                JSON: List of log entries matching frontend LogEntry interface
            """
            try:
                # Generate logs from recent activity
                logs = []
                
                # Add status log
                logs.append({
                    'id': 'log_status',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': 'System operational',
                    'severity': 'success'
                })
                
                # Add order logs
                orders = self.allocation_tracker.get_today_orders()
                for idx, order in enumerate(orders, 1):
                    logs.append({
                        'id': f'log_order_{idx}',
                        'timestamp': order.get('timestamp', datetime.now().isoformat()).split('T')[1][:8] if 'T' in str(order.get('timestamp', '')) else datetime.now().strftime('%H:%M:%S'),
                        'message': f"Order placed: {order.get('symbol', 'N/A')} - {order.get('amount', 0):.2f}",
                        'severity': 'success'
                    })
                
                # Reverse to show latest first
                logs.reverse()
                
                return jsonify({
                    'success': True,
                    'logs': logs[:50]  # Limit to 50 most recent
                })
                
            except Exception as e:
                logger.exception(f"Error getting logs: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'logs': []
                }), 500
        
        @self.app.route('/api/ai/chat', methods=['POST'])
        def ai_chat():
            """
            AI chat endpoint using Gemini
            
            Request body:
                {
                    "prompt": "user question",
                    "context": {
                        "stocks": [...],
                        "orders": [...],
                        "capital": {...},
                        "stock_context": {...}
                    }
                }
            
            Returns:
                JSON: AI response
            """
            try:
                data = request.get_json()
                prompt = data.get('prompt', '')
                context = data.get('context', {})
                
                if not prompt:
                    return jsonify({
                        'success': False,
                        'error': 'Prompt is required'
                    }), 400
                
                # Generate AI response
                response = self.gemini_client.generate_response(prompt, context)
                
                return jsonify({
                    'success': True,
                    'response': response
                })
                
            except Exception as e:
                logger.exception(f"Error in AI chat: {e}")
                # Return the error message from Gemini client if available
                error_response = 'I encountered an error. Please try again.'
                try:
                    # Try to get a more specific error from Gemini client
                    if hasattr(self.gemini_client, 'model') and self.gemini_client.model is None:
                        error_response = (
                            "AI service is unavailable. The Gemini API key may be missing or invalid. "
                            "Please check the backend configuration. Trading features are still available."
                        )
                except:
                    pass
                
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'response': error_response
                }), 500
        
        @self.app.route('/api/ai/analyze', methods=['POST'])
        def ai_analyze():
            """
            Stock analysis endpoint
            
            Request body:
                {
                    "type": "stocks" | "allocation" | "trades" | "risk",
                    "data": {...}
                }
            
            Returns:
                JSON: Analysis response
            """
            try:
                data = request.get_json()
                analysis_type = data.get('type', 'stocks')
                analysis_data = data.get('data', {})
                
                if analysis_type == 'stocks':
                    stocks = analysis_data.get('stocks', [])
                    response = self.gemini_client.analyze_stocks(stocks)
                elif analysis_type == 'allocation':
                    capital = analysis_data.get('capital', {})
                    response = self.gemini_client.explain_allocation(capital)
                elif analysis_type == 'trades':
                    orders = analysis_data.get('orders', [])
                    response = self.gemini_client.summarize_trades(orders)
                elif analysis_type == 'risk':
                    stocks = analysis_data.get('stocks', [])
                    response = self.gemini_client.analyze_risk(stocks)
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid analysis type'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'response': response
                })
                
            except Exception as e:
                logger.exception(f"Error in AI analysis: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/backtest', methods=['POST'])
        def run_backtest():
            """
            Run backtest simulation
            
            Request body:
                {
                    "days": 7,  // Number of days to simulate
                    "start_date": "2025-01-10"  // Optional start date
                }
            
            Returns:
                JSON: Backtest results
            """
            try:
                data = request.get_json() or {}
                days = data.get('days', 7)
                start_date_str = data.get('start_date')
                
                # Parse start date if provided
                start_date = None
                if start_date_str:
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        start_date = pytz.timezone(config.MARKET_TIMEZONE).localize(start_date)
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': 'Invalid start_date format. Use YYYY-MM-DD'
                        }), 400
                
                # Run backtest
                results = self.backtester.run_backtest(days=days, start_date=start_date)
                
                # Check if backtest returned an error
                if results and 'error' in results:
                    logger.error(f"Backtest failed: {results['error']}")
                    return jsonify({
                        'success': False,
                        'error': results['error'],
                        'results': None
                    }), 400
                
                # Save results (if no error)
                if results and 'error' not in results:
                    try:
                        saved_file = self.backtester.save_results(results)
                    except Exception as save_error:
                        logger.warning(f"Failed to save backtest results: {save_error}")
                        saved_file = None
                else:
                    saved_file = None
                
                logger.info(f"Backtest completed successfully: {results.get('total_orders', 0)} orders, {results.get('simulated_days', 0)} days simulated")
                
                return jsonify({
                    'success': True,
                    'results': results,
                    'saved_to': saved_file
                })
                
            except Exception as e:
                logger.exception(f"Error running backtest: {e}")
                error_message = str(e)
                
                # Provide user-friendly error messages
                if 'authenticated' in error_message.lower() or 'authentication' in error_message.lower():
                    error_message = "Authentication required. Please ensure HISTORICAL and MARKET API clients are configured."
                elif 'historical' in error_message.lower() or 'data' in error_message.lower():
                    error_message = "Unable to fetch historical data. Please check HISTORICAL_API_KEY configuration."
                
                return jsonify({
                    'success': False,
                    'error': error_message,
                    'results': None
                }), 500
        
        @self.app.route('/api/backtest/results', methods=['GET'])
        def get_backtest_results():
            """
            Get latest backtest results
            
            Returns:
                JSON: Latest backtest results
            """
            try:
                # Find latest backtest result file
                data_dir = config.DATA_DIR
                if not os.path.exists(data_dir):
                    return jsonify({
                        'success': False,
                        'error': 'No backtest results found'
                    }), 404
                
                # Find all backtest result files
                import glob
                result_files = glob.glob(os.path.join(data_dir, 'backtest_results_*.json'))
                
                if not result_files:
                    return jsonify({
                        'success': False,
                        'error': 'No backtest results found'
                    }), 404
                
                # Get the latest file
                latest_file = max(result_files, key=os.path.getctime)
                
                # Load results
                with open(latest_file, 'r') as f:
                    results = json.load(f)
                
                return jsonify({
                    'success': True,
                    'results': results,
                    'file': latest_file
                })
                
            except Exception as e:
                logger.exception(f"Error getting backtest results: {e}")
                return jsonify({
                    'success': False,
                    'error': f"Failed to load backtest results: {str(e)}",
                    'results': None
                }), 500
    
    def _register_static_routes(self):
        """Register routes for serving static frontend files"""
        
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def serve_frontend(path):
            """
            API-only mode: Frontend is served separately on Vercel
            This route returns a helpful message for root access
            """
            # If path starts with /api, let API routes handle it
            if path.startswith('api'):
                return jsonify({'error': 'API endpoint not found'}), 404
            
            # For root or any non-API path, return API info
            return jsonify({
                'service': 'Trading Bot API',
                'status': 'running',
                'message': 'This is the backend API. Frontend is hosted separately.',
                'api_endpoints': {
                    'health': '/api/health',
                    'stocks': '/api/stocks',
                    'capital': '/api/capital',
                    'orders': '/api/orders',
                    'logs': '/api/logs',
                    'status': '/api/status',
                    'backtest': 'POST /api/backtest',
                    'ai_chat': 'POST /api/ai/chat'
                },
                'documentation': 'See README.md for full API documentation'
            }), 200
    
    def run(self, host=None, port=None, debug=None):
        """
        Run the Flask server
        
        Args:
            host: Host address (defaults to config)
            port: Port number (defaults to config)
            debug: Debug mode (defaults to config)
        """
        host = host or config.FLASK_HOST
        port = port or config.FLASK_PORT
        debug = debug if debug is not None else config.FLASK_DEBUG
        
        logger.info(f"Starting Flask API server on {host}:{port}")
        logger.info(f"API endpoints available at http://{host}:{port}/api/")
        logger.info("Running in API-only mode (frontend served separately)")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

