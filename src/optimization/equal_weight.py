import numpy as np

from src.optimization.base import (
    PortfolioOptimizer,
)


def optimize_equal_weight(
    optimizer: PortfolioOptimizer,
):
    """
    Allocate equal weights to all assets.
    """

    n_assets = optimizer.n_assets

    weights = np.ones(
        n_assets
    ) / n_assets

    metrics = optimizer.calculate_metrics(
        weights
    )

    return (
        optimizer.weights_to_series(
            weights
        ),
        metrics,
    )