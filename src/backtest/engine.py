import pandas as pd
import numpy as np
from typing import Optional

from .portfolio import Portfolio

class BacktestEngine:
    """
    Simple backtest engine for factor-based strategies
    """

    def __init__(self,
                 initial_capital: float = 1_000_000,
                 commission_pct: float = 0.001,
                 rebalance_frequency: str = 'monthly'):
        """
        Initialise backtest engine

        :param initial_capital: float - initial capital
        :param commission_pct: float - commission as percentage of trade value
        :param rebalance_frequency: str - 'daily', 'weekly', 'monthly', 'quarterly'
        """
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.rebalance_frequency = rebalance_frequency
        self.portfolio = Portfolio(initial_capital=initial_capital)

    def run_long_short(self,
                       prices: pd.DataFrame,
                       factor_values: pd.DataFrame,
                       long_pct: float = 0.2,
                       short_pct: float = 0.2,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Portfolio:
        """
        Run long short backtest

        :param prices: pd.DataFrame - price data
        :param factor_values: pd.DataFrame - factor values
        :param long_pct: float - percentage of stock to long
        :param short_pct: float - percentage of stock to short
        :param start_date: str, optional - start date for backtest
        :param end_date: str, optional - end date for backtest
        :return: Portfolio - portfolio with trade history
        """
        # Filter dates
        if start_date:
            prices = prices[prices.index >= start_date]
            factor_values = factor_values[factor_values.index >= start_date]
        if end_date:
            prices = prices[prices.index <= end_date]
            factor_values = factor_values[factor_values.index <= end_date]

        # Determine rebalance dates
        rebalance_dates = self._get_rebalance_dates(prices.index)

        print(f"Running backtest for {prices.index[0].date()} to {prices.index[-1].date()}")
        print(f"Rebalancing {len(rebalance_dates)} times {self.rebalance_frequency}")

        # Run backtest
        for i, date in enumerate(prices.index):
            current_prices = prices.loc[date]

            # Rebalance on rebase dates
            if date in rebalance_dates:
                factor_date = factor_values.index[factor_values.index <= date][-1]
                current_factors = factor_values.loc[factor_date].dropna()

                self._rebalance_long_short(
                    current_prices,
                    current_factors,
                    long_pct,
                    short_pct
                )

                print(f"[{i}/{len(prices)}] Rebalance on {date.date()}: "
                      f"${self.portfolio.get_portfolio_value(current_prices):,.0f}")

            # Record daily snapshot
            self.portfolio.record_snapshot(date, current_prices)

        return self.portfolio

    def _get_rebalance_dates(self, dates: pd.DatetimeIndex) -> list:
        """Get rebalance dates based on frequency"""
        if self.rebalance_frequency == 'daily':
            return dates.tolist()

        elif self.rebalance_frequency == 'weekly':
            # First trading day of each week (Monday or first available)
            date_series = dates.to_series()
            week_changes = date_series.dt.isocalendar().week != date_series.dt.isocalendar().week.shift(1)
            return dates[week_changes].tolist()

        elif self.rebalance_frequency == 'monthly':
            # First trading day of each month
            date_series = dates.to_series()
            month_changes = date_series.dt.month != date_series.dt.month.shift(1)
            return dates[month_changes].tolist()

        elif self.rebalance_frequency == 'quarterly':
            # First trading day of each quarter
            date_series = dates.to_series()
            quarter_changes = date_series.dt.quarter != date_series.dt.quarter.shift(1)
            return dates[quarter_changes].tolist()

        else:
            raise ValueError(f"Unknown rebalance frequency: {self.rebalance_frequency}")

    def _rebalance_long_short(self,
                              prices: pd.Series,
                              factors: pd.Series,
                              long_pct: float,
                              short_pct: float):
        """Rebalance portfolio to target long/short positions"""

        # Get common stocks (have both price and factor)
        common_stocks = prices.index.intersection(factors.index)
        valid_prices = prices[common_stocks]
        valid_factors = factors[common_stocks]

        # Remove stocks with missing data
        valid_stocks = valid_prices[valid_prices > 0].index
        valid_factors = valid_factors[valid_stocks]
        valid_prices = valid_prices[valid_stocks]

        if len(valid_factors) < 10:
            print(f"Warning: only {len(valid_factors)} stocks available")
            return

        # Rank stocks by factor
        n_long = max(1, int(len(valid_factors) * long_pct))
        n_short = max(1, int(len(valid_factors) * short_pct))

        sorted_factors = valid_factors.sort_values(ascending=False)
        long_tickers = sorted_factors.head(n_long).index
        short_tickers = sorted_factors.tail(n_short).index

        # Calculate target portfolio value (split 50/50 between long and short)
        total_value = self.portfolio.get_portfolio_value(valid_prices)
        long_value = total_value * 0.5
        short_value = total_value * 0.5

        # Close existing positions not in new portfolio
        all_target_tickers = set(long_tickers) | set(short_tickers)
        for ticker in list(self.portfolio.positions.keys()):
            if ticker  not in all_target_tickers:
                self._close_position(ticker, prices[ticker])

        # Open/adjust long position
        for ticker in long_tickers:
            target_value = long_value / len(long_tickers)
            target_shares = target_value / valid_prices[ticker]
            current_shares = self.portfolio.get_positions(ticker)

            if abs(target_shares - current_shares) > 0.1:
                self._trade(ticker, target_shares - current_shares, valid_prices[ticker])

    def _trade(self, ticker: str, shares: float, price: float):
        """Execute a trade with commission"""
        trade_value = abs(shares * price)
        commission = self.commission_pct * trade_value

        self.portfolio.cash -= (shares * price + commission)
        current_shares = self.portfolio.get_positions(ticker)
        self.portfolio.update_positions(ticker, current_shares + shares)

    def _close_position(self, ticker: str, price: float):
        """Close an existing position"""
        shares = self.portfolio.get_positions(ticker)
        if shares != 0:
            self._trade(ticker, -shares, price)
