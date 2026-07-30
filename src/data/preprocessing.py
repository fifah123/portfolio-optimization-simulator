import pandas as pd


def clean_price_data(
    prices: pd.DataFrame,
    fill_method: str = "ffill",
) -> pd.DataFrame:
    """
    Clean historical price data.

    Parameters
    ----------
    prices : pd.DataFrame
        Historical price data.

    fill_method : str
        Missing value handling method.

    Returns
    -------
    pd.DataFrame
        Cleaned price data.
    """

    prices = prices.copy()

    # Remove duplicate dates
    prices = prices[~prices.index.duplicated(keep="first")]

    # Sort chronologically
    prices = prices.sort_index()

    # Replace infinite values
    prices = prices.replace([float("inf"), float("-inf")], pd.NA)

    if fill_method == "ffill":
        prices = prices.ffill()

    elif fill_method == "drop":
        prices = prices.dropna()

    else:
        raise ValueError(
            f"Unsupported fill_method: {fill_method}"
        )

    # Remove rows that are still completely empty
    prices = prices.dropna(how="all")

    return prices