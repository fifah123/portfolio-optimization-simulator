import numpy as np
import pandas as pd


def simulate_gbm_portfolio(
    initial_value: float,
    portfolio_return: float,
    portfolio_volatility: float,
    years: int = 5,
    simulations: int = 1000,
    trading_days: int = 252,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate future portfolio values using
    Geometric Brownian Motion.

    Parameters
    ----------
    initial_value : float
        Initial portfolio investment.

    portfolio_return : float
        Expected annualized portfolio return.

    portfolio_volatility : float
        Annualized portfolio volatility.

    years : int
        Simulation horizon in years.

    simulations : int
        Number of simulation paths.

    trading_days : int
        Number of trading days per year.

    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Simulated portfolio values.
    """

    np.random.seed(random_seed)

    n_days = (
        years
        * trading_days
    )

    dt = (
        1
        / trading_days
    )

    # Daily drift
    daily_drift = (

        portfolio_return

        - 0.5
        * portfolio_volatility**2
    ) * dt

    # Daily volatility
    daily_volatility = (

        portfolio_volatility

        * np.sqrt(dt)
    )

    # Random shocks
    random_shocks = np.random.normal(

        loc=0,

        scale=1,

        size=(
            n_days,
            simulations,
        ),
    )

    # Daily returns
    daily_returns = np.exp(

        daily_drift

        + daily_volatility
        * random_shocks
    )

    # Add initial value
    price_paths = np.vstack(

        [

            np.ones(
                simulations
            ),

            daily_returns,

        ]
    )

    # Cumulative growth
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