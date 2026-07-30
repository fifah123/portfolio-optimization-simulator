import numpy as np
import pandas as pd


def calculate_portfolio_returns(
    asset_returns: pd.DataFrame,
    weights: pd.Series,
) -> pd.Series:
    """
    Calculate portfolio returns based on
    asset returns and portfolio weights.

    Parameters
    ----------
    asset_returns : pd.DataFrame
        Historical asset returns.

    weights : pd.Series
        Portfolio allocation weights.

    Returns
    -------
    pd.Series
        Portfolio returns.
    """

    # Make sure weights follow asset order
    weights = weights.reindex(
        asset_returns.columns
    )

    portfolio_returns = (
        asset_returns
        .mul(weights, axis=1)
        .sum(axis=1)
    )

    return portfolio_returns


def backtest_buy_and_hold(
    prices: pd.DataFrame,
    weights: pd.Series,
    initial_value: float = 100000.0,
) -> pd.DataFrame:
    """
    Backtest a buy-and-hold portfolio.

    Portfolio weights remain constant in terms
    of initial capital allocation, but no
    rebalancing occurs.

    Parameters
    ----------
    prices : pd.DataFrame
        Historical asset prices.

    weights : pd.Series
        Initial portfolio weights.

    initial_value : float
        Initial investment.

    Returns
    -------
    pd.DataFrame
        Backtest results.
    """

    weights = weights.reindex(
        prices.columns
    )

    normalized_prices = (
        prices
        / prices.iloc[0]
    )

    weighted_growth = (
        normalized_prices
        .mul(weights, axis=1)
        .sum(axis=1)
    )

    portfolio_value = (
        initial_value
        * weighted_growth
    )

    portfolio_returns = (
        portfolio_value
        .pct_change()
        .fillna(0)
    )

    results = pd.DataFrame(

        {
            "Portfolio_Value":
                portfolio_value,

            "Portfolio_Return":
                portfolio_returns,
        },

        index=prices.index,
    )

    return results


def backtest_rebalanced(
    prices: pd.DataFrame,
    weights: pd.Series,
    initial_value: float = 100000.0,
    rebalance_frequency: str = "M",
) -> pd.DataFrame:
    """
    Backtest a periodically rebalanced portfolio.

    Parameters
    ----------
    prices : pd.DataFrame
        Historical asset prices.

    weights : pd.Series
        Target portfolio weights.

    initial_value : float
        Initial portfolio value.

    rebalance_frequency : str
        Rebalancing frequency.

        Options:
        - D: Daily
        - W: Weekly
        - M: Monthly
        - Q: Quarterly
        - Y: Yearly

    Returns
    -------
    pd.DataFrame
        Backtest results.
    """

    weights = weights.reindex(
        prices.columns
    )

    daily_returns = (
        prices
        .pct_change()
        .fillna(0)
    )

    portfolio_values = []

    current_value = (
        initial_value
    )

    current_weights = (
        weights.copy()
    )

    # Identify rebalance dates
    rebalance_dates = (
        prices
        .resample(
            rebalance_frequency
        )
        .last()
        .index
    )

    for date in prices.index:

        daily_asset_returns = (
            daily_returns.loc[date]
        )

        # Portfolio daily return
        portfolio_return = (

            daily_asset_returns

            * current_weights

        ).sum()

        current_value *= (

            1
            + portfolio_return
        )

        portfolio_values.append(

            {
                "Date":
                    date,

                "Portfolio_Value":
                    current_value,

                "Portfolio_Return":
                    portfolio_return,
            }
        )

        # Rebalance
        if date in rebalance_dates:

            current_weights = (
                weights.copy()
            )

    results = pd.DataFrame(
        portfolio_values
    )

    results = (
        results
        .set_index("Date")
    )

    return results


def calculate_benchmark_value(
    benchmark_prices: pd.Series,
    initial_value: float = 100000.0,
) -> pd.Series:
    """
    Calculate benchmark portfolio value
    assuming buy-and-hold investment.
    """

    normalized_prices = (

        benchmark_prices

        / benchmark_prices.iloc[0]
    )

    benchmark_value = (

        initial_value

        * normalized_prices
    )

    return benchmark_value