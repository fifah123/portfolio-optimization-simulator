import numpy as np
import pandas as pd


def simulate_historical_bootstrap(
    initial_value: float,
    portfolio_returns: pd.Series,
    years: int = 5,
    simulations: int = 1000,
    trading_days: int = 252,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate future portfolio values by randomly
    resampling historical portfolio returns.

    Parameters
    ----------
    initial_value : float
        Initial investment.

    portfolio_returns : pd.Series
        Historical portfolio daily returns.

    years : int
        Simulation horizon.

    simulations : int
        Number of simulation paths.

    trading_days : int
        Trading days per year.

    random_seed : int
        Random seed.

    Returns
    -------
    pd.DataFrame
        Simulated portfolio values.
    """

    np.random.seed(
        random_seed
    )

    historical_returns = (

        portfolio_returns

        .dropna()

        .values
    )

    n_days = (

        years

        * trading_days
    )

    # Randomly sample historical returns
    sampled_returns = np.random.choice(

        historical_returns,

        size=(

            n_days,

            simulations,
        ),

        replace=True,
    )

    # Convert returns to growth factors
    growth_factors = (

        1

        + sampled_returns
    )

    # Add initial investment
    price_paths = np.vstack(

        [

            np.ones(
                simulations
            ),

            growth_factors,

        ]
    )

    # Calculate cumulative growth
    cumulative_paths = np.cumprod(

        price_paths,

        axis=0,
    )

    portfolio_paths = (

        initial_value

        * cumulative_paths
    )

    dates = pd.date_range(

        start=pd.Timestamp.today(),

        periods=
            n_days + 1,

        freq="B",
    )

    return pd.DataFrame(

        portfolio_paths,

        index=dates,

        columns=[

            f"Simulation_{i+1}"

            for i in range(
                simulations
            )

        ],
    )