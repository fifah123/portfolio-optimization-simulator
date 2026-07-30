import pandas as pd


def format_asset_metrics(
    metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Format asset metrics for Streamlit display.
    """

    formatted = metrics.copy()

    percentage_columns = [
        "Annual Return",
        "CAGR",
        "Volatility",
        "Maximum Drawdown",
    ]

    for column in percentage_columns:

        if column in formatted.columns:
            formatted[column] = (
                formatted[column] * 100
            ).round(2).astype(str) + "%"

    if "Sharpe Ratio" in formatted.columns:
        formatted["Sharpe Ratio"] = (
            formatted["Sharpe Ratio"]
            .round(2)
        )

    return formatted