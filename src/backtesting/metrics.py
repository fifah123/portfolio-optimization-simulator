import numpy as np
import pandas as pd


def calculate_cagr(
    portfolio_values: pd.Series,
) -> float:
    """
    Calculate Compound Annual Growth Rate.
    """

    start_value = (
        portfolio_values.iloc[0]
    )

    end_value = (
        portfolio_values.iloc[-1]
    )

    days = (

        portfolio_values.index[-1]

        - portfolio_values.index[0]
    ).days

    years = (
        days / 365.25
    )

    if years <= 0:

        return 0.0

    cagr = (

        end_value
        / start_value

    ) ** (

        1 / years

    ) - 1

    return cagr


def calculate_annualized_volatility(
    returns: pd.Series,
    trading_days: int = 252,
) -> float:
    """
    Calculate annualized volatility.
    """

    return (

        returns.std()

        * np.sqrt(
            trading_days
        )
    )


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    trading_days: int = 252,
) -> float:
    """
    Calculate annualized Sharpe ratio.
    """

    daily_rf = (

        (1 + risk_free_rate)

        ** (
            1 / trading_days
        )

        - 1
    )

    excess_returns = (

        returns

        - daily_rf
    )

    if excess_returns.std() == 0:

        return 0.0

    sharpe = (

        excess_returns.mean()

        / excess_returns.std()

    ) * np.sqrt(
        trading_days
    )

    return sharpe


def calculate_max_drawdown(
    portfolio_values: pd.Series,
) -> float:
    """
    Calculate maximum drawdown.
    """

    rolling_max = (

        portfolio_values

        .cummax()
    )

    drawdown = (

        portfolio_values

        / rolling_max

        - 1
    )

    return drawdown.min()


def calculate_calmar_ratio(
    cagr: float,
    max_drawdown: float,
) -> float:
    """
    Calculate Calmar ratio.
    """

    if max_drawdown == 0:

        return 0.0

    return (

        cagr

        / abs(
            max_drawdown
        )
    )


def calculate_performance_metrics(
    portfolio_values: pd.Series,
    portfolio_returns: pd.Series,
    risk_free_rate: float = 0.0,
    trading_days: int = 252,
) -> dict:
    """
    Calculate complete portfolio performance metrics.
    """

    cagr = calculate_cagr(

        portfolio_values
    )

    volatility = (
        calculate_annualized_volatility(

            portfolio_returns,

            trading_days,
        )
    )

    sharpe = (
        calculate_sharpe_ratio(

            portfolio_returns,

            risk_free_rate,

            trading_days,
        )
    )

    max_drawdown = (
        calculate_max_drawdown(

            portfolio_values
        )
    )

    calmar = (
        calculate_calmar_ratio(

            cagr,

            max_drawdown,
        )
    )

    total_return = (

        portfolio_values.iloc[-1]

        / portfolio_values.iloc[0]

        - 1
    )

    positive_days = (

        portfolio_returns

        > 0
    ).mean()

    negative_days = (

        portfolio_returns

        < 0
    ).mean()

    metrics = {

        "Initial Value":
            portfolio_values.iloc[0],

        "Final Value":
            portfolio_values.iloc[-1],

        "Total Return":
            total_return,

        "CAGR":
            cagr,

        "Annualized Volatility":
            volatility,

        "Sharpe Ratio":
            sharpe,

        "Maximum Drawdown":
            max_drawdown,

        "Calmar Ratio":
            calmar,

        "Positive Days":
            positive_days,

        "Negative Days":
            negative_days,
    }

    return metrics


def calculate_drawdown_series(
    portfolio_values: pd.Series,
) -> pd.Series:
    """
    Calculate historical drawdown series.
    """

    rolling_max = (

        portfolio_values

        .cummax()
    )

    drawdown = (

        portfolio_values

        / rolling_max

        - 1
    )

    return drawdown


def calculate_rolling_metrics(
    returns: pd.Series,
    window: int = 252,
    trading_days: int = 252,
) -> pd.DataFrame:
    """
    Calculate rolling volatility and Sharpe ratio.
    """

    rolling_return = (

        returns

        .rolling(window)

        .mean()
    )

    rolling_volatility = (

        returns

        .rolling(window)

        .std()

        * np.sqrt(
            trading_days
        )
    )

    rolling_sharpe = (

        rolling_return

        / returns
        .rolling(window)
        .std()

    ) * np.sqrt(
        trading_days
    )

    return pd.DataFrame(

        {

            "Rolling_Volatility":
                rolling_volatility,

            "Rolling_Sharpe":
                rolling_sharpe,

        },

        index=returns.index,
    )