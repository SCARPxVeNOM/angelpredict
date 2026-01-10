# NSE Automated Trading Dashboard

A professional, production-grade web dashboard for an automated after-market stock trading simulation platform targeting Indian markets (NSE).

## 🎯 Features

- **Real-time Market Scanning** - Automated scanning after market close
- **Smart Stock Selection** - Filters stocks with ≤ -5% drop and picks top 5
- **Paper Trading Mode** - Simulates trades with ₹3,00,000 virtual capital
- **Angel One Integration** - Built for Angel One SmartAPI
- **Professional UI** - Institutional-grade fintech interface comparable to Zerodha Kite and TradingView

## 🚀 Tech Stack

- **React 18** + **Vite** - Fast, modern development
- **TypeScript** - Type-safe code
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization
- **Lucide Icons** - Clean, modern icons
- **Zustand** - State management

## 📦 Installation

```bash
npm install
```

## 🏃 Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Build

```bash
npm run build
```

## 📊 Trading Logic

1. **Scan Time**: After market close
2. **Data Source**: Angel One SmartAPI
3. **Filter**: Stocks with drop ≤ -5%
4. **Sort**: Ascending by drop percentage
5. **Selection**: Top 5 stocks
6. **Order Size**: ₹15,000 per stock
7. **Capital**: ₹3,00,000 total (paper money)

## 🎨 UI Components

- **Top Navigation Bar** - Market status, capital summary, mode indicator
- **Sidebar** - Navigation menu with Dashboard, Orders, Logs
- **Capital Overview** - Four animated cards showing capital metrics
- **Strategy Panel** - Read-only display of trading rules
- **Stock Table** - Interactive table with top 5 stocks
- **Stock Detail Drawer** - Detailed view with mini charts
- **Orders Panel** - Timeline-style order history
- **Logs Panel** - Terminal-style system logs

## 🎯 Design Philosophy

- Dark mode first
- Glassmorphism effects
- High information density
- Smooth micro-animations
- Zero clutter
- Professional fintech aesthetic

## 📝 License

MIT

## 👨‍💻 Author

Built for serious fintech applications, hackathons, and portfolio demonstrations.
