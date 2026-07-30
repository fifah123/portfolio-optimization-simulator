import numpy as np
import pandas as pd


SCENARIOS = {

    "Bear": {

        "return_adjustment":
            -0.05,

        "volatility_multiplier":
            1.30,
    },

    "Base": {

        "return_adjustment":
            0.00,

        "volatility_multiplier":
            1.00,
    },

    "Bull": {

        "return_adjustment":
            0.05,

        "volatility_multiplier":
            0.80,
    },
}


def simulate_scenario(
    initial_value: float,
    portfolio_return: float,
    portfolio_volatility: float,
    scenario: str,
    years: int = 5,
    simulations: int = 1000,
    trading_days: int = 252,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate portfolio under Bull, Base,
    or Bear scenarios.
    """

    if scenario not in SCENARIOS:

        raise ValueError(

            f"Unknown scenario: {scenario}"
        )

    config = SCENARIOS[
        scenario
    ]

    adjusted_return = (

        portfolio_return

        + config[
            "return_adjustment"
        ]
    )

    adjusted_volatility = (

        portfolio_volatility

        * config[
            "volatility_multiplier"
        ]
    )

    from src.simulation.monte_carlo import (

        simulate_gbm_portfolio
    )

    return simulate_gbm_portfolio(

        initial_value=
            initial_value,

        portfolio_return=
            adjusted_return,

        portfolio_volatility=
            adjusted_volatility,

        years=
            years,

        simulations=
            simulations,

        trading_days=
            trading_days,

        random_seed=
            random_seed,
    )