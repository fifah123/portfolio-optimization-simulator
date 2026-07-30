import numpy as np
import pandas as pd


def generate_random_portfolios(
    optimizer,
    n_portfolios: int = 10000,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate random portfolios and calculate
    expected return, volatility, and Sharpe ratio.

    Parameters
    ----------
    optimizer :
        PortfolioOptimizer instance.

    n_portfolios : int
        Number of random portfolios.

    min_weight : float
        Minimum allocation per asset.

    max_weight : float
        Maximum allocation per asset.

    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Random portfolio statistics.
    """

    np.random.seed(
        random_seed
    )

    results = []

    n_assets = (
        optimizer.n_assets
    )

    for _ in range(
        n_portfolios
    ):

        weights = np.random.random(
            n_assets
        )

        weights = (
            weights
            / weights.sum()
        )

        # Check allocation constraints

        if np.any(
            weights < min_weight
        ):
            continue

        if np.any(
            weights > max_weight
        ):
            continue

        metrics = (
            optimizer.calculate_metrics(
                weights
            )
        )

        results.append(
            {
                "Return":
                    metrics[
                        "Expected Return"
                    ],

                "Volatility":
                    metrics[
                        "Volatility"
                    ],

                "Sharpe Ratio":
                    metrics[
                        "Sharpe Ratio"
                    ],
            }
        )

    return pd.DataFrame(
        results
    )


def calculate_efficient_frontier(
    optimizer,
    target_returns: np.ndarray,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
):
    """
    Calculate minimum volatility portfolio
    for each target return.
    """

    from scipy.optimize import minimize

    frontier_results = []

    n_assets = (
        optimizer.n_assets
    )

    initial_weights = (
        np.ones(
            n_assets
        )
        / n_assets
    )

    bounds = [
        (
            min_weight,
            max_weight,
        )
        for _ in range(
            n_assets
        )
    ]

    for target_return in target_returns:

        constraints = [

            {
                "type": "eq",

                "fun":
                    lambda weights:
                    np.sum(
                        weights
                    ) - 1,
            },

            {
                "type": "eq",

                "fun":
                    lambda weights,
                    target=target_return:

                    optimizer.calculate_portfolio_return(
                        weights
                    )
                    - target,
            },
        ]

        result = minimize(

            fun=
                lambda weights:

                optimizer.calculate_portfolio_variance(
                    weights
                ),

            x0=
                initial_weights,

            method="SLSQP",

            bounds=
                bounds,

            constraints=
                constraints,
        )

        if result.success:

            weights = result.x

            metrics = (
                optimizer.calculate_metrics(
                    weights
                )
            )

            frontier_results.append(
                {
                    "Return":
                        metrics[
                            "Expected Return"
                        ],

                    "Volatility":
                        metrics[
                            "Volatility"
                        ],

                    "Sharpe Ratio":
                        metrics[
                            "Sharpe Ratio"
                        ],
                }
            )

    return pd.DataFrame(
        frontier_results
    )