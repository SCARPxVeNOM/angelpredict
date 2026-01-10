"""
Google Gemini AI Client
Handles AI-powered analysis and chat for trading insights
"""
import warnings
# Suppress deprecation warning - package still works
warnings.filterwarnings('ignore', category=FutureWarning)
import google.generativeai as genai
from logzero import logger
from config import config
import json
from typing import Dict, List, Optional, Any


class GeminiClient:
    """Google Gemini API client for AI analysis"""
    
    def __init__(self, api_key=None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (defaults to config)
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response with context
        
        Args:
            prompt: User prompt/question
            context: Optional context data (stocks, orders, capital, etc.)
        
        Returns:
            str: AI response
        """
        try:
            # Build context-aware prompt
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.exception(f"Error generating Gemini response: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build context-aware prompt
        
        Args:
            prompt: User prompt
            context: Context data
        
        Returns:
            str: Full prompt with context
        """
        system_prompt = """You are an AI trading analyst assistant for a paper trading simulation platform. 
Your role is to help users understand trading decisions, analyze stock selections, and explain capital allocation strategies.

IMPORTANT DISCLAIMERS:
- This is a SIMULATION ONLY platform - no real money is involved
- You should NOT provide trading advice or price predictions
- You should NOT recommend buying or selling specific stocks
- Focus on explaining the logic and reasoning behind automated decisions
- Always remind users this is paper trading/simulation

When analyzing stocks, consider:
- Technical indicators (EMA, price movements)
- Sector correlations and diversification
- Risk factors and volatility
- Capital allocation strategies
- Market conditions and context

Be concise, clear, and educational. Use formatting like bullet points, bold text, and tables when appropriate."""

        full_prompt = f"{system_prompt}\n\n"
        
        # Add context if provided
        if context:
            context_str = self._format_context(context)
            full_prompt += f"Context:\n{context_str}\n\n"
        
        full_prompt += f"User Question: {prompt}\n\n"
        full_prompt += "Please provide a helpful analysis based on the context above."
        
        return full_prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context data for prompt
        
        Args:
            context: Context dictionary
        
        Returns:
            str: Formatted context string
        """
        parts = []
        
        if 'stocks' in context:
            stocks = context['stocks']
            parts.append("Selected Stocks:")
            for stock in stocks[:5]:  # Top 5
                parts.append(
                    f"- {stock.get('symbol', 'N/A')} ({stock.get('name', 'N/A')}): "
                    f"Price: ₹{stock.get('current_price', 0):.2f}, "
                    f"EMA: ₹{stock.get('ema', 0):.2f}, "
                    f"Fall: {stock.get('fall_percentage', 0):.2f}%"
                )
        
        if 'orders' in context:
            orders = context['orders']
            parts.append(f"\nRecent Orders ({len(orders)}):")
            for order in orders[:5]:  # Recent 5
                parts.append(
                    f"- {order.get('symbol', 'N/A')}: "
                    f"{order.get('quantity', 0)} shares @ ₹{order.get('price', 0):.2f}, "
                    f"Total: ₹{order.get('amount', 0):.2f}"
                )
        
        if 'capital' in context:
            capital = context['capital']
            parts.append(f"\nCapital Overview:")
            parts.append(f"- Total: ₹{capital.get('total', 0):,.2f}")
            parts.append(f"- Deployed: ₹{capital.get('deployed', 0):,.2f}")
            parts.append(f"- Available: ₹{capital.get('available', 0):,.2f}")
        
        if 'stock_context' in context:
            stock = context['stock_context']
            parts.append(f"\nStock Details:")
            parts.append(f"- Symbol: {stock.get('symbol', 'N/A')}")
            parts.append(f"- Name: {stock.get('name', 'N/A')}")
            parts.append(f"- Current Price: ₹{stock.get('current_price', 0):.2f}")
            parts.append(f"- EMA: ₹{stock.get('ema', 0):.2f}")
            parts.append(f"- Fall Percentage: {stock.get('fall_percentage', 0):.2f}%")
        
        return "\n".join(parts)
    
    def analyze_stocks(self, stocks_data: List[Dict[str, Any]]) -> str:
        """
        Analyze stock selection
        
        Args:
            stocks_data: List of stock dictionaries
        
        Returns:
            str: Analysis response
        """
        prompt = """Analyze the selected stocks and explain:
1. Why these stocks were selected based on the criteria
2. Sector distribution and correlation risks
3. Risk factors to consider
4. Capital allocation rationale

Be educational and focus on the logic behind the selection."""
        
        context = {'stocks': stocks_data}
        return self.generate_response(prompt, context)
    
    def explain_allocation(self, capital_data: Dict[str, Any]) -> str:
        """
        Explain capital allocation strategy
        
        Args:
            capital_data: Capital information dictionary
        
        Returns:
            str: Explanation response
        """
        prompt = """Explain the capital allocation strategy:
1. How capital is allocated per stock
2. Why ₹15,000 per stock (5% of total capital)
3. Risk management through diversification
4. Available capital and deployment percentage"""
        
        context = {'capital': capital_data}
        return self.generate_response(prompt, context)
    
    def summarize_trades(self, orders_data: List[Dict[str, Any]]) -> str:
        """
        Summarize trading activity
        
        Args:
            orders_data: List of order dictionaries
        
        Returns:
            str: Summary response
        """
        prompt = """Provide a comprehensive summary of today's trading activity:
1. Total orders placed
2. Capital deployed
3. Stock selection overview
4. Performance metrics (if available)
5. Key observations"""
        
        context = {'orders': orders_data}
        return self.generate_response(prompt, context)
    
    def analyze_risk(self, stocks_data: List[Dict[str, Any]]) -> str:
        """
        Analyze risk factors
        
        Args:
            stocks_data: List of stock dictionaries
        
        Returns:
            str: Risk analysis response
        """
        prompt = """Analyze the risk factors for the selected stocks:
1. Sector concentration risk
2. Volatility considerations
3. Market correlation
4. Individual stock risk factors
5. Overall portfolio risk assessment"""
        
        context = {'stocks': stocks_data}
        return self.generate_response(prompt, context)

