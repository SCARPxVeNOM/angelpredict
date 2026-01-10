"""
Nifty 50 Fetcher
Fetches and manages Nifty 50 company list with AngelOne symbol mappings
"""
import json
import os
from logzero import logger
from config import config


class Nifty50Fetcher:
    """Fetches Nifty 50 company list"""
    
    def __init__(self, symbols_file=None):
        """
        Initialize Nifty 50 fetcher
        
        Args:
            symbols_file: Path to Nifty 50 symbols JSON file
        """
        self.symbols_file = symbols_file or config.NIFTY50_SYMBOLS_FILE
        self.companies = self._load_symbols()
    
    def _load_symbols(self):
        """
        Load Nifty 50 symbols from JSON file
        
        Returns:
            list: List of company dictionaries
        """
        try:
            if os.path.exists(self.symbols_file):
                with open(self.symbols_file, 'r') as f:
                    companies = json.load(f)
                    logger.info(f"Loaded {len(companies)} Nifty 50 companies")
                    return companies
            else:
                logger.error(f"Symbols file not found: {self.symbols_file}")
                return []
        except Exception as e:
            logger.exception(f"Error loading symbols: {e}")
            return []
    
    def get_all_companies(self):
        """
        Get all Nifty 50 companies
        
        Returns:
            list: List of all companies with their details
        """
        return self.companies
    
    def get_company_by_symbol(self, symbol):
        """
        Get company details by trading symbol
        
        Args:
            symbol: Trading symbol (e.g., "SBIN", "RELIANCE")
        
        Returns:
            dict: Company details or None if not found
        """
        for company in self.companies:
            if company.get('symbol') == symbol:
                return company
        return None
    
    def get_symbol_token(self, symbol):
        """
        Get symbol token ID for a given symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            str: Symbol token ID or None if not found
        """
        company = self.get_company_by_symbol(symbol)
        if company:
            return company.get('token')
        return None
    
    def get_trading_symbol(self, symbol):
        """
        Get full trading symbol with exchange suffix (e.g., "SBIN-EQ")
        
        Args:
            symbol: Base trading symbol
        
        Returns:
            str: Full trading symbol or None if not found
        """
        company = self.get_company_by_symbol(symbol)
        if company:
            base_symbol = company.get('symbol')
            exchange = company.get('exchange', 'NSE')
            # Format: SYMBOL-EQ for equity
            return f"{base_symbol}-EQ"
        return None
    
    def get_all_symbols(self):
        """
        Get list of all trading symbols
        
        Returns:
            list: List of trading symbols
        """
        return [company.get('symbol') for company in self.companies if company.get('symbol')]




