import numpy as np
import pandas as pd


def calculate_daily_returns(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate daily percentage returns.
    """

    returns = prices.pct_change(fill_method=None)

    return returns.dropna(how="all")


def calculate_log_returns(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate logarithmic returns.
    """

    log_returns = np.log(prices / prices.shift(1))

    return log_returns.dropna(how="all")


def calculate_annualized_returns(
    daily_returns: pd.DataFrame,
    trading_days: int = 252,
) -> pd.Series:
    """
    Calculate annualized returns based on compounded daily returns.
    """

    number_of_days = len(daily_returns)

    if number_of_days == 0:
        return pd.Series(dtype=float)

    annualized_returns = (
        (1 + daily_returns).prod()
        ** (trading_days / number_of_days)
        - 1
    )

    return annualized_returns


def calculate_cagr(
    prices: pd.DataFrame,
) -> pd.Series:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    """

    if prices.empty:
        return pd.Series(dtype=float)

    years = (
        prices.index[-1] - prices.index[0]
    ).days / 365.25

    if years <= 0:
        return pd.Series(dtype=float)

    cagr = (
        prices.iloc[-1] / prices.iloc[0]
    ) ** (1 / years) - 1

    return cagr