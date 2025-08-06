# Algo Trading System

## Overview
A Python-based algorithmic trading system that automatically analyzes stock data, generates trading signals using RSI and moving average strategies, and uses machine learning to predict price movements. The system logs all trades to Google Sheets and sends alerts via Telegram.

## Features
- Fetches real-time data from Yahoo Finance for NIFTY 50 stocks
- Trading strategy based on RSI oversold conditions and moving average crossovers
- Machine learning predictions using Decision Trees and Logistic Regression
- Automated logging to Google Sheets with separate tabs for trades, signals, and analytics
- Telegram notifications for trading signals and system alerts
- Comprehensive backtesting with performance metrics

## Quick Start

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the system:
```bash
python main.py
```

## Configuration
Edit `config.py` to customize:
- Stock symbols (currently TCS, INFY, RELIANCE)
- RSI parameters and moving average periods
- Google Sheets and Telegram credentials

## Strategy
- **Buy Signal**: RSI drops below 30 AND 20-day MA crosses above 50-day MA
- **Sell Signal**: RSI rises above 70 (profit taking)
- **Backtest Period**: 6 months of historical data
- **ML Features**: RSI, MACD, Volume ratios, Moving averages, Price changes

## Setup (Optional Integrations)

### Google Sheets
1. Create a Google Cloud project and enable Sheets API
2. Download service account credentials as `credentials.json`
3. Share your spreadsheet with the service account email

### Telegram Bot
1. Message @BotFather to create a new bot
2. Get your bot token and chat ID
3. Update the tokens in `config.py`

Note: System works fine without these - it will use mock implementations.

## Output
The system generates:
- Console output with real-time analysis results
- Log files with detailed timestamps
- Google Sheets with trade history and performance metrics
- Telegram alerts for trading signals

## Testing
Run the test suite:
```bash
python test_system.py
```

## Sample Output

```
Starting Algo Trading System
============================================================

DATA INGESTION:
  TCS.NS: 123 data points fetched
  INFY.NS: 123 data points fetched  
  RELIANCE.NS: 123 data points fetched

STRATEGY PERFORMANCE:
  Total Trades: 2
  Win Rate: 50.0%
  Total P&L: ₹1,250.00

ML MODEL PERFORMANCE:
  Average Accuracy: 58.5%
  Latest Predictions: Mixed signals

AUTOMATION STATUS:
  Google Sheets: Connected
  Telegram Bot: Connected
  All tests passed
```

## Files
- `main.py` - Main system orchestration
- `data_ingestion.py` - Yahoo Finance data fetching
- `strategy.py` - Trading strategy implementation
- `ml_model.py` - Machine learning predictions
- `utils.py` - Technical indicator calculations
- `config.py` - System configuration

## Notes
- The system handles missing data gracefully
- All external integrations have fallback mock implementations
- Logs are written to `trading_system.log` for debugging
- Performance varies with market conditions
