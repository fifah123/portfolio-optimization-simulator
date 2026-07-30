import numpy as np
from scipy.optimize import minimize

from src.optimization.base import (
    PortfolioOptimizer,
)


def optimize_target_return(
    optimizer: PortfolioOptimizer,
    target_return: float,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
):
    """
    Find minimum-risk portfolio that achieves
    the target annual return.

    Parameters
    ----------
    optimizer : PortfolioOptimizer

    target_return : float
        Target annualized return.

    min_weight : float
        Minimum allocation per asset.

    max_weight : float
        Maximum allocation per asset.
    """

    n_assets = optimizer.n_assets

    initial_weights = (
        np.ones(n_assets)
        / n_assets
    )

    constraints = [
        {
            "type": "eq",
            "fun": lambda weights:
                np.sum(weights) - 1,
        },
        {
            "type": "ineq",
            "fun": lambda weights:
                optimizer.calculate_portfolio_return(
                    weights
                ) - target_return,
        },
    ]

    bounds = [
        (
            min_weight,
            max_weight,
        )
        for _ in range(n_assets)
    ]

    result = minimize(
        fun=lambda weights:
            optimizer.calculate_portfolio_variance(
                weights
            ),
        x0=initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        raise ValueError(
            f"Target return optimization failed: "
            f"{result.message}"
        )

    weights = result.x

    metrics = optimizer.calculate_metrics(
        weights
    )

    return (
        optimizer.weights_to_series(
            weights
        ),
        metrics,
    )