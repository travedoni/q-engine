# Systematic Alpha Factor Research & Backtesting Engine

A quantitative research platform for discovering, testing, and backtesting systematic alpha factors on equity markets.

## Overview

Built an end-to-end system to research momentum-based trading strategies using 5 years of historical data for 100 S&P 500 stocks. Discovered that 252-day price momentum has statistically significant predictive power (IC = 0.032, p < 0.01), though underperformed buy-and-hold in the strong 2024-2026 bull market.

## Key Features

- **Automated Data Pipeline**: PostgreSQL database with daily refresh capability
- **Factor Library**: Modular factor system with normalization and outlier handling
- **Backtesting Engine**: Event-driven backtester with transaction costs and performance analytics
- **IC Analysis**: Statistical validation using Information Coefficient methodology

## Results

**252-Day Momentum Strategy (2022-2026)**
- Total Return: +26.3%
- CAGR: 6.0%
- Sharpe Ratio: 0.45
- Max Drawdown: -8.0%
- S&P 500 Benchmark: +58.8%

**Key Finding**: Long-term momentum is predictive but underperformed in strong bull market due to universe bias and long-short structure.

## Tech Stack

- **Python**: pandas, numpy, scipy, matplotlib
- **Database**: PostgreSQL
- **Data**: yfinance API
- **Architecture**: OOP with factory pattern

## Project Structure
```
q-engine/
├── src/
│   ├── factors/          # Alpha factor library
│   ├── backtest/         # Backtesting engine
│   ├── data_fetcher.py   # Data collection
│   └── db_manager.py     # Database interface
├── sql/
│   └── schema.sql        # Database schema
├── scripts/
│   ├── setup_database.py
│   └── download_data.py
└── notebooks/            # Research & analysis
```

## Setup
```bash
# Create database
createdb quant_research

# Install dependencies
pip install -r requirements.txt

# Initialize
python scripts/setup_database.py
python scripts/download_data.py
```

## Usage
```python
from factors import PriceMomentum
from backtest import BacktestEngine

# Calculate factor
momentum = PriceMomentum(lookback_days=252)
factor_values = momentum.calculate(prices)

# Run backtest
engine = BacktestEngine(initial_capital=1_000_000)
portfolio = engine.run_long_short(prices, factor_values)
```

## Future Improvements

- Expand universe to full S&P 500
- Add value and quality factors
- Implement portfolio optimization
- Test long-only vs long-short
