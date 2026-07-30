import numpy as np
from scipy.optimize import minimize

from src.optimization.base import (
    PortfolioOptimizer,
)


def optimize_minimum_variance(
    optimizer: PortfolioOptimizer,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
):
    """
    Find portfolio with minimum volatility.

    Constraints:
        Sum of weights = 1

    Bounds:
        min_weight <= weight <= max_weight
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
        }
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
            f"Optimization failed: "
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