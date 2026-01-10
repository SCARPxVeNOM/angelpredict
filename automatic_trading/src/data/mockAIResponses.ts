// Mock AI responses for different query types
export const mockAIResponses: Record<string, string> = {
  'why_selected': `Based on today's scan criteria, these 5 stocks were selected because:

**Selection Criteria Met:**
• All stocks showed a drop of ≤ -5% from previous close
• Sorted by smallest drop (most conservative approach)
• Sufficient liquidity for ₹15,000 allocation per stock

**Top 5 Breakdown:**

1. **TATASTEEL** (-5.37%)
   - Largest drop in selection
   - Steel sector weakness
   - High volume, good liquidity

2. **HINDALCO** (-4.91%)
   - Aluminum sector correction
   - Strong fundamentals despite drop

3. **JSWSTEEL** (-4.86%)
   - Metal sector correlation
   - Technical support nearby

4. **VEDL** (-4.68%)
   - Commodity-linked volatility
   - Diversification benefit

5. **COALINDIA** (-4.55%)
   - Smallest drop in selection
   - PSU stability factor

⚠️ **Risk Note:** All 5 stocks are from metals/commodities sector - high correlation risk.`,

  'why_rejected': `Stocks were rejected from today's scan for the following reasons:

**Primary Rejection Criteria:**

1. **Drop < -5% threshold** (Most common)
   - 2,800+ stocks didn't meet minimum drop requirement
   - Only 47 stocks qualified with ≤ -5% drop

2. **Ranking beyond Top 5**
   - 42 stocks met drop criteria but ranked 6-47
   - Examples: SAIL (-5.89%), NMDC (-5.45%), MOIL (-5.12%)

3. **Liquidity Filters** (Applied pre-scan)
   - Stocks with avg volume < 100K shares
   - Penny stocks (price < ₹10)
   - Stocks in trade-to-trade segment

4. **Corporate Actions**
   - Stocks with pending dividends/splits
   - Suspended or delisted securities

**Notable Rejections:**
• SAIL: -5.89% (ranked 6th, just missed cut)
• NMDC: -5.45% (ranked 7th)
• HINDZINC: -5.23% (ranked 8th)

💡 **Insight:** Expanding to Top 10 would add ₹75K more deployment but increase sector concentration risk.`,

  'riskiest_trade': `**Risk Analysis - Today's Trades:**

🔴 **Highest Risk: TATASTEEL**

**Why it's riskiest:**
• Largest drop: -5.37% (highest volatility signal)
• Steel sector facing headwinds
• Highest quantity: 111 shares (₹14,968 exposure)
• Technical: Near 52-week low zone

**Risk Factors:**
1. **Sector Risk:** All 5 picks are metals/commodities
2. **Correlation:** 0.85+ correlation between picks
3. **Macro Sensitivity:** Vulnerable to global commodity prices

**Risk Mitigation Present:**
✅ Equal allocation (₹15K each) limits single-stock impact
✅ Paper trading mode - no real capital at risk
✅ Automatic execution removes emotional bias

**Risk Score Breakdown:**
• TATASTEEL: 8.5/10 (Highest volatility)
• HINDALCO: 7.2/10 (Sector correlation)
• JSWSTEEL: 7.0/10 (Similar to HINDALCO)
• VEDL: 6.8/10 (Commodity exposure)
• COALINDIA: 5.5/10 (PSU stability, lowest risk)

⚠️ **Portfolio Risk:** High sector concentration = 9/10 risk level`,

  'explain_allocation': `**Capital Allocation Breakdown:**

**Total Capital:** ₹3,00,000 (Paper Money)

**Allocation Strategy:**
• **Per-stock allocation:** ₹15,000 (fixed)
• **Maximum picks:** 5 stocks
• **Total deployed:** ₹74,216.55 (24.74%)
• **Available balance:** ₹2,25,783.45 (75.26%)

**Why This Allocation?**

1. **Equal Weighting Philosophy**
   - Each stock gets exactly ₹15,000
   - No bias toward any single pick
   - Simplifies risk management

2. **Conservative Deployment**
   - Only 25% capital used per scan
   - Preserves 75% for future opportunities
   - Protects against concentrated losses

3. **Quantity Calculation**
   - Qty = ₹15,000 ÷ Last Close Price
   - TATASTEEL: 15000 ÷ 134.85 = 111 shares
   - COALINDIA: 15000 ÷ 393.50 = 38 shares

**Actual Deployment:**
| Stock | Allocation | Qty | Actual Cost |
|-------|-----------|-----|-------------|
| TATASTEEL | ₹15,000 | 111 | ₹14,968.35 |
| HINDALCO | ₹15,000 | 25 | ₹14,936.25 |
| JSWSTEEL | ₹15,000 | 17 | ₹14,485.70 |
| VEDL | ₹15,000 | 35 | ₹14,873.25 |
| COALINDIA | ₹15,000 | 38 | ₹14,953.00 |

💡 **Note:** Slight variations due to whole share purchases (no fractional shares).`,

  'what_if_4_percent': `**What-If Analysis: -4% Threshold**

**Current Strategy:** Drop ≤ -5%
**Proposed Change:** Drop ≤ -4%

**Impact Simulation:**

**1. Stock Selection Changes:**
• Current picks: 5 stocks (all -4.55% to -5.37%)
• With -4% threshold: 12 additional stocks qualify
• New pool: 59 stocks total (vs current 47)

**2. Top 5 Would Change To:**
1. TATASTEEL: -5.37% (same)
2. HINDALCO: -4.91% (same)
3. JSWSTEEL: -4.86% (same)
4. VEDL: -4.68% (same)
5. COALINDIA: -4.55% (same)

**Result:** No change in Top 5! All current picks are between -4% and -5%.

**3. If We Picked Stocks at -4.00% to -4.54%:**
Potential new entries:
• ADANIPORTS: -4.45%
• SUNPHARMA: -4.32%
• DRREDDY: -4.18%
• CIPLA: -4.05%

**4. Risk Impact:**
• ✅ Better sector diversification (pharma + ports)
• ⚠️ Smaller drops = less "value" opportunity
• ⚠️ Higher false positive rate

**5. Capital Impact:**
• Same: ₹75,000 deployed (5 stocks × ₹15K)
• No change in allocation logic

**Recommendation:**
🔵 Current -5% threshold is optimal for this strategy. -4% would add noise without improving Top 5 quality.`,

  'summarize_trades': `**Today's Trading Summary**
*Generated: 15:45:33 | Scan Date: 10 Jan 2025*

**Execution Overview:**
✅ All 5 orders simulated successfully
⏱️ Total execution time: 10 seconds
📊 Scan processed: 2,847 NSE stocks

**Orders Placed:**

| # | Symbol | Qty | Price | Amount | Status |
|---|--------|-----|-------|--------|--------|
| 1 | TATASTEEL | 111 | ₹134.85 | ₹14,968 | ✅ Simulated |
| 2 | HINDALCO | 25 | ₹597.45 | ₹14,936 | ✅ Simulated |
| 3 | JSWSTEEL | 17 | ₹852.10 | ₹14,486 | ✅ Simulated |
| 4 | VEDL | 35 | ₹424.95 | ₹14,873 | ✅ Simulated |
| 5 | COALINDIA | 38 | ₹393.50 | ₹14,953 | ✅ Simulated |

**Capital Metrics:**
• Total Deployed: ₹74,216.55
• Available: ₹2,25,783.45
• Utilization: 24.74%

**Sector Exposure:**
• Metals & Mining: 100% (High concentration ⚠️)

**Key Insights:**
1. All picks from same sector - correlation risk
2. Average drop: -4.87% (moderate opportunity)
3. Conservative capital deployment (25%)
4. No execution errors or API failures

**Risk Flags:**
🔴 Sector concentration: 10/10 stocks in metals
🟡 Volatility: TATASTEEL showing highest drop
🟢 Liquidity: All stocks highly liquid

**Next Steps:**
• Monitor positions at market open
• Consider sector diversification in next scan
• Review stop-loss levels if deploying real capital`,

  'default': `I'm your AI Market Analyst. I can help explain:

• Why specific stocks were selected or rejected
• Risk analysis of today's trades
• Capital allocation logic
• What-if scenarios for strategy changes
• Post-scan summaries and insights

**I cannot:**
❌ Predict future prices
❌ Give buy/sell recommendations
❌ Execute trades
❌ Access live broker APIs

💡 **Try asking:**
"Why were these stocks selected?"
"Which trade is riskiest?"
"Explain capital allocation"
"What if threshold was -4%?"

This is a simulation environment for learning and analysis only.`
}

// Function to get appropriate response based on user query
export const getAIResponse = (query: string, context?: any): string => {
  const lowerQuery = query.toLowerCase()
  
  if (lowerQuery.includes('why') && (lowerQuery.includes('select') || lowerQuery.includes('pick') || lowerQuery.includes('chose'))) {
    return mockAIResponses.why_selected
  }
  
  if (lowerQuery.includes('reject') || lowerQuery.includes('not select') || lowerQuery.includes('excluded')) {
    return mockAIResponses.why_rejected
  }
  
  if (lowerQuery.includes('risk') || lowerQuery.includes('dangerous') || lowerQuery.includes('volatile')) {
    return mockAIResponses.riskiest_trade
  }
  
  if (lowerQuery.includes('allocation') || lowerQuery.includes('capital') || lowerQuery.includes('money')) {
    return mockAIResponses.explain_allocation
  }
  
  if (lowerQuery.includes('what if') || lowerQuery.includes('threshold') || lowerQuery.includes('-4%') || lowerQuery.includes('4%')) {
    return mockAIResponses.what_if_4_percent
  }
  
  if (lowerQuery.includes('summar') || lowerQuery.includes('overview') || lowerQuery.includes('report')) {
    return mockAIResponses.summarize_trades
  }
  
  // Context-specific responses
  if (context?.stockSymbol) {
    return `**Analysis: ${context.stockSymbol}**

**Selection Reason:**
This stock was picked because it met all scan criteria:
• Drop: ${context.dropPercent || 'N/A'}% (≤ -5% threshold)
• Rank: #${context.rank || 'N/A'} in today's scan
• Liquidity: Sufficient for ₹15,000 allocation

**Trade Details:**
• Allocated: ₹15,000
• Quantity: ${context.quantity || 'N/A'} shares
• Entry Price: ₹${context.price || 'N/A'}

**Risk Assessment:**
${context.rank <= 2 ? '⚠️ Higher volatility (larger drop)' : '✅ Relatively stable (smaller drop)'}

**Sector Context:**
Part of metals/commodities sector concentration in today's picks.

💡 This is a simulated trade in paper trading mode.`
  }
  
  return mockAIResponses.default
}

// Simulate API latency
export const simulateAILatency = (): Promise<void> => {
  const delay = Math.floor(Math.random() * 400) + 800 // 800-1200ms
  return new Promise(resolve => setTimeout(resolve, delay))
}
