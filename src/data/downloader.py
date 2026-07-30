from typing import List

import pandas as pd
import yfinance as yf


def download_price_data(
    tickers: List[str],
    start_date: str,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Download historical price data for selected assets.

    Parameters
    ----------
    tickers : list[str]
        List of ticker symbols.

    start_date : str
        Start date in YYYY-MM-DD format.

    end_date : str | None
        End date in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        Historical closing prices.
    """

    if not tickers:
        raise ValueError("At least one ticker must be provided.")

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        raise ValueError(
            "No data was downloaded. "
            "Please check the ticker symbols and date range."
        )

    # yfinance returns MultiIndex columns when multiple tickers are requested.
    if isinstance(data.columns, pd.MultiIndex):

        if "Close" in data.columns.get_level_values(0):
            prices = data["Close"]
        else:
            raise ValueError("Close price data is not available.")

    else:
        # Single ticker case
        prices = data[["Close"]]

        if len(tickers) == 1:
            prices.columns = tickers

    prices = prices.sort_index()

    return prices