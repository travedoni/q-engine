import pandas as pd
from ..base import BaseFactor

class PriceMomentum(BaseFactor):
    """
    Price momentum factor based on past returns

    Calculates momentum as percentage change over lookback period.
    Default uses 252-day (1-year) momentum, which has shown to be
    most predictive in our analysis.
    """

    def __init__(self, lookback_days: int = 252, skip_days: int = 20,
                 normalize_method: str = 'zscore', winsorize: bool = True):
        """
        Initialize price momentum factor

        :param lookback_days: int - number of days to lookback for
                momentum calculation. Default is 252
        :param skip_days: int - number of days to skip for (to
                avoid short-term reversal). Default is 20
        :param normalize_method: str - how to normalize:
                'zscore', 'rank', or 'demean'
        :param winsorize: bool - whether to winsorize extremes
        """
        params = {
            'lookback_days': lookback_days,
            'skip_days': skip_days,
            'normalize_method': normalize_method,
            'winsorize': winsorize
        }
        super().__init__(name=f'momentum_{lookback_days}d', params=params)

        self.lookback_days = lookback_days
        self.skip_days = skip_days
        self.normalize_method = normalize_method
        self.should_winsorize = winsorize

    def calculate(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate momentum factor

        :param prices: pd.DataFrame - adjusted close price with
                date as index, ticker as columns
        :return: pd.DataFrame - momentum values (percentage returns)
        """
        # Skip recent days to avoid short-term reversal
        if self.skip_days > 0:
            prices_lagged = prices.shift(self.skip_days)
        else:
            prices_lagged = prices

        # Calculate momentum: (Price_today / Price_N_days_ago) - 1
        momentum = prices_lagged.pct_change(periods=self.lookback_days)

        # Winsorize if requested
        if self.should_winsorize:
            momentum = self.winsorize(momentum, limits=(0.01, 0.99))

        # Normalize cross-sectionally
        momentum = self.normalize(momentum, method=self.normalize_method)

        # Store latest values
        self._last_value = momentum.iloc[-1]
        return momentum

    def get_top_bottom_stocks(self, prices: pd.DataFrame, top_n: int = 10,
                              bottom_n: int = 10) -> tuple:
        """
        Get top and bottom momentum stocks

        :param prices: pd.DataFrame - prices data
        :param top_n: int - number of top stocks to return
        :param bottom_n: int - number of bottom stocks to return
        :return: tuple - (top_stocks, bottom_stocks) as Series
                with tickers and momentum values
        """
        momentum = self.calculate(prices)
        latest = momentum.iloc[-1].dropna().sort_values(ascending=False)

        top_stocks = latest.head(top_n)
        bottom_stocks = latest.tail(bottom_n)

        return top_stocks, bottom_stocks

class ShortTermReversal(BaseFactor):
    """
    Short-term reversal factor (negative of short-term momentum)
    """

    def __init__(self, lookback_days: int = 20, normalize_method: str = 'zscore'):
        params = {
            'lookback_days': lookback_days,
            'normalize_method': normalize_method
        }
        super().__init__(name=f'reversal_{lookback_days}d', params=params)

        self.lookback_days = lookback_days
        self.normalize_method = normalize_method

    def calculate(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate reversal (negative momentum)"""

        # Calculate returns
        returns = prices.pct_change(periods=self.lookback_days)

        # Reversal is negative of returns (losers become winners)
        reversal = -returns

        # Normalize
        reversal = self.normalize(reversal, method=self.normalize_method)

        self._last_value = reversal.iloc[-1]

        return reversal