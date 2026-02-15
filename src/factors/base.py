from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any

class BaseFactor(ABC):
    """Base class for all alpha factors"""

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the factor

        :param name: str - Factor name
        :param params: dict, optional - Factor parameters
        """

        self.name = name
        self.params = params or {}
        self._last_value = None

    @abstractmethod
    def calculate(self, price: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the factor values

        :param price: pd.DataFrame - Price data with date as index, ticker as column
        :return: pd.DataFrame - Factor values with same shape as prices
        """
        pass

    def normalize(self, values: pd.DataFrame, method: str = 'zscore') -> pd.DataFrame:
        """
        Normalize the factor values cross-sectionally (across stock each day)

        :param values: pd.DataFrame - Raw factor values
        :param method: str - 'zscore', 'rank' or 'demean'
        :return: pd.DataFrame - Normalized factor values
        """
        if method == 'zscore':
            # Z-score: (x - mean) / std for each date
            mean = values.mean(axis=1)
            std = values.std(axis=1)
            return values.sub(mean, axis=0).div(std, axis=0)
        elif method == 'rank':
            # Rank percentile for each date
            return values.rank(axis=1, pct=True)
        elif method == 'demean':
            # Subtract mean (market neutral)
            mean = values.mean(axis=1)
            return values.sub(mean, axis=0)
        else:
            raise ValueError(f"Unknown normalization method: {method}")

    def winsorize(self, values: pd.DataFrame, limits: tuple = (0.01, 0.99)) -> pd.DataFrame:
        """
        Winsorize extreme values to reduce impact of outliers

        :param values: pd.DataFrame - Factor values
        :param limits: tuple - (lower, percentile, upper percentile)
        :return: pd.DataFrame - Winsorized values
        """
        lower = values.quantile(limits[0], axis=1)
        upper = values.quantile(limits[1], axis=1)

        # Clip values
        result = values.clip(lower=lower, upper=upper, axis=0)

        return result

    def get_latest_values(self) -> Optional[pd.Series]:
        """Get most recent factor values"""
        return self._last_value

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}), params={self.params}"
