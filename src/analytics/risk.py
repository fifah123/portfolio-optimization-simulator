import numpy as np
import pandas as pd


def calculate_annualized_volatility(
    daily_returns: pd.DataFrame,
    trading_days: int = 252,
) -> pd.Series:
    """
    Calculate annualized volatility.
    """

    return daily_returns.std() * np.sqrt(trading_days)


def calculate_sharpe_ratio(
    annualized_returns: pd.Series,
    annualized_volatility: pd.Series,
    risk_free_rate: float = 0.04,
) -> pd.Series:
    """
    Calculate annualized Sharpe Ratio.

    Sharpe Ratio =
    (Annualized Return - Risk Free Rate)
    / Annualized Volatility
    """

    if annualized_volatility.empty:
        return pd.Series(dtype=float)

    sharpe = (
        annualized_returns - risk_free_rate
    ) / annualized_volatility

    return sharpe


def calculate_max_drawdown(
    prices: pd.DataFrame,
) -> pd.Series:
    """
    Calculate maximum drawdown for each asset.
    """

    cumulative_max = prices.cummax()

    drawdown = (
        prices - cumulative_max
    ) / cumulative_max

    return drawdown.min()


def calculate_downside_deviation(
    daily_returns: pd.DataFrame,
    target_return: float = 0.0,
    trading_days: int = 252,
) -> pd.Series:
    """
    Calculate annualized downside deviation.

    Only negative returns below the target return
    are considered.
    """

    downside_returns = daily_returns[
        daily_returns < target_return
    ]

    downside_deviation = (
        downside_returns
        .fillna(0)
        .pow(2)
        .mean()
        .pow(0.5)
        * np.sqrt(trading_days)
    )

    return downside_deviation


def calculate_sortino_ratio(
    annualized_returns: pd.Series,
    downside_deviation: pd.Series,
    risk_free_rate: float = 0.04,
) -> pd.Series:
    """
    Calculate Sortino Ratio.

    Sortino Ratio =
    (Annualized Return - Risk Free Rate)
    / Downside Deviation
    """

    sortino = (
        annualized_returns - risk_free_rate
    ) / downside_deviation

    return sortino


def calculate_rolling_volatility(
    daily_returns: pd.DataFrame,
    window: int = 30,
    trading_days: int = 252,
) -> pd.DataFrame:
    """
    Calculate rolling annualized volatility.
    """

    rolling_volatility = (
        daily_returns
        .rolling(window=window)
        .std()
        * np.sqrt(trading_days)
    )

    return rolling_volatility


def calculate_rolling_returns(
    daily_returns: pd.DataFrame,
    window: int = 30,
) -> pd.DataFrame:
    """
    Calculate rolling annualized returns.
    """

    rolling_returns = (
        daily_returns
        .rolling(window=window)
        .mean()
        * 252
    )

    return rolling_returns


def calculate_drawdown_series(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the full drawdown time series.
    """

    cumulative_max = prices.cummax()

    drawdown = (
        prices - cumulative_max
    ) / cumulative_max

    return drawdown