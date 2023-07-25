import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import coint, adfuller
from constants import *
import functools


class Statistics_Cointegration:
    def __init__(self, arr1: np.ndarray, arr2: np.ndarray) -> None:
        self.arr1 = arr1
        self.arr2 = arr2
        self.model = sm.OLS(self.arr1, self.arr2).fit()

    @functools.cache
    def calculate_hedge_ratio(self) -> float:
        return self.model.params[0]

    @property
    @functools.cache
    def hedge_ratio(self) -> float:
        return self.calculate_hedge_ratio()

    @functools.cache
    def calculate_spread(self) -> np.ndarray:
        return self.arr1 - self.hedge_ratio * self.arr2

    @property
    @functools.cache
    def spread(self) -> np.ndarray:
        return self.calculate_spread()

    def calculate_correlation(self) -> float:
        return np.corrcoef(self.arr1, self.arr2)[0, 1]

    def check_cointegration(self, threshold: float = 0.05) -> bool:
        _, pvalue, _ = coint(self.arr1, self.arr2)
        return pvalue < threshold

    def check_stationarity(self, threshold: float = 0.05) -> bool:
        adf_result = adfuller(self.spread)
        return adf_result[1] < threshold

    def calculate_half_life(self) -> float:
        if np.any(pd.isnull(self.spread)):
            spread_lag = pd.Series(self.spread).shift(
                1).fillna(method='bfill').values
        else:
            spread_lag = np.roll(self.spread, 1)
        spread_ret = self.spread - spread_lag
        spread_lag2 = sm.add_constant(spread_lag)
        model = sm.OLS(spread_ret, spread_lag2)
        res = model.fit()
        return -np.log(2) / res.params[1]

    def calculate_zscore(self) -> np.ndarray:
        return stats.zscore(self.spread)

    def calculate_zscore_rolling(self, window: int = 21) -> np.ndarray:
        spread_series = pd.Series(self.spread)
        mean = spread_series.rolling(window=window).mean()
        std = spread_series.rolling(window=window).std()
        zscore_rolling = (spread_series - mean) / std
        return zscore_rolling.values
