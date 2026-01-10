"""
Allocation Tracker
Tracks daily allocations to prevent duplicate allocations within the same day
"""
import json
import os
from datetime import datetime, timedelta
from logzero import logger
from config import config


class AllocationTracker:
    """Tracks daily stock allocations"""
    
    def __init__(self, allocations_file=None):
        """
        Initialize allocation tracker
        
        Args:
            allocations_file: Path to allocations JSON file
        """
        self.allocations_file = allocations_file or config.DAILY_ALLOCATIONS_FILE
        self.allocations = self._load_allocations()
    
    def _load_allocations(self):
        """
        Load allocations from JSON file
        
        Returns:
            dict: Allocations data
        """
        try:
            if os.path.exists(self.allocations_file):
                with open(self.allocations_file, 'r') as f:
                    return json.load(f)
            else:
                # Create empty allocations structure
                return {}
        except Exception as e:
            logger.exception(f"Error loading allocations: {e}")
            return {}
    
    def _save_allocations(self):
        """Save allocations to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.allocations_file), exist_ok=True)
            
            with open(self.allocations_file, 'w') as f:
                json.dump(self.allocations, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving allocations: {e}")
    
    def _get_today_date(self):
        """
        Get today's date in YYYY-MM-DD format
        
        Returns:
            str: Today's date
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    def is_allocated_today(self, symbol):
        """
        Check if a company was allocated funds today
        
        Args:
            symbol: Company trading symbol
        
        Returns:
            bool: True if allocated today, False otherwise
        """
        today = self._get_today_date()
        
        if today in self.allocations:
            allocated_companies = self.allocations[today].get('allocated_companies', [])
            return symbol in allocated_companies
        
        return False
    
    def mark_allocated(self, symbol, order_id=None, amount=None):
        """
        Mark a company as allocated for today
        
        Args:
            symbol: Company trading symbol
            order_id: Order ID (optional)
            amount: Allocation amount (optional)
        """
        today = self._get_today_date()
        
        if today not in self.allocations:
            self.allocations[today] = {
                "date": today,
                "allocated_companies": [],
                "orders": []
            }
        
        # Add to allocated companies list if not already present
        if symbol not in self.allocations[today]['allocated_companies']:
            self.allocations[today]['allocated_companies'].append(symbol)
        
        # Add order details if provided
        if order_id:
            order_info = {
                "symbol": symbol,
                "order_id": order_id,
                "timestamp": datetime.now().isoformat()
            }
            if amount:
                order_info["amount"] = amount
            
            self.allocations[today]['orders'].append(order_info)
        
        self._save_allocations()
        logger.info(f"Marked {symbol} as allocated for {today}")
    
    def get_allocated_today(self):
        """
        Get list of companies allocated today
        
        Returns:
            list: List of symbols allocated today
        """
        today = self._get_today_date()
        
        if today in self.allocations:
            return self.allocations[today].get('allocated_companies', [])
        
        return []
    
    def get_today_orders(self):
        """
        Get all orders placed today
        
        Returns:
            list: List of order dictionaries
        """
        today = self._get_today_date()
        
        if today in self.allocations:
            return self.allocations[today].get('orders', [])
        
        return []
    
    def reset_daily_allocations(self):
        """
        Reset allocations for a new day (called automatically if date changes)
        Note: This is handled automatically by checking date, but can be called manually
        """
        today = self._get_today_date()
        
        # Remove old dates (keep only last 30 days)
        dates_to_remove = []
        for date in self.allocations.keys():
            if date != today:
                # Keep last 30 days
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    days_diff = (datetime.now() - date_obj).days
                    if days_diff > 30:
                        dates_to_remove.append(date)
                except:
                    dates_to_remove.append(date)
        
        for date in dates_to_remove:
            del self.allocations[date]
        
        self._save_allocations()
        logger.info(f"Reset allocations for new day: {today}")
    
    def get_allocation_history(self, days=7):
        """
        Get allocation history for last N days
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            dict: Allocation history
        """
        history = {}
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.allocations:
                history[date] = self.allocations[date]
        
        return history

