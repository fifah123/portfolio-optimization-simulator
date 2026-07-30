import pandas as pd


def calculate_correlation_matrix(
    daily_returns: pd.DataFrame,
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Calculate the correlation matrix of asset returns.

    Parameters
    ----------
    daily_returns : pd.DataFrame
        Daily returns for selected assets.

    method : str
        Correlation method:
        - pearson
        - spearman
        - kendall

    Returns
    -------
    pd.DataFrame
        Correlation matrix.
    """

    if daily_returns.empty:
        return pd.DataFrame()

    return daily_returns.corr(method=method)