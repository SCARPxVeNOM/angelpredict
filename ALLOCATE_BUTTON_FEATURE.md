# Allocate Button Feature

## Overview
Added an "Allocate" button to execute paper trades for the top 5 scanned stocks with ₹15,000 total allocation (₹3,000 per company).

## Changes Made

### 1. Configuration Update (`config/config.py`)
**Changed allocation model:**
- **Before**: `ALLOCATION_PER_COMPANY = 15000` (₹15,000 per company)
- **After**: 
  - `TOTAL_ALLOCATION = 15000` (₹15,000 total for all 5 companies)
  - `ALLOCATION_PER_COMPANY = 3000` (₹3,000 per company)

### 2. Backend API Endpoint (`api/flask_api.py`)
**Added new endpoint: `POST /api/stocks/allocate`**

**Request:**
```json
{
  "stocks": [
    {
      "symbol": "ITC",
      "name": "ITC Limited",
      "lastClose": 337.15,
      "quantity": 8,
      "allocatedAmount": 3000
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "id": "PAPER_ITC_20260111_123456",
      "symbol": "ITC",
      "quantity": 8,
      "price": 337.15,
      "amount": 3000,
      "timestamp": "2026-01-11T12:34:56",
      "status": "simulated"
    }
  ],
  "total_allocated": 15000,
  "message": "Successfully allocated 5 paper trades"
}
```

**Features:**
- Creates simulated paper trade orders for each stock
- Saves orders to `data/order_history.json`
- Tracks allocations using `AllocationTracker`
- Logs all allocation activities

### 3. Frontend API Service (`automatic_trading/src/services/api.ts`)
**Added new method: `allocateStocks(stocks: Stock[])`**

```typescript
async allocateStocks(stocks: Stock[]): Promise<any> {
  const response = await this.request('/api/stocks/allocate', {
    method: 'POST',
    body: JSON.stringify({ stocks })
  });
  return response;
}
```

### 4. Stock Table Component (`automatic_trading/src/components/StockTable.tsx`)
**Added "Allocate" button with:**
- Green accent color matching UI theme
- Loading state ("Allocating...")
- Disabled when no stocks or already allocating
- Success/error alerts
- Auto-updates stock status to "simulated" after allocation

**UI Layout:**
```
[Scan Now] [Allocate] [Total: 5 stocks]
```

**Button Styling:**
- Background: `bg-accent-success/10`
- Border: `border-accent-success/30`
- Hover: `hover:bg-accent-success/20`
- Icon: ChevronRight (green)
- Text: "Allocate" / "Allocating..."

## User Flow

1. **Scan Stocks**: Click "Scan Now" to fetch eligible stocks (≥3% below 20 EMA)
2. **Review**: See top 5 stocks with ₹3,000 allocation each
3. **Allocate**: Click "Allocate" to execute paper trades
4. **Confirmation**: See success message with total allocated amount
5. **Status Update**: Stock status changes from "PENDING" to "SIMULATED"
6. **View Orders**: Check Orders panel to see allocated trades

## Allocation Details

- **Total Allocation**: ₹15,000
- **Per Company**: ₹3,000
- **Max Companies**: 5
- **Trade Type**: Paper trading (simulated)
- **Order ID Format**: `PAPER_{SYMBOL}_{TIMESTAMP}`

## Example Allocation

If scan finds these stocks:
1. ITC @ ₹337.15 → 8 shares × ₹337.15 = ₹2,697.20 (allocated ₹3,000)
2. ADANIENT @ ₹2,153.78 → 1 share × ₹2,153.78 = ₹2,153.78 (allocated ₹3,000)
3. HDFCBANK @ ₹929.08 → 3 shares × ₹929.08 = ₹2,787.24 (allocated ₹3,000)
4. RELIANCE @ ₹1,475.58 → 2 shares × ₹1,475.58 = ₹2,951.16 (allocated ₹3,000)
5. TITAN @ ₹2,523.48 → 1 share × ₹2,523.48 = ₹2,523.48 (allocated ₹3,000)

**Total Allocated**: ₹15,000 (₹3,000 × 5 companies)

## Files Modified

1. `config/config.py` - Updated allocation amounts
2. `api/flask_api.py` - Added `/api/stocks/allocate` endpoint
3. `automatic_trading/src/services/api.ts` - Added `allocateStocks()` method
4. `automatic_trading/src/components/StockTable.tsx` - Added Allocate button and handler

## Testing

1. Start backend: `python main.py`
2. Start frontend: `cd automatic_trading && npm run dev`
3. Click "Scan Now" to fetch stocks
4. Click "Allocate" to execute paper trades
5. Check Orders panel for allocated trades
6. Verify `data/order_history.json` contains orders

## Next Steps

- Deploy changes to Render (backend)
- Deploy changes to Vercel (frontend)
- Test on production environment
- Monitor logs for allocation activities
