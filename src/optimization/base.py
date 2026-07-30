import numpy as np
import pandas as pd


class PortfolioOptimizer:
    """
    Base portfolio optimization class.

    Parameters
    ----------
    expected_returns : pd.Series
        Expected annualized returns for each asset.

    covariance_matrix : pd.DataFrame
        Annualized covariance matrix of asset returns.

    risk_free_rate : float
        Annualized risk-free rate.
    """

    def __init__(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        risk_free_rate: float = 0.04,
    ):

        self.expected_returns = expected_returns
        self.covariance_matrix = covariance_matrix
        self.risk_free_rate = risk_free_rate

        self.assets = expected_returns.index.tolist()
        self.n_assets = len(self.assets)

    def calculate_portfolio_return(
        self,
        weights: np.ndarray,
    ) -> float:
        """
        Calculate portfolio expected annual return.
        """

        return float(
            np.dot(
                weights,
                self.expected_returns.values,
            )
        )

    def calculate_portfolio_variance(
        self,
        weights: np.ndarray,
    ) -> float:
        """
        Calculate portfolio annualized variance.
        """

        return float(
            weights.T
            @ self.covariance_matrix.values
            @ weights
        )

    def calculate_portfolio_volatility(
        self,
        weights: np.ndarray,
    ) -> float:
        """
        Calculate portfolio annualized volatility.
        """

        variance = (
            self.calculate_portfolio_variance(
                weights
            )
        )

        return float(
            np.sqrt(variance)
        )

    def calculate_sharpe_ratio(
        self,
        weights: np.ndarray,
    ) -> float:
        """
        Calculate portfolio Sharpe Ratio.
        """

        portfolio_return = (
            self.calculate_portfolio_return(
                weights
            )
        )

        portfolio_volatility = (
            self.calculate_portfolio_volatility(
                weights
            )
        )

        if portfolio_volatility == 0:
            return 0.0

        return (
            portfolio_return
            - self.risk_free_rate
        ) / portfolio_volatility

    def calculate_metrics(
        self,
        weights: np.ndarray,
    ) -> dict:
        """
        Calculate complete portfolio metrics.
        """

        portfolio_return = (
            self.calculate_portfolio_return(
                weights
            )
        )

        portfolio_volatility = (
            self.calculate_portfolio_volatility(
                weights
            )
        )

        sharpe_ratio = (
            self.calculate_sharpe_ratio(
                weights
            )
        )

        return {
            "Expected Return": portfolio_return,
            "Volatility": portfolio_volatility,
            "Sharpe Ratio": sharpe_ratio,
        }

    def weights_to_series(
        self,
        weights: np.ndarray,
    ) -> pd.Series:
        """
        Convert weights array into pandas Series.
        """

        return pd.Series(
            weights,
            index=self.assets,
            name="Weight",
        )