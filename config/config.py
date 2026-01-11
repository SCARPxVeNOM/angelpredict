"""
Configuration file for trading bot
Contains API keys, capital settings, and trading parameters
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
TRADING_API_KEY = os.getenv("TRADING_API_KEY", "9DYha4fz")
TRADING_SECRET_KEY = os.getenv("TRADING_SECRET_KEY", "07f4e644-bfba-4245-920b-fc287bfb7dd2")

HISTORICAL_API_KEY = os.getenv("HISTORICAL_API_KEY", "GEa34V7A")
HISTORICAL_SECRET_KEY = os.getenv("HISTORICAL_SECRET_KEY", "bd409a72-8ea4-44e3-b656-be829af41674")

MARKET_API_KEY = os.getenv("MARKET_API_KEY", "7TmcRllV")
MARKET_SECRET_KEY = os.getenv("MARKET_SECRET_KEY", "1a02e75d-1a1f-4f9a-96fb-e8a9e4107393")

# AngelOne Credentials (to be set in .env)
ANGELONE_USERNAME = os.getenv("ANGELONE_USERNAME", "")
ANGELONE_PASSWORD = os.getenv("ANGELONE_PASSWORD", "")  # Can be password or MPIN
ANGELONE_MPIN = os.getenv("ANGELONE_MPIN", "")  # MPIN for login (if using MPIN method)
ANGELONE_TOTP_TOKEN = os.getenv("ANGELONE_TOTP_TOKEN", "")  # QR code token for 2FA
USE_MPIN = os.getenv("USE_MPIN", "false").lower() == "true"  # Set to true to use MPIN instead of password

# Trading Parameters
TOTAL_CAPITAL = 300000  # ₹3,00,000
ALLOCATION_PER_COMPANY = 15000  # ₹15,000 per company (5% of total capital)
MAX_COMPANIES = 5  # Top 5 companies

# Market Settings
MARKET_CLOSE_HOUR = 15  # 3 PM
MARKET_CLOSE_MINUTE = 30  # 30 minutes
MARKET_TIMEZONE = "Asia/Kolkata"  # IST

# EMA Parameters
EMA_PERIOD = 20
EMA_TIMEFRAME = "ONE_DAY"  # Daily candles (changed from ONE_HOUR)
FALL_THRESHOLD = 3.0  # 3% below EMA

# Order Settings
ORDER_VARIETY = "NORMAL"
ORDER_PRODUCT_TYPE = "INTRADAY"  # Can be changed to DELIVERY
ORDER_DURATION = "DAY"
ORDER_TYPE = "LIMIT"
EXCHANGE = "NSE"

# Trading Mode
PAPER_TRADING = True  # Set to False to place real orders on AngelOne
SIMULATE_ORDERS = True  # Simulate orders instead of placing real trades

# Data Paths
DATA_DIR = "data"
NIFTY50_SYMBOLS_FILE = f"{DATA_DIR}/nifty50_symbols.json"
DAILY_ALLOCATIONS_FILE = f"{DATA_DIR}/daily_allocations.json"
ORDER_HISTORY_FILE = f"{DATA_DIR}/order_history.json"

# Gemini AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDU8bKCXRpEzvXeLG-mP6dT2Fm2P-koQ0Q")

# Frontend Settings
FRONTEND_BUILD_PATH = "automatic_trading/dist"
FRONTEND_INDEX_PATH = f"{FRONTEND_BUILD_PATH}/index.html"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Vercel frontend URL for CORS

# API Settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False
API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{FLASK_PORT}")

