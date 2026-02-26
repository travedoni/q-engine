import pandas as pd
import numpy as np
from typing import Dict

class Portfolio:
    """
    Manages portfolio positions and tracks performance
    """

    def __init__(self, initial_capital: float = 1_000_000) -> None:
        """
        Initializes Portfolio object

        :param initial_capital: float - starting capital in dollars
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, float] = {}
        self.history = []

    def get_positions(self, ticker: str) -> float:
        """Get current position in shares"""
        return self.positions.get(ticker, 0)

    def update_positions(self, ticker: str, shares: float) -> None:
        """Update position (positive = long, negative = short)"""
        if shares == 0:
            if ticker in self.positions:
                del self.positions[ticker]
        else:
            self.positions[ticker] = shares

    def get_portfolio_value(self, prices: pd.Series) -> float:
        """
        Calculate total portfolio value

        :param prices: pd.Series - current prices for all tickers
        :return: float - total portfolio value
        """
        holdings_value = 0
        for ticker, shares in self.positions.items():
            if ticker in prices.index:
                holdings_value += shares * prices[ticker]

        return self.cash + holdings_value

    def record_snapshot(self, date, prices: pd.Series):
        """Record portfolio state"""
        total_value = self.get_portfolio_value(prices)

        snapshot = {
            'date': date,
            'total_value': total_value,
            'cash': self.cash,
            'num_positions': len(self.positions),
            'positions': self.positions.copy()
        }
        self.history.append(snapshot)

    def get_performance_df(self) -> pd.DataFrame:
        """Get performance history as a dataframe"""
        if not self.history:
            return pd.DataFrame()

        df = pd.DataFrame([
            {
                'date': h['date'],
                'total_value': h['total_value'],
                'cash': h['cash'],
                'num_positions': h['num_positions']
            }
            for h in self.history
        ])

        df.set_index('date', inplace=True)
        return df

    def calculate_returns(self) -> pd.Series:
        """Calculate return of portfolio"""
        df = self.get_performance_df()
        if len(df) == 0:
            return pd.Series()

        returns = df['total_value'].pct_change()
        return returns

    def get_summary_stats(self) -> Dict:
        """Calculate summary stats of portfolio"""
        df = self.get_performance_df()
        if len(df) == 0:
            return {}

        returns = self.calculate_returns().dropna()
        total_returns = (df['total_value'].iloc[-1] / self.initial_capital) - 1

        # Annualize metrics (assuming daily data)
        trading_days = len(returns)
        years = trading_days / 252

        cagr = (1 + total_returns) ** (1 / years) - 1 if years > 0 else 0

        # Volatility
        annual_vol = returns.std() * np.sqrt(252)

        # Sharp ratio (assuming 0% risk-free rate for simplicity)
        sharpe = (returns.mean() * 252) / annual_vol if annual_vol > 0 else 0

        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        return {
            'total_returns': total_returns,
            'cagr': cagr,
            'annual_volality': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'final_value': df['total_value'].iloc[-1],
            'num_trades': trading_days,
        }